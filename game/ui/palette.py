"""City-corporate tactical command palette shared by UI screens."""

from __future__ import annotations

# Arcade accepts RGB/RGBA tuples directly, which keeps these helpers easy to
# test without importing arcade during static unit tests.
BACKGROUND = (3, 7, 11)
PANEL_FILL = (9, 18, 27, 232)
PANEL_FILL_DARK = (2, 6, 10, 242)
PANEL_BORDER = (83, 186, 255)
PANEL_BORDER_MUTED = (31, 82, 116)
HEADER = (247, 171, 69)
TEXT = (225, 241, 248)
MUTED_TEXT = (134, 167, 181)
RESOURCE = (96, 231, 193)
WARNING = (255, 190, 76)
DANGER = (255, 88, 76)
ACCENT = (97, 207, 255)
SKYLINE_SHADOW = (5, 19, 31, 205)
GRID_LINE = (22, 84, 112, 132)
SELECTED_FILL = (32, 75, 98, 238)
AMBER_BORDER = (255, 172, 67)
AMBER_FILL = (48, 31, 10, 190)
SCANLINE = (120, 186, 220, 45)
TACTICAL_GREEN = (120, 232, 180)
