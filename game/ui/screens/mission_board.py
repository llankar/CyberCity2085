"""Mission board presentation helpers for the RPG command screen."""

from __future__ import annotations

from ...mission_templates import MissionTemplate
from ...narrative.mission_briefing_conventions import build_short_emotional_impact
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


def _mission_consequence_preview(mission: MissionTemplate) -> str:
    pressure = mission.district_pressure or {}
    volatility = int(pressure.get("unrest", 0)) + int(pressure.get("media_heat", 0))
    if volatility >= 8:
        return "Likely district escalation"
    if volatility >= 4:
        return "Moderate civilian tension"
    return "Contained consequences"


def _emotional_impact_short(mission: MissionTemplate) -> str:
    hint = mission.emotional_impact_hint or {}
    if not isinstance(hint, dict):
        return "neutral"
    return build_short_emotional_impact(hint.get("level"), hint.get("short_text") or hint.get("text"))


def recommended_action_for_mission(mission: MissionTemplate | None) -> str:
    """Return contextual recommendation for management screens."""
    if mission is None:
        return "Recommended action: select a priority mission to review."
    if mission.risk_level >= 4:
        return "Recommended action: assign support before launch."
    if mission.duration_days >= 3:
        return "Recommended action: secure resources for multiple days."
    return "Recommended action: launch quickly to keep the initiative."


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

    emotional = _emotional_impact_short(mission)
    return [
        f"Risk: {mission.risk_level} ({risk_label(mission.risk_level)})",
        f"Duration: {mission.duration_days} day{'s' if mission.duration_days != 1 else ''}",
        f"Cost: {max(0, mission.duration_days * 2)} command bandwidth",
        f"Emotional impact: {emotional}",
        f"Consequence: {_mission_consequence_preview(mission)}",
        recommended_action_for_mission(mission),
        *build_mission_detail_sections(mission),
    ]


def build_interactive_tooltips() -> dict[str, str]:
    """English tooltip copy for key interactive UI elements."""
    return {
        "mission_list": "Open the world map to choose a mission.",
        "launch_action": "Launch current mission with selected squad.",
        "risk": "Higher risk means heavier resistance.",
    }
