"""Narrative feed list ordering + rendering."""

from __future__ import annotations

from ....narrative.event_feed import NarrativeFeedEntry
from .feed_filters import FILTER_ALL, apply_feed_filter
from .feed_item import NarrativeFeedWidgetLine, to_widget_line

_PRIORITY = {
    "agent": 0,
    "consequence": 1,
    "mission": 2,
    "faction": 3,
    "system": 4,
    "base": 5,
}


def build_feed_lines(
    entries: list[NarrativeFeedEntry],
    active_filter: str = FILTER_ALL,
    clip: int = 120,
) -> list[NarrativeFeedWidgetLine]:
    filtered = apply_feed_filter(entries, active_filter=active_filter)
    ranked = sorted(
        enumerate(filtered),
        key=lambda pair: (_PRIORITY.get(pair[1].category, 99), pair[0]),
    )
    return [to_widget_line(entry, age_steps=index, clip=clip) for index, (_, entry) in enumerate(ranked)]
