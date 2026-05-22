"""Compact command-center narrative feed panel (agent-centered)."""

from __future__ import annotations

from ...narrative.event_feed import NarrativeFeedEntry
from .narrative.feed_filters import FILTER_ALL
from .narrative.feed_item import NarrativeFeedWidgetLine
from .narrative.feed_list import build_feed_lines


def build_narrative_feed_panel_lines(
    entries: list[NarrativeFeedEntry],
    active_filter: str = FILTER_ALL,
) -> list[NarrativeFeedWidgetLine]:
    """Transform feed entries into compact panel-ready lines."""
    if not entries:
        return [
            NarrativeFeedWidgetLine(
                "🏙 [BASE] (tense) Aucun signal narratif récent. · à l'instant",
                emphasis="muted",
                category="base",
                tone="tense",
            )
        ]
    return build_feed_lines(entries, active_filter=active_filter)
