"""Shared progress style values."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProgressStyle:
    thickness: int = 6


progress_style = ProgressStyle()
