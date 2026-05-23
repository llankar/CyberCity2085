"""CyberCity 2085 — New Game Setup Screen.

Lets the player name their corporation and city before the campaign
begins.  Pure arcade draw calls, no UIManager required.
"""

from __future__ import annotations

import math
import string

import arcade

from game.ui.palette import (
    AMBER_BORDER, AMBER_FILL, BACKGROUND, DANGER,
    GRID_LINE, HEADER, MUTED_TEXT, PANEL_BORDER,
    SCANLINE, SKYLINE_SHADOW, TACTICAL_GREEN, TEXT,
)

# ── Constants ────────────────────────────────────────────────────────────────

_MAX_LEN   = 28
_ALLOWED   = set(string.ascii_letters + string.digits + " -_.'()&")

_FIELD_W   = 480
_FIELD_H   = 52
_LABEL_H   = 24

_DIFF_LABELS = [
    ("ROOKIE",   "Easy — agents rarely die",         palette_key := "tactical_green"),
    ("VETERAN",  "Normal — authentic XCOM tension",  "warning"),
    ("LEGEND",   "Hard — every decision is final",   "danger"),
]

# ── Helpers ──────────────────────────────────────────────────────────────────

def _rect(l, b, r, t, color):
    arcade.draw_lrbt_rectangle_filled(l, r, b, t, color)


def _field_bounds(cx: int, cy: int):
    return cx - _FIELD_W // 2, cy - _FIELD_H // 2, cx + _FIELD_W // 2, cy + _FIELD_H // 2


# ── View ─────────────────────────────────────────────────────────────────────

class NewGameSetupView(arcade.View):
    """Corp name / city name / difficulty setup before a new campaign."""

    def __init__(self) -> None:
        super().__init__()
        self._corp = "AEGIS Corporation"
        self._city = "Neo-Chrome City"
        self._focus  = 0          # 0 = corp, 1 = city
        self._diff   = 1          # 0 = rookie, 1 = veteran, 2 = legend
        self._elapsed = 0.0
        self._hover_start: str | None = None

        # Hit rects filled in on_draw
        self._hit_corp:  tuple | None = None
        self._hit_city:  tuple | None = None
        self._hit_diffs: list[tuple] = []
        self._hit_start: tuple | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_show_view(self) -> None:
        arcade.set_background_color(BACKGROUND)

    def on_update(self, dt: float) -> None:
        self._elapsed += dt

    def on_draw(self) -> None:
        self.clear()
        w, h = self.window.width, self.window.height
        self._draw_background(w, h)
        self._draw_form(w, h)

    # ── Input ─────────────────────────────────────────────────────────────────

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.TAB:
            self._focus = 1 - self._focus
            return
        if key == arcade.key.ESCAPE:
            from game.ui.screens.title_screen import TitleView
            self.window.show_view(TitleView())
            return
        if key in (arcade.key.RETURN, arcade.key.ENTER):
            if self._focus < 1:
                self._focus += 1
            else:
                self._start_game()
            return
        if key == arcade.key.BACKSPACE:
            if self._focus == 0:
                self._corp = self._corp[:-1]
            else:
                self._city = self._city[:-1]
            return
        # Printable character
        char = _key_to_char(key, modifiers)
        if char and char in _ALLOWED:
            if self._focus == 0 and len(self._corp) < _MAX_LEN:
                self._corp += char
            elif self._focus == 1 and len(self._city) < _MAX_LEN:
                self._city += char

    def on_mouse_press(self, x: float, y: float, _button: int, _mods: int) -> None:
        xi, yi = int(x), int(y)
        if self._hit_corp and _in(*self._hit_corp, xi, yi):
            self._focus = 0; return
        if self._hit_city and _in(*self._hit_city, xi, yi):
            self._focus = 1; return
        for i, bounds in enumerate(self._hit_diffs):
            if _in(*bounds, xi, yi):
                self._diff = i; return
        if self._hit_start and _in(*self._hit_start, xi, yi):
            self._start_game()

    def on_mouse_motion(self, x: float, y: float, *_) -> None:
        xi, yi = int(x), int(y)
        self._hover_start = (
            "start" if (self._hit_start and _in(*self._hit_start, xi, yi)) else None
        )

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw_background(self, w: int, h: int) -> None:
        _rect(0, 0, w, h, BACKGROUND)
        horizon = int(h * 0.28)
        for i, x in enumerate(range(-60, w + 100, 70)):
            tower_h = horizon + 38 + ((i * 41 + 7) % 140)
            _rect(x, 0, x + 48, tower_h, SKYLINE_SHADOW)
        _rect(0, 0, w, horizon, (4, 2, 6))
        arcade.draw_line(0, horizon, w, horizon, (245, 103, 55, 50), 3)
        for y in range(0, h, 5):
            arcade.draw_line(0, y, w, y, SCANLINE, 1)
        for offset in range(-w, w * 2, 90):
            arcade.draw_line(offset, 0, offset + 64, horizon, (22, 84, 112, 30), 1)

    def _draw_form(self, w: int, h: int) -> None:
        cx = w // 2
        form_top = int(h * 0.82)

        # Title
        arcade.draw_text(
            "NEW CAMPAIGN SETUP",
            cx, form_top,
            HEADER, font_size=28, bold=True,
            anchor_x="center", anchor_y="center",
        )
        arcade.draw_text(
            "Name your corporation and city before deployment",
            cx, form_top - 34,
            MUTED_TEXT, font_size=12,
            anchor_x="center", anchor_y="center",
        )
        # Decorative line
        arcade.draw_line(cx - 300, form_top - 50, cx + 300, form_top - 50, PANEL_BORDER, 1)

        fy = form_top - 90

        # Corp name field
        cy_corp = fy
        self._hit_corp = _field_bounds(cx, cy_corp)
        self._draw_text_field(
            "CORPORATION NAME", self._corp,
            cx, cy_corp, focused=(self._focus == 0),
        )
        fy -= _FIELD_H + _LABEL_H + 24

        # City name field
        cy_city = fy
        self._hit_city = _field_bounds(cx, cy_city)
        self._draw_text_field(
            "CITY NAME", self._city,
            cx, cy_city, focused=(self._focus == 1),
        )
        fy -= _FIELD_H + _LABEL_H + 36

        # Difficulty
        arcade.draw_text(
            "DIFFICULTY",
            cx - _FIELD_W // 2, fy + _LABEL_H // 2,
            MUTED_TEXT, font_size=10, bold=True,
        )
        fy -= 4
        diff_w = _FIELD_W // 3 - 8
        self._hit_diffs = []
        for i, (dlabel, ddesc, _col_key) in enumerate(_DIFF_LABELS):
            bx = cx - _FIELD_W // 2 + i * (diff_w + 12)
            by = fy - 40
            sel = (i == self._diff)
            diff_col = (
                TACTICAL_GREEN if _DIFF_LABELS[i][2] == "tactical_green" else
                (arcade.color.YELLOW if _DIFF_LABELS[i][2] == "warning" else DANGER)
            )
            fill = (*diff_col[:3], 60) if sel else (8, 20, 26, 200)
            _rect(bx, by, bx + diff_w, fy, fill)
            arcade.draw_line(bx, fy, bx + diff_w, fy, diff_col if sel else GRID_LINE, 2)
            arcade.draw_text(
                dlabel, bx + diff_w // 2, fy - 14,
                diff_col if sel else MUTED_TEXT,
                font_size=12, bold=sel,
                anchor_x="center", anchor_y="center",
            )
            arcade.draw_text(
                ddesc, bx + diff_w // 2, by + 10,
                diff_col if sel else (40, 65, 80),
                font_size=8,
                anchor_x="center", anchor_y="center",
            )
            self._hit_diffs.append((bx, by, bx + diff_w, fy))

        fy -= 60

        # Start button
        bw, bh = 320, 54
        bl = cx - bw // 2
        bb = fy - bh
        hover = (self._hover_start == "start")
        fill = (22, 58, 28, 230) if hover else (10, 34, 16, 220)
        _rect(bl, bb, bl + bw, bb + bh, fill)
        arcade.draw_line(bl, bb + bh, bl + bw, bb + bh,
                         TACTICAL_GREEN, 3 if hover else 2)
        arcade.draw_line(bl, bb,      bl + bw, bb,      TACTICAL_GREEN, 1)
        col_pulse = int(200 + 55 * math.sin(self._elapsed * 2.5)) if hover else 180
        arcade.draw_text(
            "▶  START CAMPAIGN",
            cx, bb + bh // 2,
            (*TACTICAL_GREEN[:3], col_pulse),
            font_size=16, bold=True,
            anchor_x="center", anchor_y="center",
        )
        notch = 14
        arcade.draw_line(bl, bb + bh, bl + notch, bb + bh - notch, TACTICAL_GREEN, 2)
        self._hit_start = (bl, bb, bl + bw, bb + bh)

        # ESC hint
        arcade.draw_text(
            "TAB to switch field  ·  ENTER to confirm  ·  ESC to go back",
            cx, bb - 20,
            (40, 65, 80), font_size=10,
            anchor_x="center", anchor_y="center",
        )

    def _draw_text_field(
        self,
        label: str,
        text: str,
        cx: int,
        cy: int,
        focused: bool,
    ) -> None:
        l, b, r, t = _field_bounds(cx, cy)
        border_col = AMBER_BORDER if focused else PANEL_BORDER
        fill = (*AMBER_FILL[:3], 180) if focused else (8, 18, 24, 200)
        _rect(l, b, r, t, fill)
        arcade.draw_line(l, t, r, t, border_col, 2)
        arcade.draw_line(l, b, r, b, GRID_LINE,   1)
        arcade.draw_line(l, b, l, t, GRID_LINE,   1)
        arcade.draw_line(r, b, r, t, GRID_LINE,   1)
        # Label above
        arcade.draw_text(
            label,
            l, t + 6,
            MUTED_TEXT if not focused else HEADER, font_size=10, bold=focused,
        )
        # Value with cursor
        cursor = "_" if focused and int(self._elapsed * 2) % 2 == 0 else ""
        arcade.draw_text(
            text + cursor,
            l + 16, cy,
            TEXT if focused else MUTED_TEXT,
            font_size=18,
            anchor_y="center",
        )

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _start_game(self) -> None:
        from game.gamestate import GameState
        from game.ui.screens.management_screen import ManagementView

        corp = self._corp.strip() or "AEGIS Corporation"
        city = self._city.strip() or "Neo-Chrome City"

        gs = GameState()
        gs.corp_name  = corp
        gs.city_name  = city
        gs.base_name  = f"{corp} · Forward Base Kilo"

        # Difficulty modifiers (light touch — no new systems)
        if self._diff == 0:    # Rookie
            gs.funds.current_funds += 200
        elif self._diff == 2:  # Legend
            gs.funds.current_funds = max(10, gs.funds.current_funds - 100)

        view = ManagementView(gs)
        view.setup()
        self.window.show_view(view)


# ── Utility ───────────────────────────────────────────────────────────────────

def _in(l: int, b: int, r: int, t: int, x: int, y: int) -> bool:
    return l <= x <= r and b <= y <= t


_KEY_SHIFT_MAP = {
    arcade.key.KEY_1: "!",  arcade.key.KEY_2: "@",  arcade.key.KEY_3: "#",
    arcade.key.KEY_4: "$",  arcade.key.KEY_5: "%",  arcade.key.KEY_6: "^",
    arcade.key.KEY_7: "&",  arcade.key.KEY_8: "*",  arcade.key.KEY_9: "(",
    arcade.key.KEY_0: ")",  arcade.key.MINUS: "_",  arcade.key.EQUAL: "+",
    arcade.key.APOSTROPHE: '"',  arcade.key.PERIOD: ">",
}


def _key_to_char(key: int, modifiers: int) -> str | None:
    shifted = bool(modifiers & arcade.key.MOD_SHIFT)
    if arcade.key.A <= key <= arcade.key.Z:
        c = chr(key)
        return c.upper() if shifted else c.lower()
    if key == arcade.key.SPACE:
        return " "
    if shifted and key in _KEY_SHIFT_MAP:
        return _KEY_SHIFT_MAP[key]
    if arcade.key.KEY_0 <= key <= arcade.key.KEY_9:
        return chr(key - arcade.key.KEY_0 + ord("0"))
    if key == arcade.key.MINUS:
        return "-"
    if key == arcade.key.PERIOD:
        return "."
    if key == arcade.key.APOSTROPHE:
        return "'"
    return None


