"""Reusable panel and status-bar drawing helpers for command screens."""

from __future__ import annotations

import arcade

from . import palette
from .command_deck import skyline_bands


def draw_panel(
    left: int, bottom: int, width: int, height: int, title: str = ""
) -> None:
    """Draw a dark translucent panel with a neon line frame."""
    right = left + width
    top = bottom + height
    arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, palette.PANEL_FILL)
    arcade.draw_line(left, bottom, right, bottom, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(left, top, right, top, palette.PANEL_BORDER, 2)
    arcade.draw_line(left, bottom, left, top, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(right, bottom, right, top, palette.PANEL_BORDER_MUTED, 1)
    if title:
        arcade.draw_text(f"▣ {title.upper()}", left + 12, top - 24, palette.HEADER, 13)


def draw_status_bar(text: str, width: int, height: int) -> None:
    """Draw the top command-HUD status bar."""
    arcade.draw_lrbt_rectangle_filled(
        0, width, height - 34, height, palette.PANEL_FILL_DARK
    )
    arcade.draw_line(0, height - 35, width, height - 35, palette.PANEL_BORDER, 2)
    arcade.draw_text(text, 18, height - 24, palette.RESOURCE, 12)


def draw_megacity_backdrop(width: int, height: int) -> None:
    """Draw a moody holographic mega-city backdrop behind command panels."""
    if hasattr(arcade, "set_background_color"):
        arcade.set_background_color(palette.BACKGROUND)
    for left, bottom, building_width, building_height in skyline_bands(width, height):
        arcade.draw_lrbt_rectangle_filled(
            left,
            left + building_width,
            bottom,
            bottom + building_height,
            palette.SKYLINE_SHADOW,
        )
        antenna_x = left + building_width // 2
        arcade.draw_line(
            antenna_x,
            bottom + building_height,
            antenna_x,
            bottom + building_height + 22,
            palette.PANEL_BORDER_MUTED,
            1,
        )
    horizon = max(92, int(height * 0.2))
    arcade.draw_line(0, horizon, width, horizon, palette.PANEL_BORDER_MUTED, 1)
    for offset in range(0, width, 96):
        arcade.draw_line(offset, 0, offset + 54, horizon, palette.GRID_LINE, 1)


def draw_deck_panel(panel) -> None:
    """Draw a command-deck panel from a layout object."""
    draw_panel(panel.left, panel.bottom, panel.width, panel.height, panel.title)
    notch = 18
    arcade.draw_line(
        panel.left + panel.width - notch,
        panel.bottom + panel.height,
        panel.left + panel.width,
        panel.bottom + panel.height - notch,
        palette.PANEL_BORDER,
        2,
    )
