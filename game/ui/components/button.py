"""Shared button style values."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ButtonStyle:
    corner_radius: int = 8
    border_width: int = 1


button_style = ButtonStyle()
