"""Mission board presentation helpers for the RPG command screen."""

from __future__ import annotations

from ...mission_templates import MissionTemplate
from ..components.mission.mission_card import build_mission_card_line
from ..components.mission.mission_detail import build_mission_detail_sections

OBJECTIVE_LABELS = {
    "extract": "EXTRACT",
    "sabotage": "SABOTAGE",
    "data_theft": "DATA THEFT",
    "eliminate": "ELIMINATE",
    "safe_extraction": "EXTRACT",
    "data_with_detour": "DATA THEFT",
    "sabotage_window": "SABOTAGE",
}


def risk_label(risk_level: int) -> str:
    if risk_level >= 4:
        return "severe"
    if risk_level >= 2:
        return "elevated"
    return "contained"


def objective_label(objective_type: str | None) -> str:
    return OBJECTIVE_LABELS.get(objective_type or "eliminate", "ELIMINATE")


def build_mission_board_lines(missions: list[MissionTemplate], selected_index: int) -> list[str]:
    if not missions:
        return ["No missions available."]

    selected_index %= len(missions)
    return [
        build_mission_card_line(
            mission,
            index=index,
            selected=index == selected_index,
            objective_label=objective_label(mission.objective_type),
            risk_label=risk_label(mission.risk_level),
        )
        for index, mission in enumerate(missions)
    ]


def build_selected_mission_lines(mission: MissionTemplate | None) -> list[str]:
    if mission is None:
        return ["Select a mission to inspect launch pressure and fallout."]
    return build_mission_detail_sections(mission)
