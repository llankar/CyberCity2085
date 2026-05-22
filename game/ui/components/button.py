"""Shared button style values."""
from __future__ import annotations

from .foundation import Button
from ..theme import radii
from ..theme.elevation import stroke

button_style = Button(corner_radius=radii.control, border_width=stroke.hairline)
