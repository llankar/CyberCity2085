"""Real engine windups, dodging, interrupts and bounded zone lifetime."""

from unittest.mock import patch

from game.character import Character
from game.combat import CombatEngine, CombatState
from game.combat.battlefield import HazardZone
from game.cover_system import CoverNode
from game.stats import EnemyStats
from game.unit import Unit


def battle(subtype="heavy", theme="mutant"):
    character = Character("Rook")
    character.stats.hp = character.stats.max_hp = 50
    ally = Unit(position=(96, 64), health=50, stats=character.stats, character=character)
    enemy = Unit(position=(32, 64), health=50, stats=EnemyStats(hp=50, max_hp=50),
                 unit_type="enemy", enemy_theme=theme, enemy_subtype=subtype)
    engine = CombatEngine(CombatState(None, [ally], [enemy]), cover_nodes=[])
    engine.start_player_turn()
    return engine, ally, enemy


def test_real_projection_marks_a_fixed_tile_and_dodge_does_not_retarget():
    engine, ally, enemy = battle()
    intent = engine.enemy_intents()[0]
    assert intent.action == "TOXIN" and intent.target is None
    assert intent.destination == (96, 64)
    assert engine.perform_action("move", actor=ally, move_delta=(0, 32)).success
    assert engine.enemy_intents()[0] is intent
    with patch("game.combat_system.resolve_attack") as attack:
        engine.start_enemy_turn()
    attack.assert_not_called()
    assert enemy.action_points == 0 and enemy.control_cooldown == 2
    assert len(engine.state.tactical_flags["hazards"]) == 1
    zone = engine.state.tactical_flags["hazards"][0]
    assert zone.position == (96, 64) and zone.radius_cells == 0
    engine.start_player_turn()
    assert ally.health == 50 and ally.action_points == 2


def test_remaining_on_mark_costs_one_hp_and_ap_without_a_disease():
    engine, ally, _ = battle()
    engine.start_enemy_turn()
    engine.start_player_turn()
    assert ally.health == ally.stats.hp == 49
    assert ally.action_points == 1
    assert not ally.status_effects
    assert any("SLUDGE -1 HP / -1 AP" in text for text in engine.state.logs)


def test_cutting_sight_spoils_the_whole_activation_and_does_not_rearm_on_redraw():
    engine, _, enemy = battle()
    ally = engine.state.allied_units[0]
    ally.position = (160, 64)
    engine.enemy_orders.reserve([enemy], [ally], None, [], refresh=True)
    engine.cover_nodes.append(CoverNode(3, 2, "high", passable=False))
    assert engine.enemy_intents()[0].action == "HOLD"
    engine.cover_nodes.clear()
    for _ in range(3):
        assert engine.enemy_intents()[0].action == "HOLD"
    engine.start_enemy_turn()
    assert enemy.action_points == 0
    assert not engine.state.tactical_flags["hazards"]
    assert sum("cast_blocked" in text for text in engine.state.logs) == 1


def test_stun_and_phase_energy_loss_cannot_release_a_free_projection():
    engine, _, enemy = battle()
    enemy.apply_status("stunned")
    engine.start_enemy_turn()
    assert not engine.state.tactical_flags["hazards"]
    engine, _, enemy = battle()
    engine.state.tactical_flags["hazards"] = [HazardZone("blackout", enemy.position, 0)]
    engine.start_enemy_turn()
    assert enemy.action_points == 0
    assert not any(zone.kind == "sludge" for zone in engine.state.tactical_flags["hazards"])


def test_only_mutant_specialists_at_midrange_mark_and_cooldown_requires_two_normal_activations():
    for subtype, theme in [("grunt", "mutant"), ("heavy", "raider"), ("elite", "novatek_hybrid")]:
        engine, _, _ = battle(subtype, theme)
        assert engine.enemy_intents()[0].action != "TOXIN"
    engine, ally, enemy = battle()
    ally.position = (64, 64)
    engine.enemy_orders.reserve([enemy], [ally], None, [], refresh=True)
    assert engine.enemy_intents()[0].action != "TOXIN"
    ally.position = (192, 64)
    engine.enemy_orders.reserve([enemy], [ally], None, [], refresh=True)
    assert engine.enemy_intents()[0].action != "TOXIN"
    ally.position = (96, 64)
    engine.enemy_orders.reserve([enemy], [ally], None, [], refresh=True)
    engine.start_enemy_turn()
    for remaining in (1, 0):
        engine.start_player_turn()
        assert engine.enemy_intents()[0].action != "TOXIN"
        # Isolate cooldown from ordinary movement/attacks during these phases.
        with patch("game.combat.engine.run_enemy_ai", return_value=[]):
            engine.start_enemy_turn()
        assert enemy.control_cooldown == remaining
    engine.start_player_turn()
    assert engine.enemy_intents()[0].action == "TOXIN"


def test_overlaps_do_not_stack_and_expiry_preserves_static_hazards():
    engine, ally, _ = battle()
    static = HazardZone("blackout", (320, 320), 0)
    engine.state.tactical_flags["hazards"] = [static]
    engine.release_enemy_projection(None, ally.position)
    engine.release_enemy_projection(None, ally.position)
    engine.state.turn = "enemy"
    engine.start_player_turn()
    assert ally.health == 49 and ally.action_points == 1
    engine.state.turn = "enemy"
    engine.start_player_turn()
    assert engine.state.tactical_flags["hazards"] == [static]
    assert ally.health == 49 and ally.action_points == 2


def test_execution_rechecks_range_after_reservation():
    engine, _, enemy = battle()
    enemy.position = (320, 320)
    engine.start_enemy_turn()
    assert not engine.state.tactical_flags["hazards"]
    assert any("cast_blocked" in line for line in engine.state.logs)
