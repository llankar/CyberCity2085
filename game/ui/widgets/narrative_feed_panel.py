"""Compact command-center narrative feed panel (agent-centered)."""

from __future__ import annotations

from dataclasses import dataclass

from ...narrative.event_feed import NarrativeFeedEntry

_CATEGORY_BADGES = {
    "agent": "[AGENT]",
    "mission": "[MISSION]",
    "faction": "[FACTION]",
    "base": "[BASE]",
}


@dataclass(frozen=True)
class NarrativeFeedWidgetLine:
    text: str
    emphasis: str = "normal"


def build_narrative_feed_panel_lines(entries: list[NarrativeFeedEntry]) -> list[NarrativeFeedWidgetLine]:
    """Transform feed entries into compact panel-ready lines."""
    if not entries:
        return [NarrativeFeedWidgetLine("[BASE] Aucun signal narratif récent.", emphasis="muted")]

    lines: list[NarrativeFeedWidgetLine] = []
    for entry in entries:
        badge = _CATEGORY_BADGES.get(entry.category, "[BASE]")
        lines.append(NarrativeFeedWidgetLine(f"{badge} {entry.text}"))
    return lines
