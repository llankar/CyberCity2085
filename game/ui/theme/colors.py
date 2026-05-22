"""Semantic color aliases for command surfaces."""

from __future__ import annotations

from dataclasses import dataclass

from .. import palette


@dataclass(frozen=True)
class SurfaceColors:
    primary: tuple[int, int, int] = palette.PANEL_FILL
    elevated: tuple[int, int, int] = palette.PANEL_FILL_DARK
    slot: tuple[int, int, int] = palette.HUD_SLOT_FILL


@dataclass(frozen=True)
class AccentColors:
    primary: tuple[int, int, int] = palette.HEADER
    muted_border: tuple[int, int, int] = palette.PANEL_BORDER_MUTED


@dataclass(frozen=True)
class WarningColors:
    primary: tuple[int, int, int] = palette.AMBER_FILL


@dataclass(frozen=True)
class DangerColors:
    primary: tuple[int, int, int] = palette.DANGER


@dataclass(frozen=True)
class SuccessColors:
    primary: tuple[int, int, int] = palette.TACTICAL_GREEN


surface = SurfaceColors()
accent = AccentColors()
warning = WarningColors()
danger = DangerColors()
success = SuccessColors()
