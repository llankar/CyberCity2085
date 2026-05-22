"""Shared UI badges used across tactical cards and overlays."""

from __future__ import annotations

import arcade

from ... import palette


def draw_upgrade_badge(points: int, left: int, bottom: int) -> None:
    """Draw a numbered pending-upgrade badge."""
    width = 38
    height = 22
    arcade.draw_lrbt_rectangle_filled(
        left, left + width, bottom, bottom + height, palette.RESOURCE
    )
    arcade.draw_text(
        f"PTS {points}",
        left + width // 2,
        bottom + 6,
        palette.BACKGROUND,
        8,
        anchor_x="center",
    )
