"""An inaccessible objective cannot suppress every reachable combat choice."""

from unittest.mock import patch

from game.combat import CombatEngine, CombatState
from game.combat.encounter_qa import simulate_encounter
from game.mission_objectives import BattleObjective
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


def test_qa_objective_policy_can_fire_when_the_objective_route_is_unavailable(monkeypatch):
    import game.combat.encounter_qa as qa
    monkeypatch.setattr(qa, "create_battle_objective", lambda *a, **k: BattleObjective(
        "data_theft", (3200, 3200), "SEALED CACHE", required_interactions=2))
    actions = []
    perform = CombatEngine.perform_action
    def record(self, action, **kwargs):
        result = perform(self, action, **kwargs)
        if result.success:
            actions.append(action)
        return result
    with patch.object(CombatEngine, "perform_action", record):
        result = simulate_encounter(theme="generic", level=1, risk=1, count=1, seed=0,
                                    policy="objective", objective_kind="data_theft", max_turns=3)
    assert "fire" in actions
    assert result["objective_progress"] == 0


def test_blocked_objective_assault_announces_a_threat_clearance_next_phase():
    rear = Unit(position=(320, 192), health=1, stats=PlayerStats(level=5))
    front = Unit(position=(64, 64), health=50, stats=PlayerStats(level=5))
    enemy = Unit(position=(32, 192), health=50, stats=EnemyStats(level=3),
                 unit_type="enemy", enemy_theme="corp_37", attack_range=1)
    objective = BattleObjective("defend", (512, 192), "SEALED RELAY")
    state = CombatState(None, [rear, front], [enemy], objective=objective)
    engine = CombatEngine(state, can_enter=lambda x, y: 0 <= x < 256 and 0 <= y < 256)
    engine.start_player_turn()
    shown = engine.enemy_intents()[0]
    assert shown.action == "BREACH" and shown.target is None
    with patch("game.combat_system.resolve_attack") as attack:
        engine.start_enemy_turn()
    attack.assert_not_called()
    assert enemy.position == (32, 192) and enemy.action_points == 0
    assert engine.enemy_intents()[0].action == "HOLD"
    engine.start_player_turn()
    next_order = engine.enemy_intents()[0]
    assert next_order.action == "HUNT" and next_order.target is front
    assert "REORIENTED" in next_order.rationale
    assert engine.enemy_intents()[0] is next_order


def test_objective_is_not_abandoned_when_no_reachable_threat_exists():
    rear = Unit(position=(320, 192), health=50, stats=PlayerStats(level=5))
    enemy = Unit(position=(32, 192), health=50, stats=EnemyStats(),
                 unit_type="enemy", enemy_theme="corp_37", attack_range=1)
    state = CombatState(None, [rear], [enemy], objective=BattleObjective("defend", (512, 192), "RELAY"))
    engine = CombatEngine(state, can_enter=lambda x, y: 0 <= x < 256 and 0 <= y < 256)
    engine.start_player_turn()
    engine.start_enemy_turn()
    engine.start_player_turn()
    assert engine.enemy_intents()[0].action == "BREACH"
