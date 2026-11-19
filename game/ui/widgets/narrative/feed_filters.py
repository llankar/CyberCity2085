"""Quick filter rules for narrative feed."""

from __future__ import annotations

from ....narrative.event_feed import NarrativeFeedEntry

FILTER_ALL = "all"
FILTER_AGENTS = "agents"
FILTER_MISSIONS = "missions"
FILTER_FACTIONS = "factions"

FILTERS = (FILTER_ALL, FILTER_AGENTS, FILTER_MISSIONS, FILTER_FACTIONS)


def apply_feed_filter(entries: list[NarrativeFeedEntry], active_filter: str = FILTER_ALL) -> list[NarrativeFeedEntry]:
    if active_filter not in FILTERS or active_filter == FILTER_ALL:
        return entries
    if active_filter == FILTER_AGENTS:
        return [e for e in entries if e.category in {"agent", "consequence"}]
    if active_filter == FILTER_MISSIONS:
        return [e for e in entries if e.category == "mission"]
    return [e for e in entries if e.category == "faction"]
