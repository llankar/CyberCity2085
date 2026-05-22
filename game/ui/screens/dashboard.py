"""Readable dashboard text builders for management views.

These helpers keep Arcade view classes focused on input/drawing while the
world-state presentation stays testable and reusable across Corp/City views.
"""

from __future__ import annotations

from collections.abc import Iterable

from ...consequences import Consequence
from ...factions import Faction
from ...world import District


def _tag_names(tagged_items: Iterable[object], empty: str = "none") -> str:
    """Return compact Savage Fate tag names for dashboard display."""
    names = [getattr(tag, "name", str(tag)) for tag in tagged_items]
    return ", ".join(names) if names else empty


def pressure_label(value: int, *, inverse: bool = False) -> str:
    """Translate a 0-100 pressure value into a readable severity label."""
    if inverse:
        if value >= 70:
            return "secure"
        if value >= 40:
            return "strained"
        return "collapsing"
    if value >= 70:
        return "critical"
    if value >= 40:
        return "volatile"
    return "contained"


def build_resource_summary_line(resources: dict[str, int]) -> str:
    """Build a compact strategic-resource strip for command status bars."""
    ordered_keys = ("credits", "intel", "salvage", "influence")
    parts = [f"{key.title()} {int(resources.get(key, 0))}" for key in ordered_keys]
    return " | ".join(parts)


def district_pressure_severity(district: District) -> str:
    """Summarize the worst current district pressure as a short severity string."""
    instability = 100 - district.stability
    worst = max(instability, district.unrest, district.media_heat)
    if worst >= 70:
        return "CRITICAL"
    if worst >= 40:
        return "VOLATILE"
    return "CONTAINED"


def build_command_status_line(
    turn: int,
    base_name: str,
    resources: dict[str, int],
    district: District,
    available_funds: int | None = None,
    campaign_date_label: str | None = None,
) -> str:
    """Build the top-line command HUD status for Corp and City screens."""
    funds_text = (
        f"FUNDS {available_funds} // " if available_funds is not None else ""
    )
    date_text = f"{campaign_date_label} // " if campaign_date_label else ""
    return (
        f"TURN {turn} // {date_text}{base_name} // "
        f"{funds_text}"
        f"{build_resource_summary_line(resources)} // "
        f"DISTRICT PRESSURE {district_pressure_severity(district)}"
    )


def build_district_status_lines(district: District) -> list[str]:
    """Build concise district pulse lines for management screens."""
    return [
        f"District: {district.name} ({district.control_faction} control)",
        (
            f"Stability {district.stability}/100 "
            f"[{pressure_label(district.stability, inverse=True)}] | "
            f"Unrest {district.unrest}/100 "
            f"[{pressure_label(district.unrest)}] | "
            f"Media Heat {district.media_heat}/100 "
            f"[{pressure_label(district.media_heat)}]"
        ),
        f"Active Tags: {_tag_names(district.tags)}",
    ]


def build_faction_pressure_lines(factions: list[Faction], limit: int = 3) -> list[str]:
    """Build faction pressure summaries sorted by hostility to the player."""
    ranked = sorted(
        factions, key=lambda faction: faction.hostility_to_player, reverse=True
    )
    lines = []
    for faction in ranked[:limit]:
        lines.append(
            f"{faction.name}: Hostility {faction.hostility_to_player}/100 | "
            f"Influence {faction.influence}/100 | "
            f"Legitimacy {faction.public_legitimacy}/100 | "
            f"Tags: {_tag_names(faction.active_tags)}"
        )
    return lines or ["No active factions tracked."]


def build_recent_consequence_lines(
    consequences: list[Consequence], limit: int = 3
) -> list[str]:
    """Build latest fallout lines with severity and affected target."""
    if not consequences:
        return ["No fallout recorded yet."]

    lines = []
    for consequence in consequences[-limit:][::-1]:
        target = (
            consequence.affected_agent
            or consequence.affected_faction
            or consequence.affected_district
            or "city grid"
        )
        text = consequence.narrative_text or "Unspecified consequence ripples outward."
        lines.append(f"S{consequence.severity} {target}: {text}")
    return lines


def build_agent_aftermath_lines(lines: list[str], limit: int = 4) -> list[str]:
    """Build compact latest agent aftermath lines for the RPG dashboard."""
    if not lines:
        return ["No agent aftermath recorded yet."]

    report_lines: list[str] = []
    for line in lines[-limit:][::-1]:
        report_lines.append(line.removeprefix("Aftermath: "))
    return report_lines


def build_event_log_lines(events: list[str], limit: int = 5) -> list[str]:
    """Build newest event-log beats first for compact screen space."""
    if not events:
        return ["No operational events logged."]
    return list(events[-limit:][::-1])
