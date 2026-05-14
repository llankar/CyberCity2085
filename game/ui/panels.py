"""Reusable panel and status-bar drawing helpers for command screens."""

from __future__ import annotations

import arcade

from . import palette


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
