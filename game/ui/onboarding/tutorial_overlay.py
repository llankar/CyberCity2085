"""Tutorial overlay rendering and cross-screen help panel content."""

from __future__ import annotations

from dataclasses import dataclass

from .tutorial_copy_en import HELP_COPY, TUTORIAL_OBJECTIVES, TUTORIAL_TITLES
from .tutorial_steps import current_step_key


@dataclass(frozen=True)
class OverlayHighlight:
    screen: str
    target: str
    arrow: str


HIGHLIGHTS = {
    "enter_rooms": OverlayHighlight("corp", "facility_room", "Click any lit room."),
    "select_agents": OverlayHighlight("squad", "barracks", "Choose an agent card."),
    "form_squad": OverlayHighlight("squad", "insertion", "Toggle at least two agents."),
    "open_mission_board": OverlayHighlight("squad", "ops", "Open Operations Table."),
    "launch_mission": OverlayHighlight("squad", "launch", "Press launch."),
    "basic_battle_controls": OverlayHighlight("battle", "action_bar", "Try move + attack."),
}


def build_help_panel(screen: str, objective: str | None) -> dict[str, object]:
    copy = HELP_COPY.get(screen, HELP_COPY["corp"])
    return {
        "objective": objective or "No active objective.",
        "controls": list(copy["controls"]),
        "next": copy["next"],
    }


def overlay_state_for_screen(progress: dict, screen: str) -> dict[str, object]:
    step = current_step_key(progress)
    if step is None:
        return {"visible": False}
    highlight = HIGHLIGHTS.get(step)
    objective = f"{TUTORIAL_TITLES[step]}: {TUTORIAL_OBJECTIVES[step]}"
    visible = bool(highlight and highlight.screen == screen)
    return {
        "visible": visible,
        "step": step,
        "objective": objective,
        "highlight_target": highlight.target if highlight else "",
        "arrow_text": highlight.arrow if highlight else "",
        "help": build_help_panel(screen, objective),
    }
