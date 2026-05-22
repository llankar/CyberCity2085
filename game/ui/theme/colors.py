"""Semantic color tokens for command UI. Avoid raw palette usage in screens."""

from __future__ import annotations

from dataclasses import dataclass

from .. import palette


@dataclass(frozen=True)
class ColorTokens:
    surface_primary: tuple[int, int, int] = palette.PANEL_FILL
    surface_elevated: tuple[int, int, int] = palette.PANEL_FILL_DARK
    surface_slot: tuple[int, int, int] = palette.HUD_SLOT_FILL

    text_primary: tuple[int, int, int] = palette.HEADER
    text_secondary: tuple[int, int, int] = palette.PANEL_BORDER_MUTED

    accent_primary: tuple[int, int, int] = palette.HEADER
    accent_warning: tuple[int, int, int] = palette.AMBER_FILL
    accent_danger: tuple[int, int, int] = palette.DANGER
    accent_success: tuple[int, int, int] = palette.TACTICAL_GREEN


colors = ColorTokens()
