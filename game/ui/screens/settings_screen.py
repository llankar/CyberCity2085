"""CyberCity 2085 — Settings Screen.

Accessible from the title menu.  Allows toggling display, audio, and
accessibility options that are stored in a persistent SettingsState
object written to a small JSON file next to save slots.

No GameState dependency — settings apply globally.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass, field

import arcade

from game.ui.palette import (
    ACCENT, BACKGROUND, GRID_LINE, HEADER, MUTED_TEXT,
    PANEL_BORDER, PANEL_BORDER_MUTED, PANEL_FILL_DARK,
    SCANLINE, SKYLINE_SHADOW, TACTICAL_GREEN, TEXT, WARNING,
)

# ── Settings file path ────────────────────────────────────────────────────────

_SETTINGS_PATH = os.path.join("saves", "settings.json")


@dataclass
class SettingsState:
    fullscreen:       bool  = False
    audio_enabled:    bool  = True
    music_volume:     int   = 70     # 0-100
    sfx_volume:       int   = 80     # 0-100
    high_contrast:    bool  = False
    show_grid:        bool  = True
    camera_shake:     bool  = True
    resolution_index: int   = 1      # index into _RESOLUTIONS
    display_index:    int   = 0      # index into available screens
    extra_flags: dict       = field(default_factory=dict)


_RESOLUTIONS: list[tuple[int, int]] = [
    (1280, 720),
    (1920, 1000),
    (1920, 1080),
    (2560, 1440),
]


def load_settings() -> SettingsState:
    try:
        with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        s = SettingsState()
        s.fullscreen       = bool(data.get("fullscreen",       s.fullscreen))
        s.audio_enabled    = bool(data.get("audio_enabled",    s.audio_enabled))
        s.music_volume     = int(data.get("music_volume",      s.music_volume))
        s.sfx_volume       = int(data.get("sfx_volume",        s.sfx_volume))
        s.high_contrast    = bool(data.get("high_contrast",    s.high_contrast))
        s.show_grid        = bool(data.get("show_grid",        s.show_grid))
        s.camera_shake     = bool(data.get("camera_shake",     s.camera_shake))
        s.resolution_index = int(data.get("resolution_index",  s.resolution_index))
        s.display_index    = int(data.get("display_index",     s.display_index))
        return s
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return SettingsState()


def save_settings(s: SettingsState) -> None:
    os.makedirs("saves", exist_ok=True)
    with open(_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(asdict(s), f, indent=2)


# ── Layout helpers ────────────────────────────────────────────────────────────

def _rect(l, b, r, t, color) -> None:
    arcade.draw_lrbt_rectangle_filled(l, r, b, t, color)


def _in(l: int, b: int, r: int, t: int, x: int, y: int) -> bool:
    return l <= x <= r and b <= y <= t


def _available_screens() -> list[object]:
    try:
        screens = list(arcade.get_screens())
    except Exception:
        screens = []
    return screens or [None]


def _screen_label(screen: object | None, index: int) -> str:
    if screen is None:
        return "Primary display"
    name = ""
    try:
        name = str(screen.get_monitor_name() or "").strip()
    except Exception:
        name = ""
    if not name:
        try:
            name = str(screen.get_device_name() or "").strip()
        except Exception:
            name = ""
    prefix = name if name else f"Display {index + 1}"
    try:
        size = f"{int(screen.width)}x{int(screen.height)}"
    except Exception:
        size = "Unknown size"
    return f"{prefix}  ({size})"


# ── View ──────────────────────────────────────────────────────────────────────

class SettingsView(arcade.View):
    """Full-screen settings panel accessible from the title menu."""

    def __init__(self) -> None:
        super().__init__()
        self._settings  = load_settings()
        self._elapsed   = 0.0
        self._message   = ""
        self._msg_timer = 0.0
        # Hit rects for toggle buttons
        self._hits: list[tuple[int, int, int, int, str]] = []

    # ── Arcade lifecycle ──────────────────────────────────────────────────────

    def on_show_view(self) -> None:
        arcade.set_background_color(BACKGROUND)

    def on_update(self, dt: float) -> None:
        self._elapsed += dt
        if self._msg_timer > 0:
            self._msg_timer = max(0.0, self._msg_timer - dt)

    def on_draw(self) -> None:
        self.clear()
        w, h = self.window.width, self.window.height
        self._hits = []
        self._draw_bg(w, h)
        self._draw_panel(w, h)

    def on_key_press(self, key: int, _modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            self._back()

    def on_mouse_press(self, x: float, y: float, _button: int, _modifiers: int) -> None:
        xi, yi = int(x), int(y)
        for (l, b, r, t, action) in self._hits:
            if _in(l, b, r, t, xi, yi):
                self._handle(action)
                return

    # ── Background ────────────────────────────────────────────────────────────

    def _draw_bg(self, w: int, h: int) -> None:
        _rect(0, 0, w, h, BACKGROUND)
        horizon = int(h * 0.28)
        for i, x in enumerate(range(-60, w + 100, 70)):
            tower_h = horizon + 38 + ((i * 41 + 7) % 140)
            _rect(x, 0, x + 48, tower_h, SKYLINE_SHADOW)
        _rect(0, 0, w, horizon, (4, 2, 6))
        arcade.draw_line(0, horizon, w, horizon, (245, 103, 55, 40), 3)
        for y in range(0, h, 5):
            arcade.draw_line(0, y, w, y, SCANLINE, 1)
        # Top / bottom bars
        _rect(0, h - 40, w, h, PANEL_FILL_DARK)
        _rect(0, 0, w, 40, PANEL_FILL_DARK)
        arcade.draw_line(0, h - 40, w, h - 40, PANEL_BORDER, 1)
        arcade.draw_line(0, 41, w, 41, PANEL_BORDER, 1)

    # ── Main panel ────────────────────────────────────────────────────────────

    def _draw_panel(self, w: int, h: int) -> None:
        cx = w // 2
        panel_w = min(700, w - 80)
        panel_h = 540
        px = cx - panel_w // 2
        py = (h - panel_h) // 2

        # Background glass
        _rect(px, py, px + panel_w, py + panel_h, (6, 12, 18, 230))
        arcade.draw_line(px, py + panel_h, px + panel_w, py + panel_h, HEADER, 2)
        arcade.draw_line(px, py,           px + panel_w, py,           PANEL_BORDER_MUTED, 1)
        arcade.draw_line(px, py,           px,           py + panel_h, PANEL_BORDER_MUTED, 1)
        arcade.draw_line(px + panel_w, py, px + panel_w, py + panel_h, PANEL_BORDER_MUTED, 1)
        # XCOM notch
        notch = 20
        arcade.draw_line(px, py + panel_h, px + notch, py + panel_h - notch, HEADER, 2)

        # Title
        arcade.draw_text(
            "SYSTEM SETTINGS", cx, py + panel_h - 22,
            HEADER, font_size=20, bold=True,
            anchor_x="center", anchor_y="center",
        )
        arcade.draw_line(px + 20, py + panel_h - 40, px + panel_w - 20, py + panel_h - 40, PANEL_BORDER, 1)

        s = self._settings
        row_h = 48
        col1 = px + 24
        col2 = px + panel_w - 200
        row_y = py + panel_h - 60

        def _section(title: str) -> None:
            nonlocal row_y
            row_y -= 8
            arcade.draw_text(title, col1, row_y, MUTED_TEXT, font_size=9, bold=True)
            row_y -= 18

        def _toggle(label: str, description: str, value: bool, action: str) -> None:
            nonlocal row_y
            ry = row_y
            # Row background
            _rect(px + 12, ry - 6, px + panel_w - 12, ry + 30, (8, 16, 22, 180))
            arcade.draw_line(px + 12, ry + 30, px + panel_w - 12, ry + 30, GRID_LINE, 1)
            # Label
            arcade.draw_text(label, col1, ry + 14, TEXT, font_size=12, bold=True, anchor_y="center")
            arcade.draw_text(description, col1, ry + 4, MUTED_TEXT, font_size=9, anchor_y="center")
            # Toggle button
            tw, th = 80, 28
            tx = col2 + 16
            ty = ry + 2
            on_col  = TACTICAL_GREEN if value else (40, 55, 60)
            off_col = (40, 55, 60) if value else WARNING
            _rect(tx,       ty, tx + tw // 2, ty + th, (*off_col, 200) if not value else (14, 28, 14, 200))
            _rect(tx + tw // 2, ty, tx + tw, ty + th, (*on_col, 200) if value else (14, 28, 14, 200))
            arcade.draw_line(tx, ty + th, tx + tw, ty + th, TACTICAL_GREEN if value else PANEL_BORDER_MUTED, 2)
            arcade.draw_text("OFF", tx + tw // 4, ty + th // 2, off_col if not value else MUTED_TEXT, font_size=9, bold=not value, anchor_x="center", anchor_y="center")
            arcade.draw_text("ON",  tx + 3 * tw // 4, ty + th // 2, on_col  if value  else MUTED_TEXT, font_size=9, bold=value,     anchor_x="center", anchor_y="center")
            self._hits.append((tx, ty, tx + tw, ty + th, action))
            row_y -= row_h

        def _cycle(label: str, description: str, values: list[str], current: int, action_prev: str, action_next: str) -> None:
            nonlocal row_y
            ry = row_y
            _rect(px + 12, ry - 6, px + panel_w - 12, ry + 30, (8, 16, 22, 180))
            arcade.draw_line(px + 12, ry + 30, px + panel_w - 12, ry + 30, GRID_LINE, 1)
            arcade.draw_text(label, col1, ry + 14, TEXT, font_size=12, bold=True, anchor_y="center")
            arcade.draw_text(description, col1, ry + 4, MUTED_TEXT, font_size=9, anchor_y="center")
            # ◀ VALUE ▶
            vx = col2
            vy = ry + 2
            aw2 = 26
            val_w = 120
            _rect(vx, vy, vx + aw2, vy + 28, (12, 24, 32, 200))
            _rect(vx + aw2 + val_w, vy, vx + aw2 * 2 + val_w, vy + 28, (12, 24, 32, 200))
            arcade.draw_text("◀", vx + aw2 // 2, vy + 14, ACCENT, font_size=12, anchor_x="center", anchor_y="center")
            arcade.draw_text("▶", vx + aw2 + val_w + aw2 // 2, vy + 14, ACCENT, font_size=12, anchor_x="center", anchor_y="center")
            arcade.draw_text(
                values[current], vx + aw2 + val_w // 2, vy + 14,
                TEXT, font_size=10, anchor_x="center", anchor_y="center",
            )
            self._hits.append((vx, vy, vx + aw2, vy + 28, action_prev))
            self._hits.append((vx + aw2 + val_w, vy, vx + aw2 * 2 + val_w, vy + 28, action_next))
            row_y -= row_h

        # ── DISPLAY ───────────────────────────────────────────────────────
        _section("DISPLAY")
        res_labels = [f"{rw}×{rh}" for rw, rh in _RESOLUTIONS]
        _cycle(
            "Resolution", "Window size (restart required)",
            res_labels, s.resolution_index,
            "res_prev", "res_next",
        )
        screens = _available_screens()
        s.display_index = max(0, min(s.display_index, len(screens) - 1))
        _cycle(
            "Display Screen", "Choose the monitor used by the game",
            [_screen_label(screen, i) for i, screen in enumerate(screens)],
            s.display_index,
            "screen_prev", "screen_next",
        )
        _toggle("Fullscreen", "Toggle borderless fullscreen mode", s.fullscreen, "toggle_fullscreen")
        _toggle("Show Grid",  "Show tactical grid overlay in battle",   s.show_grid,    "toggle_grid")
        _toggle("High Contrast", "Increase UI element contrast", s.high_contrast, "toggle_contrast")

        row_y -= 4
        arcade.draw_line(px + 20, row_y, px + panel_w - 20, row_y, PANEL_BORDER_MUTED, 1)
        row_y -= 6

        # ── AUDIO ─────────────────────────────────────────────────────────
        _section("AUDIO")
        _toggle("Audio Enabled", "Master audio on/off",  s.audio_enabled, "toggle_audio")
        _toggle("Camera Shake",  "Screen shake on impact", s.camera_shake,  "toggle_shake")

        row_y -= 4
        arcade.draw_line(px + 20, row_y, px + panel_w - 20, row_y, PANEL_BORDER_MUTED, 1)
        row_y -= 6

        # ── KEYBOARD REFERENCE ────────────────────────────────────────────
        _section("KEYBOARD REFERENCE")
        shortcuts = [
            ("F1–F5",       "Switch management tabs"),
            ("D",           "Advance day"),
            ("S / L",       "Save / Load"),
            ("B",           "Launch mission (Squad tab)"),
            ("N",           "Recruit agent (Squad tab)"),
            ("ARROWS",      "Move unit / navigate menus"),
            ("SPACE / ENTER","Select / Confirm"),
            ("ESC",         "Back / Abort"),
        ]
        scol_l = px + 24
        scol_r = px + panel_w // 2 + 24
        for i, (key, desc) in enumerate(shortcuts[:8]):
            col = scol_l if i % 2 == 0 else scol_r
            row = row_y - (i // 2) * 18
            arcade.draw_text(f"{key:<12} — {desc}", col, row, MUTED_TEXT, font_size=9)

        # ── Message ───────────────────────────────────────────────────────
        if self._message and self._msg_timer > 0:
            arcade.draw_text(
                self._message, cx, py + 20,
                TACTICAL_GREEN, font_size=10, bold=True,
                anchor_x="center", anchor_y="center",
            )

        # ── Footer: save + back ───────────────────────────────────────────
        bw, bh = 180, 38
        # Back button
        bk_x = px + 20
        bk_y = py + 8
        _rect(bk_x, bk_y, bk_x + bw, bk_y + bh, (8, 20, 28, 220))
        arcade.draw_line(bk_x, bk_y + bh, bk_x + bw, bk_y + bh, PANEL_BORDER, 2)
        arcade.draw_text(
            "◀  BACK  [ESC]",
            bk_x + bw // 2, bk_y + bh // 2,
            MUTED_TEXT, font_size=11, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._hits.append((bk_x, bk_y, bk_x + bw, bk_y + bh, "back"))

        # Save & Apply button
        sv_x = px + panel_w - 20 - bw
        sv_y = py + 8
        _rect(sv_x, sv_y, sv_x + bw, sv_y + bh, (12, 36, 16, 220))
        arcade.draw_line(sv_x, sv_y + bh, sv_x + bw, sv_y + bh, TACTICAL_GREEN, 2)
        pulse = 0.85 + 0.15 * math.sin(self._elapsed * 2.5)
        arcade.draw_text(
            "SAVE & APPLY",
            sv_x + bw // 2, sv_y + bh // 2,
            (*TACTICAL_GREEN[:3], int(230 * pulse)), font_size=11, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._hits.append((sv_x, sv_y, sv_x + bw, sv_y + bh, "save_apply"))

    # ── Action handling ───────────────────────────────────────────────────────

    def _handle(self, action: str) -> None:
        s = self._settings
        if action == "back":
            self._back()
        elif action == "save_apply":
            self._apply_and_save()
        elif action == "toggle_fullscreen":
            s.fullscreen = not s.fullscreen
        elif action == "toggle_grid":
            s.show_grid = not s.show_grid
        elif action == "toggle_contrast":
            s.high_contrast = not s.high_contrast
        elif action == "toggle_audio":
            s.audio_enabled = not s.audio_enabled
        elif action == "toggle_shake":
            s.camera_shake = not s.camera_shake
        elif action == "res_prev":
            s.resolution_index = (s.resolution_index - 1) % len(_RESOLUTIONS)
        elif action == "res_next":
            s.resolution_index = (s.resolution_index + 1) % len(_RESOLUTIONS)
        elif action == "screen_prev":
            s.display_index = (s.display_index - 1) % len(_available_screens())
        elif action == "screen_next":
            s.display_index = (s.display_index + 1) % len(_available_screens())

    def _apply_and_save(self) -> None:
        s = self._settings
        save_settings(s)
        # Apply fullscreen immediately
        try:
            screens = _available_screens()
            screen = screens[s.display_index] if 0 <= s.display_index < len(screens) else None
            rw, rh = _RESOLUTIONS[s.resolution_index]
            if screen is not None:
                try:
                    rw = min(rw, max(640, int(screen.width) - 80))
                    rh = min(rh, max(480, int(screen.height) - 80))
                except Exception:
                    pass
            if s.fullscreen:
                self.window.set_fullscreen(True, screen=screen)
            else:
                self.window.set_fullscreen(False)
                self.window.set_size(rw, rh)
                if screen is not None:
                    try:
                        x = int(getattr(screen, "x", 0) + max(0, (int(screen.width) - rw) // 2))
                        y = int(getattr(screen, "y", 0) + max(0, (int(screen.height) - rh) // 2))
                        self.window.set_location(x, y)
                    except Exception:
                        pass
        except Exception:
            pass   # Not all platforms support dynamic resize
        self._message   = "Settings saved."
        self._msg_timer = 2.5

    def _back(self) -> None:
        from game.ui.screens.title_screen import TitleView
        self.window.show_view(TitleView())
