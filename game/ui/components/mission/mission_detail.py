"""Mission detail section builders."""

from __future__ import annotations

from collections.abc import Iterable

from ....mission_templates import MissionComplication, MissionTemplate
from ....narrative.mission_briefing_conventions import (
    NEUTRAL_IMPACT_FALLBACK,
    build_short_emotional_impact,
    normalize_mission_tags,
    translate_legacy_briefing_text,
)
from .impact_badges import format_launch_state, format_stress_band


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
    return build_short_emotional_impact(
        hint.get("level"),
        hint.get("short_text") or hint.get("text"),
    )


def _complication_names(complications: Iterable[MissionComplication]) -> str:
    names = [complication.name for complication in complications]
    return ", ".join(names) if names else "none"


def build_mission_detail_sections(mission: MissionTemplate) -> list[str]:
    """Return mission detail split by explicit UI sections."""
    hint = mission.emotional_impact_hint or {}
    emotional_summary = translate_legacy_briefing_text(
        hint.get("emotional_impact_summary") or _short_emotional_impact(mission)
    )
    risk_explanation = translate_legacy_briefing_text(
        hint.get("risk_explanation") or "Standard tactical risk with no dominant factor."
    )
    stress_band = format_stress_band(hint.get("expected_stress_band"))
    launch_state = format_launch_state(getattr(mission, "launch_block_reason", None))

    return [
        "[Mission Summary]",
        f"Title: {mission.title}",
        f"Type: {mission.objective_type}",
        f"Duration: {mission.duration_days} day{'s' if mission.duration_days != 1 else ''}",
        "[Risk & Complications]",
        f"Risk level: {mission.risk_level}",
        f"Risk why: {risk_explanation}",
        f"Complications: {_complication_names(mission.possible_complications)}",
        "[Squad Emotional Impact]",
        f"Emotional summary: {emotional_summary}",
        stress_band,
        f"Mission tags (normalized): {_normalized_tag_names(mission)}",
        "[Rewards & Opportunity Cost]",
        f"Fund Reward: {mission.fund_reward} corporate funds",
        f"District pressure outlook: {_pressure_summary(mission.district_pressure)}",
        launch_state,
    ]
