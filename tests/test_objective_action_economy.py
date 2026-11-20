"""Objective progress is a paid allied action; passive goals cannot be clicked away."""

import pytest

from game.combat import CombatEngine, CombatState
from game.combat.objectives import evaluate_objective, interact_objective
from game.combat.encounter_qa import simulate_encounter
from game.cover_system import CoverNode
from game.mission_objectives import BattleObjective
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


def actor(position=(64, 64), enemy=False):
    return Unit(position=position, stats=EnemyStats() if enemy else PlayerStats(),
                health=50, unit_type="enemy" if enemy else "agent")


def test_two_step_download_costs_one_ap_per_squad_turn_and_rejected_attempts_are_free():
    a, b = actor(), actor((64, 96))
    objective = BattleObjective("data_theft", (64, 64), "CACHE", required_interactions=2)
    engine = CombatEngine(CombatState(None, [a, b], [], objective=objective))
    first = engine.interact_with_objective(a)
    assert first.consumed_ap == 1 and a.action_points == 1 and objective.progress == 1
    assert a._actions_used == 1
    repeated = engine.interact_with_objective(b)
    assert repeated.reason == "interaction_already_used_this_turn"
    assert b.action_points == 2 and objective.progress == 1
    assert getattr(b, "_actions_used", 0) == 0
    engine.state.turn = "enemy"
    engine.start_player_turn()
    last = engine.interact_with_objective(b)
    assert last.status == "victory" and last.consumed_ap == 1 and b.action_points == 1
    assert sum(engine.state.tactical_flags["objective_contributions"].values()) == 2
    assert engine.interact_with_objective(b).consumed_ap == 0
    assert b.action_points == 1
    assert a._actions_used == b._actions_used == 1


@pytest.mark.parametrize("kind", ["defend", "containment", "assassination"])
def test_passive_goals_cannot_be_completed_by_pressing_interact(kind):
    a = actor()
    objective = BattleObjective(kind, a.position, "GOAL")
    result = interact_objective(objective, a, turn_number=1)
    assert result.reason == "objective_not_interactable"
    assert not objective.completed and objective.progress == 0 and a.action_points == 2


def test_dead_exhausted_enemy_and_wrong_phase_actors_cannot_advance():
    a, hostile = actor(), actor(enemy=True)
    objective = BattleObjective("extract", a.position, "WITNESS", required_interactions=2)
    engine = CombatEngine(CombatState(None, [a], [hostile], objective=objective))
    a.health = 0
    assert engine.interact_with_objective(a).consumed_ap == 0
    a.health, a.action_points = 50, 0
    assert engine.interact_with_objective(a).reason == "interaction_unavailable"
    a.action_points = 2
    assert engine.interact_with_objective(hostile).reason == "interaction_unavailable"
    engine.state.turn = "enemy"
    assert engine.interact_with_objective(a).reason == "interaction_unavailable"
    assert objective.progress == 0 and not objective.interaction_turns
    assert hostile.action_points == a.action_points == 2


def test_contested_and_remote_attempts_do_not_spend_ap_or_record_contribution():
    a, hostile = actor(), actor((96, 64), enemy=True)
    objective = BattleObjective("extract", a.position, "WITNESS", required_interactions=2)
    engine = CombatEngine(CombatState(None, [a], [hostile], objective=objective))
    assert engine.interact_with_objective(a).reason == "objective_contested"
    hostile.health = 0
    a.position = (320, 320)
    assert engine.interact_with_objective(a).reason == "interaction_blocked"
    assert a.action_points == 2 and objective.progress == 0
    assert not engine.state.tactical_flags["objective_contributions"]


def test_a_breached_objective_cannot_recover_when_the_enemy_moves_away():
    a, hostile = actor(), actor((64, 192), enemy=True)
    objective = BattleObjective("containment", (64, 256), "LINE", breach_y=192)
    engine = CombatEngine(CombatState(None, [a], [hostile], objective=objective))
    assert engine.objective_result().reason == "objective_breached"
    hostile.position = (320, 320)
    assert engine.objective_result().status == "defeat"


def test_real_objective_assault_routes_around_wall_and_spends_only_normal_movement_ap():
    a, hostile = actor((512, 320)), actor((64, 192), enemy=True)
    hostile.enemy_theme, hostile.attack_range = "corp_37", 1
    objective = BattleObjective("defend", (192, 192), "RELAY")
    walls = [CoverNode(3, y, "high", False) for y in (5, 6, 7)]
    engine = CombatEngine(CombatState(None, [a], [hostile], objective=objective), cover_nodes=walls,
                          can_enter=lambda x, y: 0 <= x <= 512 and 0 <= y <= 384)
    positions = []
    for _ in range(5):
        engine.start_player_turn()
        before = hostile.position
        result = engine.start_enemy_turn()
        positions.append(hostile.position)
        assert abs(hostile.position[0]-before[0])+abs(hostile.position[1]-before[1]) <= 64
        assert hostile.position not in {(node.world_x, node.world_y) for node in walls}
        if result.ended:
            break
    assert result.outcome == "defeat" and objective.failed
    assert any(y != 192 for _, y in positions)
    assert not any("movement_blocked" in line for line in engine.state.logs)


@pytest.mark.parametrize("kind", ["extract", "data_theft", "sabotage", "recon_scan", "civilian_rescue", "defend", "containment", "assassination"])
def test_automated_real_objective_runs_report_progress_and_true_failure_reasons(kind):
    result = simulate_encounter(theme="corp_37_robot", level=4, risk=5, count=6, seed=0,
                                policy="objective_counterplay", layout="cover", objective_kind=kind)
    assert result["outcome"] in {"victory", "defeat", "turn_limit"}
    assert 1 <= result["turns"] <= 30
    if result["objective_progress"]:
        assert sum(result["contributions"].values()) == result["objective_progress"]
    if result["outcome"] == "defeat":
        assert result["objective_reason"] in {"all_allies_down", "objective_breached", "objective_failed"}
