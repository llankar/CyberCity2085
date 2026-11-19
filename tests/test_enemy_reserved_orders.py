"""Real Arcade engine turns consume the orders exposed to the HUD."""

from types import SimpleNamespace
from unittest.mock import patch

from game.combat import CombatEngine, CombatState
from game.combat.attack_resolution import resolve_attack
from game.cover_system import CoverNode
from game.mission_objectives import BattleObjective
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


def squad():
    a = Unit(position=(64, 0), health=30, stats=PlayerStats(max_hp=30),
             character=SimpleNamespace(name="Rook", role="samurai"))
    b = Unit(position=(96, 0), health=30, stats=PlayerStats(max_hp=30),
             character=SimpleNamespace(name="Echo", role="samurai"))
    enemy = Unit(position=(0, 0), health=30, stats=EnemyStats(max_hp=30),
                 unit_type="enemy", enemy_theme="generic", attack_range=6)
    return a, b, enemy


def test_changed_priority_does_not_retarget_between_preview_and_real_enemy_activation():
    a, b, enemy = squad()
    state = CombatState(None, [a, b], [enemy])
    engine = CombatEngine(state)
    engine.start_player_turn()
    shown = engine.enemy_intents()[0]
    assert shown.target is a
    b.health = 1  # A newly tempting wounded target must not replace the promise.
    assert engine.enemy_intents()[0] is shown
    with patch("game.combat_system.resolve_attack", return_value=SimpleNamespace(damage=0)) as attack:
        # A miss must spend AP just as the real resolver does.
        attack.side_effect = lambda actor, target, *args, **kwargs: miss(actor)
        engine.start_enemy_turn()
    assert attack.call_count == 2
    assert all(call.args[1] is a for call in attack.call_args_list)
    assert not any("interrupted" in line for line in state.logs)


def miss(actor):
    actor.action_points -= 1
    return SimpleNamespace(damage=0)


def test_target_loss_is_visible_and_explicitly_replans_once():
    a, b, enemy = squad()
    state = CombatState(None, [a, b], [enemy])
    engine = CombatEngine(state)
    engine.start_player_turn()
    a.health = 0
    assert engine.enemy_intents()[0].target is b
    assert engine.enemy_intents()[0].rationale.startswith("INTERRUPTED (target_lost)")
    engine.enemy_intents()
    assert sum("target_lost" in line for line in state.logs) == 1


def test_suppression_holds_for_one_enemy_phase_then_refreshes():
    a, b, enemy = squad()
    state = CombatState(None, [a, b], [enemy])
    engine = CombatEngine(state)
    engine.start_player_turn()
    enemy.apply_status("suppressed")
    assert engine.enemy_intents()[0].action == "HOLD"
    with patch("game.combat_system.resolve_attack") as attack:
        engine.start_enemy_turn()
    attack.assert_not_called()
    assert enemy.action_points == 0
    engine.start_player_turn()
    assert engine.enemy_intents()[0].action != "HOLD"


def test_new_blocker_changes_reserved_fire_to_visible_lane_search():
    a, b, enemy = squad()
    enemy.enemy_theme = "corp_samurai"
    a.position = (192, 0)
    b.position = (224, 0)
    state = CombatState(None, [a, b], [enemy])
    engine = CombatEngine(state, cover_nodes=[])
    engine.start_player_turn()
    assert engine.enemy_intents()[0].action == "FIRE"
    engine.cover_nodes = [CoverNode(3, 0, "high", False)]
    assert engine.enemy_intents()[0].action == "HUNT"
    assert "line_blocked" in engine.enemy_intents()[0].rationale


def test_objective_reservation_controls_actual_movement_and_blocked_order_holds():
    a, b, enemy = squad()
    enemy.enemy_theme = "corp_37"
    enemy.attack_range = 1
    a.position, b.position = (320, 0), (352, 0)
    objective = BattleObjective("defend", (0, 128), "Hold relay")
    state = CombatState(None, [a, b], [enemy], objective=objective)
    engine = CombatEngine(state, can_enter=lambda x, y: True)
    engine.start_player_turn()
    assert engine.enemy_intents()[0].action == "BREACH"
    engine.start_enemy_turn()
    assert enemy.position == (0, 64)
    engine.start_player_turn()
    engine.can_enter = lambda x, y: False
    engine.start_enemy_turn()
    assert enemy.position == (0, 64)
    assert engine.enemy_intents()[0].action == "HOLD"
    assert any("movement_blocked" in line for line in state.logs)


def test_books_are_isolated_and_new_reinforcements_get_an_order():
    a, b, enemy = squad()
    first = CombatEngine(CombatState(None, [a, b], [enemy]))
    first.start_player_turn()
    a2, b2, enemy2 = squad()
    second = CombatEngine(CombatState(None, [a2, b2], [enemy2]))
    second.start_player_turn()
    enemy.apply_status("stunned")
    assert first.enemy_intents()[0].action == "HOLD"
    assert second.enemy_intents()[0].action != "HOLD"
    second.state.enemy_units.append(squad()[2])
    assert len(second.enemy_intents()) == 2


def test_actual_attack_resolver_consumes_the_reserved_target_and_refresh_is_explicit():
    a, b, enemy = squad()
    state = CombatState(None, [a, b], [enemy])
    engine = CombatEngine(state)
    engine.start_player_turn()
    b.health = 1
    with patch("game.combat_system.resolve_attack", wraps=resolve_attack) as attack:
        engine.start_enemy_turn()
    assert attack.call_count == 2
    assert all(call.args[1] is a for call in attack.call_args_list)
    engine.start_player_turn()
    assert engine.enemy_intents()[0].target is b


def test_completed_objective_releases_the_reserved_breach_visibly():
    a, b, enemy = squad()
    enemy.enemy_theme, enemy.attack_range = "corp_37", 1
    a.position, b.position = (320, 0), (352, 0)
    objective = BattleObjective("defend", (0, 128), "Hold relay")
    engine = CombatEngine(CombatState(None, [a, b], [enemy], objective=objective))
    engine.start_player_turn()
    assert engine.enemy_intents()[0].action == "BREACH"
    objective.completed = True
    order = engine.enemy_intents()[0]
    assert order.action != "BREACH"
    assert "objective_completed" in order.rationale
