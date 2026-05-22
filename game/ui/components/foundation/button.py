from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Button:
    corner_radius: int
    border_width: int
