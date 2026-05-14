"""Small Arcade drawing helpers shared by management views."""

from __future__ import annotations

import arcade


def draw_line_group(
    title: str,
    lines: list[str],
    x: int,
    y: int,
    color=arcade.color.WHITE,
) -> int:
    """Draw a titled block of compact management text and return the next y."""
    arcade.draw_text(title, x, y, arcade.color.YELLOW, 14)
    y -= 18
    for line in lines:
        arcade.draw_text(line, x + 12, y, color, 11)
        y -= 15
    return y - 8
