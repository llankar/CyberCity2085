"""Shared panel drawing helpers."""
from __future__ import annotations

import arcade

from .. import palette
from ..theme import stroke
from ..theme.typography import typography


def draw_panel_frame(left: int, bottom: int, right: int, top: int, title: str = "") -> None:
    cut = 16
    arcade.draw_line(left + cut, top, right, top, palette.PANEL_BORDER, stroke.regular)
    arcade.draw_line(left, top - cut, left + cut, top, palette.PANEL_BORDER, stroke.regular)
    arcade.draw_line(left, bottom, right - cut, bottom, palette.PANEL_BORDER_MUTED, stroke.hairline)
    arcade.draw_line(right - cut, bottom, right, bottom + cut, palette.PANEL_BORDER_MUTED, stroke.hairline)
    arcade.draw_line(left, bottom, left, top - cut, palette.PANEL_BORDER_MUTED, stroke.hairline)
    arcade.draw_line(right, bottom + cut, right, top, palette.PANEL_BORDER_MUTED, stroke.hairline)
    if title:
        arcade.draw_text(f"// {title.upper()}", left + 14, top - 23, palette.HEADER, typography.panel_title)
