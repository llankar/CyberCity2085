"""Reusable panel and status-bar drawing helpers for command screens."""

from __future__ import annotations

import arcade

from . import palette
from .command_deck import skyline_bands


def draw_panel(
    left: int, bottom: int, width: int, height: int, title: str = ""
) -> None:
    """Draw an angled tactical glass panel with XCOM-like command-room lines."""
    right = left + width
    top = bottom + height
    cut = 18
    arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, palette.PANEL_FILL)
    arcade.draw_lrbt_rectangle_filled(
        left, right, top - 30, top, palette.PANEL_FILL_DARK
    )
    arcade.draw_line(left + cut, top, right, top, palette.PANEL_BORDER, 2)
    arcade.draw_line(left, top - cut, left + cut, top, palette.PANEL_BORDER, 2)
    arcade.draw_line(left, bottom, right - cut, bottom, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(
        right - cut, bottom, right, bottom + cut, palette.PANEL_BORDER_MUTED, 1
    )
    arcade.draw_line(left, bottom, left, top - cut, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(right, bottom + cut, right, top, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(left + 8, top - 30, right - 8, top - 30, palette.GRID_LINE, 1)
    if title:
        arcade.draw_text(f"◆ {title.upper()}", left + 14, top - 22, palette.HEADER, 13)


def draw_status_bar(text: str, width: int, height: int) -> None:
    """Draw the top Avenger-style command-HUD status bar."""
    arcade.draw_lrbt_rectangle_filled(
        0, width, height - 42, height, palette.PANEL_FILL_DARK
    )
    arcade.draw_lrbt_rectangle_filled(
        0, min(width, 280), height - 42, height, palette.AMBER_FILL
    )
    arcade.draw_line(0, height - 43, width, height - 43, palette.PANEL_BORDER, 2)
    arcade.draw_line(22, height - 8, 120, height - 8, palette.HEADER, 3)
    arcade.draw_text(text, 18, height - 28, palette.RESOURCE, 12)


def draw_megacity_backdrop(width: int, height: int) -> None:
    """Draw a moody holographic mega-city backdrop behind command panels."""
    if hasattr(arcade, "set_background_color"):
        arcade.set_background_color(palette.BACKGROUND)
    arcade.draw_lrbt_rectangle_filled(0, width, 0, height, palette.BACKGROUND)
    for y in range(70, height, 72):
        arcade.draw_line(0, y, width, y, palette.SCANLINE, 1)
    for left, bottom, building_width, building_height in skyline_bands(
        width, height, count=13
    ):
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
            bottom + building_height + 24,
            palette.PANEL_BORDER_MUTED,
            1,
        )
        arcade.draw_line(
            left + 5,
            bottom + building_height - 12,
            left + building_width - 8,
            bottom + building_height - 12,
            palette.GRID_LINE,
            1,
        )
    horizon = max(110, int(height * 0.22))
    arcade.draw_line(0, horizon, width, horizon, palette.PANEL_BORDER_MUTED, 2)
    for offset in range(-width, width * 2, 96):
        arcade.draw_line(offset, 0, offset + 74, horizon, palette.GRID_LINE, 1)
    for offset in range(0, width, 120):
        arcade.draw_line(offset, 0, offset, horizon, palette.GRID_LINE, 1)


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


def draw_command_screen_frame(title: str, width: int, height: int) -> None:
    """Draw global command-room chrome around any management screen."""
    draw_megacity_backdrop(width, height)
    arcade.draw_lrbt_rectangle_filled(
        14, width - 14, height - 76, height - 46, palette.PANEL_FILL_DARK
    )
    arcade.draw_line(
        14, height - 76, width - 14, height - 76, palette.PANEL_BORDER_MUTED, 1
    )
    arcade.draw_text(title, 28, height - 68, palette.HEADER, 16)


def draw_action_strip(text: str, width: int) -> None:
    """Draw the bottom keyboard command strip."""
    arcade.draw_lrbt_rectangle_filled(0, width, 0, 42, palette.PANEL_FILL_DARK)
    arcade.draw_line(0, 43, width, 43, palette.PANEL_BORDER, 2)
    arcade.draw_text(text, 20, 16, palette.ACCENT, 13)


def draw_tactical_meter(
    left: int, bottom: int, width: int, label: str, value: int
) -> None:
    """Draw a compact 0-100 pressure meter for city/corp status panels."""
    clamped = max(0, min(100, value))
    arcade.draw_text(label.upper(), left, bottom + 9, palette.MUTED_TEXT, 10)
    arcade.draw_lrbt_rectangle_filled(
        left + 110, left + 110 + width, bottom + 8, bottom + 18, palette.PANEL_FILL_DARK
    )
    arcade.draw_lrbt_rectangle_filled(
        left + 110,
        left + 110 + int(width * clamped / 100),
        bottom + 8,
        bottom + 18,
        (
            palette.DANGER
            if clamped >= 70
            else palette.WARNING if clamped >= 40 else palette.TACTICAL_GREEN
        ),
    )
