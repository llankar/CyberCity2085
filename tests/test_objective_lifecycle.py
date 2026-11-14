"""Scenario tests for the authoritative tactical objective lifecycle."""

from game.combat import CombatEngine, CombatState
from game.combat.objectives import evaluate_objective, interact_objective
from game.combat_system import _objective_pressure_step
from game.mission_objectives import BattleObjective
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit


def _unit(position=(0, 0), *, enemy=False, hp=10, name="") -> Unit:
    stats = EnemyStats(level=1) if enemy else PlayerStats(con=1)
    stats.hp = hp
    unit = Unit(
        position=position,
        stats=stats,
        health=hp,
        action_points=2,
        unit_type="enemy" if enemy else "agent",
    )
    if name:
        unit.unit_type = name
    return unit


def test_extraction_requires_two_distinct_turns_and_moves_to_exfil() -> None:
    actor = _unit((64, 64))
    objective = BattleObjective(
        "extract",
        (64, 64),
        "WITNESS",
        required_interactions=2,
        marker_positions=[(64, 64), (160, 64)],
        phase_labels=["SECURE WITNESS", "REACH EXTRACTION"],
    )

    secured = interact_objective(objective, actor, turn_number=1)
    repeated = interact_objective(objective, actor, turn_number=1)
    actor.position = objective.position
    extracted = interact_objective(objective, actor, turn_number=2)

    assert secured.reason == "objective_progress"
    assert objective.interaction_turns == [1, 2]
    assert repeated.reason == "interaction_already_used_this_turn"
    assert extracted.status == "victory"


def test_sabotage_creates_one_turn_counterpush_before_victory() -> None:
    actor = _unit((64, 64))
    objective = BattleObjective(
        "sabotage",
        (64, 64),
        "RELAY",
        hold_turns_after_interaction=1,
        phase_labels=["PLANT CHARGE", "SURVIVE COUNTERPUSH"],
    )

    planted = interact_objective(objective, actor, turn_number=2)
    holding = evaluate_objective(
        objective, turn_number=2, allied_units=[actor], enemy_units=[_unit((320, 64), enemy=True)]
    )
    survived = evaluate_objective(
        objective, turn_number=3, allied_units=[actor], enemy_units=[_unit((320, 64), enemy=True)]
    )

    assert planted.status == "ongoing"
    assert holding.reason == "counterpush_active"
    assert survived.status == "victory"


def test_enemy_contests_interaction_and_pressures_interactable_marker() -> None:
    actor = _unit((64, 64))
    enemy = _unit((96, 64), enemy=True)
    objective = BattleObjective("data_theft", (64, 64), "CACHE", required_interactions=2)

    result = interact_objective(objective, actor, turn_number=1, enemy_units=[enemy])
    pressure_step = _objective_pressure_step(_unit((160, 64), enemy=True), objective)

    assert result.reason == "objective_contested"
    assert objective.progress == 0
    assert pressure_step == (-32, 0)


def test_non_elimination_objective_does_not_end_when_hostiles_are_gone() -> None:
    actor = _unit((0, 0))
    objective = BattleObjective("recon", (320, 320), "SCAN", required_interactions=3)

    result = evaluate_objective(
        objective, turn_number=2, allied_units=[actor], enemy_units=[]
    )

    assert result.status == "ongoing"
    assert result.reason == "objective_in_progress"


def test_engine_records_only_successful_objective_contributions() -> None:
    actor = _unit((0, 0), name="Iris")
    objective = BattleObjective("data_theft", (96, 0), "CACHE", required_interactions=2)
    state = CombatState(None, [actor], [], objective=objective, turn="player", turn_number=1)
    engine = CombatEngine(state)

    blocked = engine.interact_with_objective(actor)
    actor.position = (96, 0)
    advanced = engine.interact_with_objective(actor)

    assert blocked.reason == "interaction_blocked"
    assert advanced.reason == "objective_progress"
    assert state.tactical_flags["objective_contributions"] == {"Iris": 1}
