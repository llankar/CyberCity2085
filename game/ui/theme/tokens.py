"""Backward-compatible theme token re-exports."""

from __future__ import annotations

from dataclasses import dataclass

from .elevation import elevation, stroke
from .radii import radii as radius
from .spacing import spacing


@dataclass(frozen=True)
class OpacityTokens:
    overlay_dim: int = 164


opacity = OpacityTokens()
