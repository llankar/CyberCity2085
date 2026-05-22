"""Track high-impact relational choices for narrative follow-up."""

from __future__ import annotations


def _ensure_relation_log(game_state) -> list[dict[str, str]]:
    log = getattr(game_state, "relation_impact_log", None)
    if isinstance(log, list):
        return log
    game_state.relation_impact_log = []
    return game_state.relation_impact_log


def record_relation_impact(
    game_state, source: str, level: str, context: str = ""
) -> dict[str, str]:
    """Persist one relation-impact decision and emit a compact event beat."""
    entry = {
        "source": str(source),
        "level": str(level),
        "context": str(context),
        "day": str(getattr(game_state.calendar, "current_day", 0)),
    }
    log = _ensure_relation_log(game_state)
    log.append(entry)
    del log[:-24]
    game_state.add_event(f"Relationship pressure tracked ({entry['level']}): {entry['context']}.")
    return entry
