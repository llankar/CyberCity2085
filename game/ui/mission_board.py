"""Mission board presentation helpers for the RPG command screen."""

from __future__ import annotations

from collections.abc import Iterable

from ..consequences import Consequence
from ..mission_templates import MissionComplication, MissionTemplate
from ..narrative.mission_briefing_conventions import (
    NEUTRAL_IMPACT_FALLBACK,
    build_short_emotional_impact,
    normalize_mission_tags,
)
from .widgets.critical_choice_highlight import format_critical_choice_suffix
from .widgets.mission_impact_summary import build_mission_impact_summary_lines
from .accessibility.states import label_with_non_color_indicator

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
    """Translate numeric mission risk into a compact command-screen label."""
    if risk_level >= 4:
        return "severe"
    if risk_level >= 2:
        return "elevated"
    return "contained"


def objective_label(objective_type: str | None) -> str:
    """Return a readable label for a mission objective type."""
    return OBJECTIVE_LABELS.get(objective_type or "eliminate", "ELIMINATE")


def _tag_names(tagged_items: Iterable[object], empty: str = "none") -> str:
    names = [getattr(tag, "name", str(tag)) for tag in tagged_items]
    return ", ".join(names) if names else empty


def _normalized_tag_names(mission: MissionTemplate) -> str:
    hint = mission.emotional_impact_hint or {}
    tags = hint.get("normalized_tags") if isinstance(hint, dict) else None
    if not isinstance(tags, list):
        tags = normalize_mission_tags(mission.tags)
    return ", ".join(tags) if tags else "none"


def _short_emotional_impact(mission: MissionTemplate) -> str:
    hint = mission.emotional_impact_hint or {}
    if not isinstance(hint, dict):
        return NEUTRAL_IMPACT_FALLBACK
    return build_short_emotional_impact(hint.get("level"), hint.get("short_text") or hint.get("text"))


def _pressure_summary(pressure: dict) -> str:
    if not pressure:
        return "none"
    ordered_keys = ("stability", "unrest", "media_heat")
    keys = [key for key in ordered_keys if key in pressure]
    keys.extend(key for key in pressure if key not in keys)
    parts = []
    for key in keys:
        value = int(pressure[key])
        label = key.replace("_", " ").title()
        parts.append(f"{label} {value:+d}")
    return ", ".join(parts)


def _complication_names(complications: list[MissionComplication]) -> str:
    names = [complication.name for complication in complications]
    return ", ".join(names) if names else "none"


def _mechanical_effect_summary(effects: dict) -> str:
    if not effects:
        return "story fallout"
    parts = []
    for key, value in effects.items():
        label = key.replace("_", " ")
        parts.append(f"{label} {int(value):+d}")
    return ", ".join(parts)


def _outcome_line(label: str, consequences: list[Consequence]) -> str:
    if not consequences:
        return f"{label}: no recorded fallout"
    consequence = consequences[0]
    target = (
        consequence.affected_agent
        or consequence.affected_faction
        or consequence.affected_district
        or "city grid"
    )
    return (
        f"{label}: {target} - "
        f"{_mechanical_effect_summary(consequence.mechanical_effects)}"
    )


def build_mission_board_lines(
    missions: list[MissionTemplate], selected_index: int
) -> list[str]:
    """Build selectable mission rows for the RPG mission board."""
    if not missions:
        return ["No missions available."]

    selected_index %= len(missions)
    lines: list[str] = []
    for index, mission in enumerate(missions):
        state = "focus" if index == selected_index else "normal"
        prefix = ">" if index == selected_index else " "
        lines.append(
            f"{label_with_non_color_indicator(f'{prefix}{index + 1}. {mission.title}', state)} | "
            f"{objective_label(mission.objective_type)} | "
            f"Risk {mission.risk_level} ({risk_label(mission.risk_level)}) | "
            f"Reward {mission.fund_reward} funds | "
            f"Duration: {mission.duration_days} day{'s' if mission.duration_days != 1 else ''} | "
            f"{mission.target_faction} | Enemies {mission.starting_enemy_count}"
        )
    return lines


def build_selected_mission_lines(mission: MissionTemplate | None) -> list[str]:
    """Build the selected mission detail panel with pressure, stakes, and tags."""
    if mission is None:
        return ["Select a mission to inspect launch pressure and fallout."]

    return [
        f"Objective: {mission.objective_text}",
        f"District: {mission.district} | Pressure: {_pressure_summary(mission.district_pressure)}",
        f"Fund Reward: {mission.fund_reward} corporate funds",
        f"Duration: {mission.duration_days} day{'s' if mission.duration_days != 1 else ''}",
        f"Mission tags (normalized): {_normalized_tag_names(mission)}",
        f"Emotional impact (short): {_short_emotional_impact(mission)}",
        *build_mission_impact_summary_lines(mission),
        f"Complications: {_complication_names(mission.possible_complications)}",
        _outcome_line("Success", mission.success_consequences),
        _outcome_line("Failure", mission.failure_consequences),
        f"Relational impact:{format_critical_choice_suffix(getattr(mission, 'relation_impact', 'low')) or ' none'}",
    ]
