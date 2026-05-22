"""Corporate command-center layout primitives for CyberCity screens.

The module stays intentionally small: it describes panel placement and terse
copy. Arcade drawing remains in ``panels.py`` so layout rules can be tested
without opening a window.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..theme import spacing

@dataclass(frozen=True)
class CommandPanel:
    """A named tactical panel in the city/corporate command center."""

    key: str
    title: str
    left: int
    bottom: int
    width: int
    height: int
    accent: str = "blue"


def build_command_center_layout(
    width: int, height: int, mode: str
) -> list[CommandPanel]:
    """Build a consistent corporate-tower layout for Corp and City screens."""
    margin = spacing.md + 2
    gutter = spacing.sm + 2
    status_height = 58
    footer_height = 54
    top = height - status_height - margin
    body_bottom = footer_height
    body_height = max(420, top - body_bottom)
    left_width = max(400, int(width * 0.37))
    right_width = max(420, width - (margin * 2) - gutter - left_width)
    left = margin
    right = left + left_width + gutter
    half_height = (body_height - gutter) // 2

    if mode == "city":
        titles = {
            "left": "Municipal Control Floor",
            "right_top": "District Pressure Deck",
            "right_bottom": build_narrative_feed_panel_title("city"),
        }
    else:
        titles = {
            "left": "Executive Command Floor",
            "right_top": "R&D / Security Suites",
            "right_bottom": build_narrative_feed_panel_title("corp"),
        }

    return [
        CommandPanel(
            "primary",
            titles["left"],
            left,
            body_bottom,
            left_width,
            body_height,
            "amber",
        ),
        CommandPanel(
            "top_right",
            titles["right_top"],
            right,
            body_bottom + half_height + gutter,
            right_width,
            body_height - half_height - gutter,
            "blue",
        ),
        CommandPanel(
            "bottom_right",
            titles["right_bottom"],
            right,
            body_bottom,
            right_width,
            half_height,
            "blue",
        ),
    ]


def build_narrative_feed_panel_title(mode: str) -> str:
    """Return a stable panel title for the new narrative feed widget."""
    if mode == "city":
        return "Narrative Feed / Street Ops"
    return "Narrative Feed / District Fallout"


def panel_by_key(panels: list[CommandPanel], key: str) -> CommandPanel:
    """Fetch a command-center panel by key."""
    for panel in panels:
        if panel.key == key:
            return panel
    raise KeyError(key)


def build_command_title(mode: str, base_name: str, district_name: str) -> str:
    """Return a cinematic corporate-tower title strip."""
    label = "CITY CONTROL TOWER" if mode == "city" else "AEGIS CORPORATE TOWER"
    return f"{label} // {base_name.upper()} // {district_name.upper()}"


def build_action_strip(actions: list[str]) -> str:
    """Join controls into an XCOM-like bottom input strip."""
    return "  >  ".join(actions)
