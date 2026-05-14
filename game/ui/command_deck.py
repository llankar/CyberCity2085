"""Mega-city command deck helpers for the RPG deployment screen.

The functions here keep the XCOM-like visual direction small and testable:
three readable columns, terse squad cards, and a holographic skyline mood layer.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..character import Character, is_deployable
from ..dossier import build_agent_dossier_lines
from ..mission_templates import MissionTemplate
from .mission_board import objective_label, risk_label


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
    margin = 14
    gutter = 12
    status_height = 34
    footer_height = 58
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
        DeckPanel("squad", "Squad Bay", left, body_bottom, left_width, body_height),
        DeckPanel(
            "mission",
            "City Ops Table",
            center,
            body_bottom + detail_height + gutter,
            center_width,
            body_height - detail_height - gutter,
        ),
        DeckPanel(
            "details", "Operation Intel", center, body_bottom, center_width, detail_height
        ),
        DeckPanel(
            "briefs", "Readiness / Fallout", right, body_bottom, right_width, body_height
        ),
    ]


def deck_panel_by_key(panels: list[DeckPanel], key: str) -> DeckPanel:
    """Fetch a panel from a layout by key."""
    for panel in panels:
        if panel.key == key:
            return panel
    raise KeyError(key)


def skyline_bands(
    width: int, height: int, count: int = 9
) -> list[tuple[int, int, int, int]]:
    """Build deterministic skyline silhouettes for the mega-city backdrop."""
    if count <= 0:
        return []
    band_width = max(24, width // count)
    base_height = max(80, int(height * 0.18))
    bands = []
    for index in range(count):
        left = index * band_width
        building_height = base_height + ((index * 37) % max(60, int(height * 0.16)))
        bands.append((left, 0, band_width - 3, building_height))
    return bands


def build_agent_card_lines(
    characters: list[Character], selected_names: set[str], cursor_index: int
) -> list[str]:
    """Build compact squad-card copy for the command deck's left rail."""
    if not characters:
        return ["No agents on roster. Press N to recruit a specialist."]

    lines: list[str] = []
    for index, character in enumerate(characters):
        summary, dossier = build_agent_dossier_lines(character)
        cursor = "▶" if index == cursor_index else " "
        selected = "■" if character.name in selected_names else "□"
        state = "READY" if is_deployable(character) else "MEDBAY"
        if character.recovery_turns > 0:
            state = f"MEDBAY {character.recovery_turns}T"
        legacy_cursor = ">" if index == cursor_index else " "
        legacy_selected = "[X]" if character.name in selected_names else "[ ]"
        recovery = (
            f" | Recovery: {character.recovery_turns} turns"
            if character.recovery_turns > 0
            else ""
        )
        lines.append(
            f"{cursor} {selected} {state} // {summary}{recovery} "
            f"({legacy_cursor} {legacy_selected} {character.name})"
        )
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
