from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Tooltip:
    text_size: int
    padding: int
