"""Render-ready helper for discreetly flagging relationship-critical choices."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CriticalChoiceHighlight:
    marker: str
    text: str
    emphasis: str = "muted"


_IMPACT_COPY = {
    "low": CriticalChoiceHighlight("", "", "muted"),
    "medium": CriticalChoiceHighlight("◦", "Lien: impact modéré", "normal"),
    "high": CriticalChoiceHighlight("◆", "Lien: impact élevé", "accent"),
}


def normalize_relation_impact(relation_impact: str | None) -> str:
    level = str(relation_impact or "low").strip().lower()
    if level not in {"low", "medium", "high"}:
        return "low"
    return level


def build_critical_choice_highlight(relation_impact: str | None) -> CriticalChoiceHighlight:
    """Return display metadata for a relation-impact marker."""
    return _IMPACT_COPY[normalize_relation_impact(relation_impact)]


def format_critical_choice_suffix(relation_impact: str | None) -> str:
    """Return a compact inline suffix for line-based UI screens."""
    highlight = build_critical_choice_highlight(relation_impact)
    if not highlight.marker:
        return ""
    return f" {highlight.marker} {highlight.text}"
