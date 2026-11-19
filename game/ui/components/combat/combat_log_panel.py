"""Combat log panel builders with HUD + expanded debug views."""

from __future__ import annotations

from dataclasses import dataclass

EVENT_ALL = "all"
EVENT_COMBAT = "combat"
EVENT_SYSTEM = "system"
EVENT_EMOTIONAL = "emotional"
EVENT_STRESS = "stress"

EVENT_FILTERS = (EVENT_ALL, EVENT_COMBAT, EVENT_SYSTEM, EVENT_EMOTIONAL, EVENT_STRESS)


@dataclass(frozen=True)
class CombatLogEvent:
    """Render-neutral combat log event."""

    text: str
    event_type: str = EVENT_COMBAT


@dataclass(frozen=True)
class CombatLogPanelLine:
    """Line contract shared by HUD + expanded panel variants."""

    text: str
    event_type: str
    emphasis: str = "normal"


def _normalize_event_type(event_type: str) -> str:
    if event_type in {EVENT_COMBAT, EVENT_SYSTEM, EVENT_EMOTIONAL, EVENT_STRESS}:
        return event_type
    return EVENT_SYSTEM


def _event_prefix(event_type: str) -> str:
    return {
        EVENT_COMBAT: "⚔",
        EVENT_SYSTEM: "🛰",
        EVENT_EMOTIONAL: "💬",
        EVENT_STRESS: "🪙",
    }[_normalize_event_type(event_type)]


def apply_combat_log_filter(
    events: list[CombatLogEvent],
    active_filter: str = EVENT_ALL,
) -> list[CombatLogEvent]:
    """Filter events by event type while keeping timeline order."""
    if active_filter not in EVENT_FILTERS or active_filter == EVENT_ALL:
        return events
    return [event for event in events if _normalize_event_type(event.event_type) == active_filter]


def build_combat_log_hud_lines(
    events: list[CombatLogEvent],
    active_filter: str = EVENT_ALL,
    max_lines: int = 3,
) -> list[CombatLogPanelLine]:
    """Build short HUD lines (latest-first) for live readability."""
    filtered = apply_combat_log_filter(events, active_filter=active_filter)
    if not filtered:
        return [CombatLogPanelLine("No recent combat events.", EVENT_SYSTEM, emphasis="muted")]

    visible = list(reversed(filtered[-max(1, max_lines) :]))
    return [
        CombatLogPanelLine(
            text=f"{_event_prefix(event.event_type)} {event.text}",
            event_type=_normalize_event_type(event.event_type),
            emphasis="normal",
        )
        for event in visible
    ]


def build_combat_log_expanded_lines(
    events: list[CombatLogEvent],
    active_filter: str = EVENT_ALL,
    max_lines: int = 12,
) -> list[CombatLogPanelLine]:
    """Build expanded debug-player lines with explicit event-type tags."""
    filtered = apply_combat_log_filter(events, active_filter=active_filter)
    if not filtered:
        return [CombatLogPanelLine("[SYSTEM] No events available for this filter.", EVENT_SYSTEM, emphasis="muted")]

    visible = list(reversed(filtered[-max(1, max_lines) :]))
    lines: list[CombatLogPanelLine] = []
    for event in visible:
        kind = _normalize_event_type(event.event_type)
        emphasis = "accent" if kind in {EVENT_EMOTIONAL, EVENT_STRESS} else "normal"
        lines.append(
            CombatLogPanelLine(
                text=f"[{kind.upper()}] {event.text}",
                event_type=kind,
                emphasis=emphasis,
            )
        )
    return lines
