"""Select concise, factual tactical memories for existing narrative surfaces."""

from __future__ import annotations

from collections.abc import Iterable


_TACTICAL_MARKERS = (
    " held on at ",
    " decisive objective actions",
    " stayed in the fight after taking ",
    " under fire",
    " fell during ",
    " lost an activation to panic during ",
)


def latest_tactical_memory(history: Iterable[object] | None) -> str:
    """Return the newest known combat memory, excluding unrelated history."""
    entries = list(history or [])
    for entry in reversed(entries):
        text = str(entry).strip()
        lowered = f" {text.casefold()} "
        if any(marker in lowered for marker in _TACTICAL_MARKERS):
            return text
    return ""


def tactical_memory_summary(history: Iterable[object] | None, limit: int = 96) -> str:
    """Make the selected memory compact enough for cards and dialogue lines."""
    memory = latest_tactical_memory(history)
    if not memory:
        return ""
    summary = memory.split(": ", 1)[-1].strip().rstrip(".")
    if len(summary) <= limit:
        return summary
    return summary[: max(1, limit - 1)].rstrip() + "…"
