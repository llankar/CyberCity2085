from types import SimpleNamespace

import pytest

from game.mission_objectives import create_battle_objective
from game.ui.components.combat.objective_brief import objective_brief_lines


def objective(kind):
    return create_battle_objective(SimpleNamespace(objective_type=kind))


@pytest.mark.parametrize("kind",("defend","containment","assassination"))
def test_passive_objectives_never_offer_an_interaction(kind):
    progress,instruction=objective_brief_lines(objective(kind),turn_number=5,defend_turns_required=8,enemy_count=3)
    assert "E:" not in instruction and "AP" not in instruction
    if kind=="defend":assert "5/8" in progress
    if kind=="containment":assert "3" in progress


def test_interactive_and_counterpush_instructions_follow_actual_phase():
    goal=objective("sabotage")
    assert "1 AP" in objective_brief_lines(goal)[1]
    goal.completed=True
    goal.hold_until_turn=4
    assert "Counterpush" in objective_brief_lines(goal,turn_number=3)[0]
    assert "E:" not in objective_brief_lines(goal,turn_number=3)[1]
    assert objective_brief_lines(goal,turn_number=4)[0]=="Objective complete"


def test_failure_takes_priority_over_normal_instructions():
    goal=objective("defend")
    goal.failed=True
    goal.failure_message="Hostile crossed the zone."
    assert objective_brief_lines(goal)==("FAILED",goal.failure_message)
