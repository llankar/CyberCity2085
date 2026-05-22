"""City/corporate command deck helpers for the RPG deployment screen.

The functions here keep the XCOM-like visual direction small and testable:
three readable columns, terse squad cards, and a corporate base mood layer.
"""

from __future__ import annotations

from dataclasses import dataclass

from ...theme import spacing
from ....character import Character, is_deployable
from ....dossier import build_agent_dossier_lines
from ....mission_templates import MissionTemplate
from ...mission_board import objective_label, risk_label
from ...widgets.critical_choice_highlight import format_critical_choice_suffix


@dataclass(frozen=True)
class DeckPanel:
    """Simple rectangle used to place command-deck panels."""

    key: str
    title: str
    left: int
    bottom: int
    width: int
    height: int


def build_command_deck_layout(width: int, height: int) -> list[DeckPanel]:
    """Return a stable three-column RPG layout for a tactical command deck."""
    margin = spacing.md
    gutter = spacing.sm
    status_height = 54
    footer_height = 62
    top = height - status_height - margin
    body_bottom = footer_height
    body_height = max(360, top - body_bottom)

    left_width = max(280, int(width * 0.32))
    right_width = max(280, int(width * 0.32))
    center_width = max(
        300, width - (margin * 2) - (gutter * 2) - left_width - right_width
    )

    left = margin
    center = left + left_width + gutter
    right = center + center_width + gutter
    detail_height = max(150, int(body_height * 0.36))

    return [
        DeckPanel(
            "squad", "Agent Barracks", left, body_bottom, left_width, body_height
        ),
        DeckPanel(
            "mission",
            "Operations Table",
            center,
            body_bottom + detail_height + gutter,
            center_width,
            body_height - detail_height - gutter,
        ),
        DeckPanel(
            "details", "Intel Lab", center, body_bottom, center_width, detail_height
        ),
        DeckPanel(
            "briefs", "Medbay / Fallout", right, body_bottom, right_width, body_height
        ),
    ]


def deck_panel_by_key(panels: list[DeckPanel], key: str) -> DeckPanel:
    """Fetch a panel from a layout by key."""
    for panel in panels:
        if panel.key == key:
            return panel
    raise KeyError(key)


def build_agent_card_lines(
    characters: list[Character], selected_names: set[str], cursor_index: int
) -> list[str]:
    """Build compact squad-card copy for the command deck's left rail."""
    if not characters:
        return ["No agents on roster. Press N to recruit a specialist."]

    lines: list[str] = []
    for index, character in enumerate(characters):
        summary, dossier = build_agent_dossier_lines(character)
        cursor = ">" if index == cursor_index else " "
        selected = "[X]" if character.name in selected_names else "[ ]"
        state = "READY" if is_deployable(character) else "MEDBAY"
        if character.recovery_turns > 0:
            state = f"MEDBAY {character.recovery_turns}T"
        recovery = (
            f" | Recovery: {character.recovery_turns} turns"
            if character.recovery_turns > 0
            else ""
        )
        lines.append(f"{cursor} {selected} {summary} // {state}{recovery}")
        lines.append(dossier.strip())
        if character.pending_points > 0:
            lines.append(
                f"STAT UPGRADE {character.pending_points}: "
                "1 PSI 2 STR 3 AGI 4 CON 5 CHA"
            )
    return lines


def build_ops_table_header(mission: MissionTemplate | None, district_name: str) -> str:
    """Build a terse holographic table header for the selected operation."""
    if mission is None:
        return f"{district_name.upper()} // NO ACTIVE SIGNAL"
    return (
        f"{district_name.upper()} // {objective_label(mission.objective_type)} // "
        f"RISK {mission.risk_level} {risk_label(mission.risk_level).upper()}"
    )


def build_calendar_status_line(date_label: str, day: int, week: int) -> str:
    """Build a small command-deck calendar prompt for manual day advancement."""
    return f"{date_label} // DAY {day} // WEEK {week} // D ADVANCE DAY"


def build_corporate_finance_lines(
    next_income_date: str, projected_income: int
) -> list[str]:
    """Build compact recurring-funding copy for corporate management rooms."""
    return [
        f"Next weekly income {next_income_date}",
        f"Projected income +{max(0, int(projected_income))} funds",
    ]


def build_event_panel_lines(active_events, current_day: int) -> list[str]:
    """Build command-deck copy for unresolved strategic events and choices."""
    if not active_events:
        return [
            "No unresolved strategic events.",
            "Advance the calendar to scan pressure feeds.",
        ]

    lines: list[str] = []
    for index, event in enumerate(active_events[:3], start=1):
        days_left = event.days_remaining(current_day)
        lines.append(
            f"{index}. {event.title} [{event.category}] severity {event.severity} ({days_left}d)"
        )
        for choice_index, choice in enumerate(event.choices[:2], start=1):
            summary = f" - {choice.summary}" if choice.summary else ""
            suffix = format_critical_choice_suffix(getattr(choice, "relation_impact", "low"))
            lines.append(f"   {index}.{choice_index} {choice.label}{summary}{suffix}")
    return lines
