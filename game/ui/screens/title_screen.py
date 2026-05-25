"""CyberCity 2085 — Title Screen & Main Menu.

Animated XCOM2-style main menu: city silhouette backdrop, pulsing corp
logo, keyboard/mouse-navigable buttons.  Pure Arcade draw calls so the
cyberpunk aesthetic stays consistent with the rest of the UI layer.
"""

from __future__ import annotations

import math
from pathlib import Path

import arcade

from game.ui.palette import (
    ACCENT,
    BACKGROUND,
    GRID_LINE,
    HEADER,
    MUTED_TEXT,
    PANEL_BORDER,
    PANEL_FILL_DARK,
    SCANLINE,
    SKYLINE_SHADOW,
    TEXT,
)

# ── Layout ─────────────────────────────────────────────────────────────────

_MENU_ITEMS: list[tuple[str, str]] = [
    ("NEW GAME",  "new_game"),
    ("CONTINUE",  "continue"),
    ("SETTINGS",  "settings"),
    ("QUIT",      "quit"),
]

_BTN_W      = 340
_BTN_H      = 54
_BTN_GAP    = 14
_TITLE_FRAC = 0.70   # y-fraction of window for title baseline
_MENU_FRAC  = 0.50   # y-fraction for top of first button
_TITLE_BACKGROUND_ASSET = Path("assets/ui/title_background.png")


class TitleView(arcade.View):
    """Animated main-menu screen shown at game start."""

    def __init__(self) -> None:
        super().__init__()
        self._elapsed:     float = 0.0
        self._hover_index: int | None = None
        self._background_texture: arcade.Texture | None = None
        # Populated once per draw when window size is known.
        self._buttons: list[tuple[int, int, int, int, str, str]] = []

    # ── Arcade lifecycle ────────────────────────────────────────────────────

    def on_show_view(self) -> None:
        arcade.set_background_color(BACKGROUND)
        self._background_texture = self._load_background_texture()

    def on_draw(self) -> None:
        self.clear()
        w, h = self.window.width, self.window.height
        self._buttons = self._build_buttons(w, h)
        self._draw_background(w, h)
        self._draw_title(w, h)
        self._draw_menu(w, h)
        self._draw_footer(w, h)

    def on_update(self, delta_time: float) -> None:
        self._elapsed += delta_time

    def on_mouse_motion(self, x: float, y: float, _dx: float, _dy: float) -> None:
        self._hover_index = self._index_at(int(x), int(y))

    def on_mouse_press(self, x: float, y: float, _button: int, _modifiers: int) -> None:
        idx = self._index_at(int(x), int(y))
        if idx is not None:
            self._activate(_MENU_ITEMS[idx][1])

    def on_key_press(self, key: int, _modifiers: int) -> None:
        if key in (arcade.key.RETURN, arcade.key.ENTER, arcade.key.SPACE):
            idx = self._hover_index if self._hover_index is not None else 0
            self._activate(_MENU_ITEMS[idx][1])
        elif key == arcade.key.ESCAPE:
            self._activate("quit")
        elif key in (arcade.key.UP, arcade.key.W):
            n = len(_MENU_ITEMS)
            self._hover_index = ((self._hover_index or 0) - 1) % n
        elif key in (arcade.key.DOWN, arcade.key.S):
            n = len(_MENU_ITEMS)
            self._hover_index = ((self._hover_index or 0) + 1) % n

    # ── Button geometry ─────────────────────────────────────────────────────

    def _build_buttons(self, w: int, h: int) -> list[tuple[int, int, int, int, str, str]]:
        cx    = w // 2
        top_y = int(h * _MENU_FRAC)
        btns  = []
        for i, (label, key) in enumerate(_MENU_ITEMS):
            y_top = top_y - i * (_BTN_H + _BTN_GAP)
            y_bot = y_top - _BTN_H
            btns.append((cx - _BTN_W // 2, y_bot, cx + _BTN_W // 2, y_top, label, key))
        return btns

    def _load_background_texture(self) -> arcade.Texture | None:
        if not _TITLE_BACKGROUND_ASSET.exists():
            return None
        try:
            return arcade.load_texture(str(_TITLE_BACKGROUND_ASSET))
        except Exception:
            return None

    def _index_at(self, x: int, y: int) -> int | None:
        for i, (l, b, r, t, _, _k) in enumerate(self._buttons):
            if l <= x <= r and b <= y <= t:
                return i
        return None

    # ── Drawing ─────────────────────────────────────────────────────────────

    def _draw_background(self, w: int, h: int) -> None:
        if self._background_texture is not None:
            arcade.draw_texture_rect(
                self._background_texture, arcade.LBWH(0, 0, w, h)
            )
            arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (0, 0, 0, 48))
        else:
            # Solid dark base
            arcade.draw_lrbt_rectangle_filled(0, w, 0, h, BACKGROUND)

            # Distant city silhouette with animated lit windows
            horizon = int(h * 0.30)
            for i, x in enumerate(range(-60, w + 100, 70)):
                tower_h = horizon + 40 + ((i * 41 + 7) % 140)
                arcade.draw_lrbt_rectangle_filled(
                    x, x + 48, 0, tower_h, SKYLINE_SHADOW
                )
                seed = i * 13 + 3
                for row in range(10, tower_h - 8, 18):
                    for col in range(x + 6, x + 42, 14):
                        if (seed + row + col) % 5 < 2:
                            b = 55 + int(
                                25 * math.sin(self._elapsed * 1.1 + i * 0.4 + row * 0.05)
                            )
                            arcade.draw_lrbt_rectangle_filled(
                                col, col + 8, row, row + 9, (b + 25, b + 18, b, 190)
                            )

            # Horizon glow
            arcade.draw_lrbt_rectangle_filled(0, w, 0, horizon, (4, 2, 6))
            arcade.draw_line(0, horizon, w, horizon, (245, 103, 55, 55), 3)

        # Scanlines
        for y in range(0, h, 5):
            arcade.draw_line(0, y, w, y, SCANLINE, 1)

        # Perspective grid
        horizon = int(h * 0.30)
        for offset in range(-w, w * 2, 90):
            arcade.draw_line(offset, 0, offset + 64, horizon, (22, 84, 112, 35), 1)

        # Side vignette
        vw = int(w * 0.16)
        arcade.draw_lrbt_rectangle_filled(0,     vw,     0, h, (0, 0, 0, 150))
        arcade.draw_lrbt_rectangle_filled(w - vw, w,     0, h, (0, 0, 0, 150))

        # Top / bottom chrome bars
        arcade.draw_lrbt_rectangle_filled(0, w,         0, 40,     PANEL_FILL_DARK)
        arcade.draw_lrbt_rectangle_filled(0, w, h - 40, h,         PANEL_FILL_DARK)
        arcade.draw_line(0, 41,     w, 41,     PANEL_BORDER, 1)
        arcade.draw_line(0, h - 41, w, h - 41, PANEL_BORDER, 1)

    def _draw_title(self, w: int, h: int) -> None:
        cy = int(h * _TITLE_FRAC)
        cx = w // 2

        # Glow behind title
        pulse = 0.6 + 0.4 * math.sin(self._elapsed * 1.8)
        g_alpha = int(28 + 18 * pulse)
        arcade.draw_lrbt_rectangle_filled(
            cx - 500, cx + 500, cy - 12, cy + 76, (247, 171, 69, g_alpha)
        )

        # Main title
        arcade.draw_text(
            "CYBERCITY 2085",
            cx, cy + 32,
            HEADER,
            font_size=64,
            bold=True,
            anchor_x="center", anchor_y="center",
        )

        # Subtitle
        arcade.draw_text(
            "COVERT OPERATIONS COMMAND",
            cx, cy - 12,
            MUTED_TEXT,
            font_size=14,
            anchor_x="center", anchor_y="center",
        )

        # Flanking decorative lines
        for sign in (-1, 1):
            x0 = cx + sign * 370
            x1 = cx + sign * 490
            arcade.draw_line(x0, cy + 32, x1, cy + 32, PANEL_BORDER, 1)
            arcade.draw_line(x1, cy + 32, x1 - sign * 16, cy + 44, ACCENT, 2)

    def _draw_menu(self, _w: int, _h: int) -> None:
        for i, (left, bot, right, top, label, _key) in enumerate(self._buttons):
            self._draw_button(left, bot, right, top, label, i == self._hover_index)

    def _draw_button(
        self, left: int, bot: int, right: int, top: int, label: str, hover: bool
    ) -> None:
        fill = (42, 92, 118, 235) if hover else (8, 20, 24, 200)
        arcade.draw_lrbt_rectangle_filled(left, right, bot, top, fill)

        border = HEADER if hover else PANEL_BORDER
        arcade.draw_line(left, top,  right, top,  border, 3 if hover else 2)
        arcade.draw_line(left, bot,  right, bot,  GRID_LINE, 1)
        arcade.draw_line(left, bot,  left,  top,  GRID_LINE, 1)
        arcade.draw_line(right, bot, right, top,  GRID_LINE, 1)

        # XCOM corner notch
        notch = 14
        arcade.draw_line(left, top, left + notch, top - notch, border, 2)

        cx = (left + right) // 2
        cy = (bot  + top)  // 2
        arcade.draw_text(
            label,
            cx, cy,
            TEXT if hover else MUTED_TEXT,
            font_size=18,
            bold=hover,
            anchor_x="center", anchor_y="center",
        )

        # Active bar on left edge
        if hover:
            pulse = 0.8 + 0.2 * math.sin(self._elapsed * 4.5)
            arcade.draw_lrbt_rectangle_filled(
                left - 8, left - 2, bot + 4, top - 4,
                (*HEADER[:3], int(220 * pulse))
            )

    def _draw_footer(self, w: int, _h: int) -> None:
        arcade.draw_text(
            "v3.0  //  AEGIS CORPORATION  //  CLASSIFIED",
            w // 2, 20,
            MUTED_TEXT, font_size=10,
            anchor_x="center", anchor_y="center",
        )
        arcade.draw_text(
            "ARROW KEYS / MOUSE  ·  ENTER TO SELECT",
            w - 22, 20,
            (50, 80, 95), font_size=10,
            anchor_x="right", anchor_y="center",
        )

    # ── Action dispatch ─────────────────────────────────────────────────────

    def _activate(self, key: str) -> None:
        if key == "quit":
            arcade.exit()
            return

        if key == "new_game":
            from game.ui.screens.new_game_screen import NewGameSetupView
            self.window.show_view(NewGameSetupView())
            return

        if key == "continue":
            from game.gamestate import GameState
            from game.persistence import SaveSystem
            loaded, _result = SaveSystem.load_game(SaveSystem.slot_path(1))
            self._go_management(loaded if loaded is not None else GameState())
            return

        if key == "settings":
            from game.ui.screens.settings_screen import SettingsView
            self.window.show_view(SettingsView())
            return

    def _go_management(self, game_state) -> None:
        from game.ui.screens.management_screen import ManagementView
        view = ManagementView(game_state)
        view.setup()
        self.window.show_view(view)
