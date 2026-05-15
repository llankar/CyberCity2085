"""XCOM2-inspired command-center layout primitives for CyberCity screens.

The module stays intentionally small: it describes panel placement and terse
copy. Arcade drawing remains in ``panels.py`` so layout rules can be tested
without opening a window.
"""

from __future__ import annotations

from dataclasses import dataclass


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
    """Build a consistent command-room layout for Corp and City screens."""
    margin = 18
    gutter = 14
    status_height = 46
    footer_height = 48
    top = height - status_height - margin
    body_bottom = footer_height
    body_height = max(420, top - body_bottom)
    left_width = max(380, int(width * 0.34))
    right_width = max(420, width - (margin * 2) - gutter - left_width)
    left = margin
    right = left + left_width + gutter
    half_height = (body_height - gutter) // 2

    if mode == "city":
        titles = {
            "left": "City Situation Room",
            "right_top": "District Pressure Map",
            "right_bottom": "Faction / Operations Feed",
        }
    else:
        titles = {
            "left": "Corporate War Room",
            "right_top": "Upgrade Foundry",
            "right_bottom": "District Fallout Feed",
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


def panel_by_key(panels: list[CommandPanel], key: str) -> CommandPanel:
    """Fetch a command-center panel by key."""
    for panel in panels:
        if panel.key == key:
            return panel
    raise KeyError(key)


def build_command_title(mode: str, base_name: str, district_name: str) -> str:
    """Return a cinematic command-room title strip."""
    label = "CITY CONTROL" if mode == "city" else "CORPORATE COMMAND"
    return f"{label} // {base_name.upper()} // {district_name.upper()}"


def build_action_strip(actions: list[str]) -> str:
    """Join controls into an XCOM-like bottom input strip."""
    return "  ▸  ".join(actions)
