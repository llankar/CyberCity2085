"""Helpers to render mission impact summary with operational tags and human impact hint."""

from __future__ import annotations

from ...i18n import t
from ...narrative.mission_briefing_conventions import translate_legacy_briefing_text
from ..accessibility.states import label_with_non_color_indicator

NEUTRAL_IMPACT_TEXT = t("ui.impact.neutral")


def _tag_names(tagged_items: list[object], empty: str = "none") -> str:
    names = [getattr(tag, "name", str(tag)) for tag in tagged_items]
    return ", ".join(names) if names else empty


def impact_hint_text(emotional_impact_hint: dict | None, language: str | None = None) -> str:
    """Return a readable impact hint with fallback for missing/invalid payload."""
    if not emotional_impact_hint:
        return t("ui.impact.neutral", language)

    level = str(emotional_impact_hint.get("level", "")).lower()
    text = translate_legacy_briefing_text(emotional_impact_hint.get("text", ""))
    if level not in {"low", "medium", "high", "critical"} or not text:
        return t("ui.impact.neutral", language)
    return t("ui.impact.prefix", language, level=t(f"ui.impact.level.{level}", language), text=text)


def build_mission_impact_summary_lines(mission: object, language: str | None = None) -> list[str]:
    """Build ordered mission impact lines: operational tags first, then human hint."""
    tags = _tag_names(getattr(mission, "tags", []))
    hint = impact_hint_text(getattr(mission, "emotional_impact_hint", None), language)
    return [
        label_with_non_color_indicator(f"Operational tags: {tags}", "normal"),
        label_with_non_color_indicator(hint, "focus"),
    ]
