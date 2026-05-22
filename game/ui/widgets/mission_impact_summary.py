"""Helpers to render mission impact summary with operational tags and human impact hint."""

from __future__ import annotations

from ..accessibility.states import label_with_non_color_indicator

NEUTRAL_IMPACT_TEXT = "Impact humain attendu: informations limitées, vigilance recommandée."
IMPACT_LEVEL_LABELS = {
    "low": "faible",
    "medium": "modéré",
    "high": "élevé",
    "critical": "critique",
}


def _tag_names(tagged_items: list[object], empty: str = "none") -> str:
    names = [getattr(tag, "name", str(tag)) for tag in tagged_items]
    return ", ".join(names) if names else empty


def impact_hint_text(emotional_impact_hint: dict | None) -> str:
    """Return a readable impact hint with fallback for missing/invalid payload."""
    if not emotional_impact_hint:
        return NEUTRAL_IMPACT_TEXT

    level = str(emotional_impact_hint.get("level", "")).lower()
    text = str(emotional_impact_hint.get("text", "")).strip()
    if level not in IMPACT_LEVEL_LABELS or not text:
        return NEUTRAL_IMPACT_TEXT
    return f"Impact humain attendu ({IMPACT_LEVEL_LABELS[level]}): {text}"


def build_mission_impact_summary_lines(mission: object) -> list[str]:
    """Build ordered mission impact lines: operational tags first, then human hint."""
    tags = _tag_names(getattr(mission, "tags", []))
    hint = impact_hint_text(getattr(mission, "emotional_impact_hint", None))
    return [
        label_with_non_color_indicator(f"Tags opérationnels: {tags}", "normal"),
        label_with_non_color_indicator(hint, "focus"),
    ]
