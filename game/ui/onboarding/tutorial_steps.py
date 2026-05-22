"""Ordered onboarding steps and completion checks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TutorialStep:
    key: str
    order: int
    event: str


TUTORIAL_STEPS = [
    TutorialStep("enter_rooms", 0, "entered_room"),
    TutorialStep("select_agents", 1, "selected_agent"),
    TutorialStep("form_squad", 2, "formed_squad"),
    TutorialStep("open_mission_board", 3, "opened_mission_board"),
    TutorialStep("launch_mission", 4, "launched_mission"),
    TutorialStep("basic_battle_controls", 5, "used_battle_controls"),
]

STEP_BY_KEY = {step.key: step for step in TUTORIAL_STEPS}


def current_step_key(progress: dict) -> str | None:
    if progress.get("tutorial_completed"):
        return None
    index = int(progress.get("tutorial_step_index", 0))
    if 0 <= index < len(TUTORIAL_STEPS):
        return TUTORIAL_STEPS[index].key
    return None


def apply_tutorial_event(progress: dict, event: str) -> bool:
    if progress.get("tutorial_skipped") or progress.get("tutorial_completed"):
        return False
    index = int(progress.get("tutorial_step_index", 0))
    if not (0 <= index < len(TUTORIAL_STEPS)):
        return False
    expected = TUTORIAL_STEPS[index]
    if event != expected.event:
        return False
    progress["tutorial_step_index"] = index + 1
    if progress["tutorial_step_index"] >= len(TUTORIAL_STEPS):
        progress["tutorial_completed"] = True
    return True
