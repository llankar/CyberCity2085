"""Cyberpunk command-HUD palette shared by management screens."""

from __future__ import annotations

# Arcade accepts RGB/RGBA tuples directly, which keeps these helpers easy to
# test without importing arcade during static unit tests.
BACKGROUND = (5, 8, 16)
PANEL_FILL = (8, 16, 30, 220)
PANEL_FILL_DARK = (3, 8, 16, 235)
PANEL_BORDER = (0, 230, 255)
PANEL_BORDER_MUTED = (45, 90, 120)
HEADER = (255, 46, 208)
TEXT = (225, 244, 255)
MUTED_TEXT = (150, 180, 195)
RESOURCE = (84, 255, 174)
WARNING = (255, 201, 74)
DANGER = (255, 77, 109)
ACCENT = (0, 236, 255)
