"""Reusable UI design tokens for CyberCity command surfaces."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TypographyTokens:
    title: int = 22
    section: int = 13
    meta: int = 9


@dataclass(frozen=True)
class StrokeTokens:
    hairline: int = 1
    regular: int = 2
    strong: int = 3


@dataclass(frozen=True)
class SpacingTokens:
    xs: int = 8
    sm: int = 14
    md: int = 18
    lg: int = 24
    xl: int = 34


@dataclass(frozen=True)
class RadiusTokens:
    sm: int = 8
    md: int = 14


@dataclass(frozen=True)
class OpacityTokens:
    overlay_dim: int = 164


@dataclass(frozen=True)
class ZOrderTokens:
    backdrop: int = 0
    panel: int = 10
    modal: int = 20
    controls: int = 30


typography = TypographyTokens()
stroke = StrokeTokens()
spacing = SpacingTokens()
radius = RadiusTokens()
opacity = OpacityTokens()
z_order = ZOrderTokens()
