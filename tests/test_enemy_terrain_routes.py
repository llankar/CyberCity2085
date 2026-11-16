"""All doctrines must pay for legal detours rather than hit or enter a wall."""

from unittest.mock import patch

import pytest

from game.combat import CombatEngine, CombatState
from game.combat.encounter_qa import simulate_encounter
from game.cover_system import CoverNode
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


@pytest.mark.parametrize("theme", ["generic", "starver", "mutant", "raider", "corp_samurai", "corp_37_robot", "novatek_hybrid"])
def test_enemy_can_take_a_temporary_step_away_to_get_around_a_real_barrier(theme):
    ally = Unit(position=(384, 192), health=100, stats=PlayerStats(level=8))
    enemy = Unit(position=(64, 192), health=50, stats=EnemyStats(level=4),
                 unit_type="enemy", enemy_theme=theme, attack_range=1)
    wall = {(96, y) for y in range(128, 257, 32)}
    nodes = [CoverNode(x//32, y//32, "high", False) for x, y in wall]
    engine = CombatEngine(CombatState(None, [ally], [enemy]), cover_nodes=nodes,
                          can_enter=lambda x, y: 0 <= x < 512 and 0 <= y < 384 and (x, y) not in wall)
    visited = []
    original_move = enemy.move
    def record_move(dx, dy):
        assert abs(dx) + abs(dy) == 32
        original_move(dx, dy)
        visited.append(enemy.position)
        assert enemy.position not in wall
    with patch.object(enemy, "move", side_effect=record_move):
        for _ in range(5):
            engine.start_player_turn()
            engine.start_enemy_turn()
            assert enemy.action_points == 0
    assert visited and max(x for x, y in visited) > 96
    assert any(y < 128 or y > 256 for x, y in visited)


def test_cover_only_blocker_is_respected_even_without_a_terrain_callback():
    ally = Unit(position=(256, 64), health=50, stats=PlayerStats(level=5))
    enemy = Unit(position=(64, 64), health=50, stats=EnemyStats(), unit_type="enemy", attack_range=1)
    nodes = [CoverNode(3, 2, "high", False)]
    engine = CombatEngine(CombatState(None, [ally], [enemy]), cover_nodes=nodes)
    visited = []
    original_move = enemy.move
    def record_move(dx, dy):
        original_move(dx, dy)
        visited.append(enemy.position)
    with patch.object(enemy, "move", side_effect=record_move):
        engine.start_player_turn()
        engine.start_enemy_turn()
    assert (96, 64) not in visited
    assert visited


def test_seeking_diagonal_cover_cannot_buy_two_cardinal_cells_for_one_ap():
    ally = Unit(position=(512, 512), health=50, stats=PlayerStats(level=5))
    enemy = Unit(position=(64, 64), health=50, stats=EnemyStats(), unit_type="enemy", attack_range=1)
    engine = CombatEngine(CombatState(None, [ally], [enemy]), cover_nodes=[CoverNode(3, 3, "low")])
    with patch.object(enemy, "move", wraps=enemy.move) as moves:
        engine.start_player_turn()
        engine.start_enemy_turn()
    assert moves.call_count > 0
    assert all(abs(call.args[0]) + abs(call.args[1]) == 32 for call in moves.call_args_list)


def test_reaching_cover_uses_remaining_ap_to_guard_instead_of_undoing_the_move():
    ally = Unit(position=(512, 64), health=50, stats=PlayerStats(level=5))
    enemy = Unit(position=(32, 64), health=50, stats=EnemyStats(), unit_type="enemy", attack_range=1)
    engine = CombatEngine(CombatState(None, [ally], [enemy]), cover_nodes=[CoverNode(3, 2, "high", False)])
    engine.start_player_turn()
    engine.start_enemy_turn()
    assert enemy.position == (64, 64) and enemy.is_defending and enemy.action_points == 0
    engine.start_player_turn()
    assert enemy.in_cover_bonus == 2
    assert engine.enemy_intents()[0].action != "COVER"
    engine.start_enemy_turn()
    assert enemy.position != (64, 64)


def test_unreachable_target_reorientation_is_deferred_and_announced_before_execution():
    wounded = Unit(position=(320, 64), health=1, stats=PlayerStats(level=5))
    reachable = Unit(position=(64, 64), health=50, stats=PlayerStats(level=5))
    enemy = Unit(position=(32, 64), health=50, stats=EnemyStats(), unit_type="enemy", attack_range=1)
    engine = CombatEngine(CombatState(None, [wounded, reachable], [enemy]),
                          can_enter=lambda x, y: 0 <= x < 192 and 0 <= y < 192)
    engine.start_player_turn()
    assert engine.enemy_intents()[0].target is wounded
    with patch("game.combat_system.resolve_attack") as attack:
        engine.start_enemy_turn()
    attack.assert_not_called()
    assert engine.enemy_intents()[0].action == "HOLD"
    engine.start_player_turn()
    shown = engine.enemy_intents()[0]
    assert shown.target is reachable and "REORIENTED" in shown.rationale
    assert engine.enemy_intents()[0] is shown


@pytest.mark.parametrize("filename", ["city_industrial_dockside_terminal.png", "cybercity_inner_02_safehouse.png"])
def test_real_map_battle_uses_authored_terrain_and_checks_every_resolved_phase(filename):
    result = simulate_encounter(theme="corp_37_robot", level=4, risk=5, count=6, seed=0,
                                policy="objective_counterplay", map_path="assets/maps/"+filename, max_turns=4)
    assert result["map_file"] == filename
    assert result["terrain_source"] == "manual_wall_traces_v1"
    assert result["geometry_checked"]
    assert result["outcome"] in {"turn_limit", "victory", "defeat"}


def test_authored_assassination_targets_highest_rank_like_the_battle_view():
    result = simulate_encounter(theme="corp_37_robot", level=4, risk=5, count=6, seed=0,
                                policy="objective_counterplay", map_path="assets/maps/cybercity_inner_02_safehouse.png",
                                objective_kind="assassination", max_turns=4)
    assert result["roles"]["heavy"] and result["roles"]["elite"]
    assert result["assassination_target_role"] == "elite"
