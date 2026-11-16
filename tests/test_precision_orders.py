"""Precision windups use real reservations, attack calculations and AP."""

from unittest.mock import patch

import pytest

from game.character import Character
from game.combat import CombatEngine, CombatState
from game.combat.attack_resolution import build_attack_context, resolve_attack
from game.combat.battlefield import HazardZone
from game.combat_system import run_enemy_ai
from game.cover_system import CoverNode
from game.stats import EnemyStats
from game.unit import Unit


def battle(theme="novatek_hybrid", subtype="elite"):
    character = Character("Rook")
    character.stats.hp = character.stats.max_hp = 100
    ally = Unit(position=(160, 64), stats=character.stats, character=character, health=100)
    enemy = Unit(position=(32, 64), health=50, stats=EnemyStats(agi=8),
                 unit_type="enemy", enemy_theme=theme, enemy_subtype=subtype, attack_range=6)
    engine = CombatEngine(CombatState(None, [ally], [enemy]), cover_nodes=[])
    engine.start_player_turn()
    return engine, ally, enemy


@pytest.mark.parametrize("theme", ["novatek_hybrid", "corp_samurai_robot", "corp_37_robot"])
def test_real_rosters_execute_one_two_ap_precision_shot_and_log_it(theme):
    engine, ally, enemy = battle(theme)
    assert engine.enemy_intents()[0].action == "LOCK"
    assert engine.enemy_intents()[0].destination == ally.position
    context = build_attack_context(enemy, ally, "precision")
    with patch("game.combat.attack_resolution.random.random", side_effect=[0.0, 1.0]):
        engine.start_enemy_turn()
    assert ally.health == 100 - context.normal_damage
    assert enemy.action_points == 0 and enemy.control_cooldown == 2
    assert sum("PRECISION_LOCK" in text for text in engine.state.logs) == 1


def test_preview_and_shared_resolver_include_cost_cover_and_critical_threshold():
    _, ally, enemy = battle()
    normal = build_attack_context(enemy, ally, "fire")
    precise = build_attack_context(enemy, ally, "precision")
    assert precise.attack_kind == "fire" and precise.ap_cost == 2
    assert precise.attack_value == normal.attack_value + 2
    assert precise.normal_damage == normal.normal_damage + 2
    assert precise.hit_chance > normal.hit_chance
    assert precise.crit_chance == 0.30
    covered = build_attack_context(enemy, ally, "precision", cover_nodes=[CoverNode(4, 2, "low")])
    assert covered.cover_bonus > 0 and covered.hit_chance < precise.hit_chance
    for critical_roll, expected in [(0.29999, True), (0.30, False)]:
        enemy.reset_actions()
        rolls = iter([0.0, critical_roll])
        result = resolve_attack(enemy, ally, "precision", rng=lambda: next(rolls))
        assert result.critical is expected and result.consumed_ap == 2
        assert result.damage == (precise.critical_damage if expected else precise.normal_damage)
        assert not result.infection_transmitted
    enemy.action_points = 1
    assert resolve_attack(enemy, ally, "precision").reason == "insufficient_ap"
    assert enemy.action_points == 1


def test_target_movement_breaks_lock_once_and_allows_only_one_ordinary_action():
    engine, ally, enemy = battle()
    assert engine.perform_action("move", actor=ally, move_delta=(0, 32)).success
    assert engine.enemy_intents()[0].action == "HUNT"
    order = engine.enemy_orders.orders[id(enemy)]
    assert order.ap_penalty == 1
    for _ in range(3):
        engine.enemy_intents()
    assert order.ap_penalty == 1
    with patch("game.combat_system.resolve_attack", wraps=resolve_attack) as attacks:
        engine.start_enemy_turn()
    assert attacks.call_count == 1 and attacks.call_args.args[2] == "fire"
    assert enemy.action_points == 0 and order.ap_penalty == 0
    assert enemy.control_cooldown == 0
    assert sum("lock_broken" in text for text in engine.state.logs) == 1


def test_sight_break_and_reopening_does_not_rearm_windup():
    engine, _, enemy = battle()
    engine.cover_nodes.append(CoverNode(3, 2, "high", passable=False))
    assert engine.enemy_intents()[0].action == "HUNT"
    engine.cover_nodes.clear()
    assert engine.enemy_intents()[0].action == "HUNT"
    with patch("game.combat_system.resolve_attack", wraps=resolve_attack) as attacks:
        engine.start_enemy_turn()
    assert attacks.call_count == 1 and attacks.call_args.args[2] == "fire"
    assert enemy.action_points == 0


def test_energy_loss_suppression_and_miss_never_grant_a_free_shot():
    engine, _, enemy = battle()
    engine.state.tactical_flags["hazards"] = [HazardZone("blackout", enemy.position, 0)]
    with patch("game.combat_system.resolve_attack") as attacks:
        engine.start_enemy_turn()
    attacks.assert_not_called()
    assert enemy.action_points == 0
    assert any("energy_lost" in text for text in engine.state.logs)
    engine, _, enemy = battle()
    enemy.apply_status("suppressed")
    with patch("game.combat_system.resolve_attack") as attacks:
        engine.start_enemy_turn()
    attacks.assert_not_called()
    engine, _, enemy = battle()
    with patch("game.combat.attack_resolution.random.random", return_value=1.0):
        engine.start_enemy_turn()
    assert enemy.action_points == 0 and enemy.control_cooldown == 2
    assert any("PRECISION_MISSED" in text for text in engine.state.logs)


def test_execution_rechecks_lost_target_even_without_hud_reconciliation():
    engine, ally, enemy = battle()
    ally.health = 0
    enemy.reset_actions()
    run_enemy_ai([ally], [enemy], reserved_orders=engine.enemy_orders.orders,
                 on_plan_interrupted=engine.interrupt_enemy_plan)
    assert engine.enemy_orders.orders[id(enemy)].intent.action != "LOCK"
    assert any("target_lost" in text for text in engine.state.logs)


def test_linked_robot_specialist_keeps_shared_target_and_loses_aim_when_leader_dies():
    engine, ally, enemy = battle("corp_samurai_robot")
    commander = Unit(position=(32, 96), health=50, stats=EnemyStats(),
                     unit_type="enemy", enemy_theme="corp_samurai_robot", enemy_subtype="commander", attack_range=6)
    engine.state.enemy_units.append(commander)
    engine.enemy_orders.reserve([enemy, commander], [ally], None, [], refresh=True)
    intent = engine.enemy_intents()[0]
    assert intent.action == "LOCK" and intent.target is ally and intent.coordinator is commander
    commander.health = 0  # Earlier overwatch or another activation may kill the leader.
    enemy.reset_actions()
    with patch("game.combat_system.resolve_attack", wraps=resolve_attack) as attacks:
        run_enemy_ai([ally], [enemy, commander], reserved_orders=engine.enemy_orders.orders,
                     on_plan_interrupted=engine.interrupt_enemy_plan)
    assert attacks.call_count == 1 and attacks.call_args.args[2] == "fire"
    assert any("command_lost" in text for text in engine.state.logs)


def test_robot_heavy_retains_suppression_under_a_precision_commander():
    engine, ally, commander = battle("corp_37_robot", "commander")
    heavy = Unit(position=(32, 96), health=50, stats=EnemyStats(), attack_range=6,
                 unit_type="enemy", enemy_theme="corp_37_robot", enemy_subtype="heavy")
    engine.state.enemy_units.append(heavy)
    engine.enemy_orders.reserve([heavy, commander], [ally], None, [], refresh=True)
    assert engine.enemy_orders.orders[id(heavy)].intent.action == "SUPPRESS"
    with patch("game.combat.attack_resolution.random.random", return_value=0.0):
        engine.start_enemy_turn()
    assert heavy.action_points == 0 and "suppressed" in ally.status_effects


def test_cooldown_requires_two_ordinary_activations_and_non_specialists_keep_their_role():
    for theme, subtype in [("corp_samurai", "elite"), ("corp_37_power_armor", "elite"), ("novatek_hybrid", "heavy")]:
        engine, _, _ = battle(theme, subtype)
        assert engine.enemy_intents()[0].action != "LOCK"
    engine, _, enemy = battle()
    engine.start_enemy_turn()
    for cooldown in (1, 0):
        engine.start_player_turn()
        assert engine.enemy_intents()[0].action != "LOCK"
        with patch("game.combat.engine.run_enemy_ai", return_value=[]):
            engine.start_enemy_turn()
        assert enemy.control_cooldown == cooldown
    engine.start_player_turn()
    assert engine.enemy_intents()[0].action == "LOCK"
