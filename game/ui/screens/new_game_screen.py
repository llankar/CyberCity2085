"""CyberCity 2085 — New Game Setup Screen.

Lets the player name their corporation and city before the campaign
begins.  Pure arcade draw calls, no UIManager required.
"""

from __future__ import annotations

import string

import arcade

from game.ui.new_game_options import DIFFICULTY_LABELS

from game.ui.palette import BACKGROUND

# ── Constants ────────────────────────────────────────────────────────────────

_MAX_LEN = 28
_ALLOWED = set(string.ascii_letters + string.digits + " -_.'()&")


_DIFF_LABELS = DIFFICULTY_LABELS

# ── Helpers ──────────────────────────────────────────────────────────────────


# ── View ─────────────────────────────────────────────────────────────────────


class NewGameSetupView(arcade.View):
    """Corp name / city name / difficulty setup before a new campaign."""

    def __init__(self) -> None:
        super().__init__()
        self._corp = "AEGIS Corporation"
        self._city = "Neo-Chrome City"
        self._focus = 0  # 0 = corp, 1 = city
        self._diff = 1  # 0 = rookie, 1 = veteran, 2 = legend
        self._elapsed = 0.0
        self._hover_start: str | None = None

        # Hit rects filled in on_draw
        self._hit_corp: tuple | None = None
        self._hit_city: tuple | None = None
        self._hit_diffs: list[tuple] = []
        self._hit_start: tuple | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_show_view(self) -> None:
        arcade.set_background_color(BACKGROUND)

    def on_update(self, dt: float) -> None:
        self._elapsed += dt
        if hasattr(self, "_visual_deck"):
            self._visual_deck.update(dt)

    def on_draw(self) -> None:
        self.clear()
        if not hasattr(self, "_visual_deck"):
            from game.ui.components.utilities.new_game import NewGameDeck

            self._visual_deck = NewGameDeck()
        self._visual_deck.hover = ("start", None) if self._hover_start else None
        self._visual_deck.draw(self)

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
            self._focus = 0
            return
        if self._hit_city and _in(*self._hit_city, xi, yi):
            self._focus = 1
            return
        for i, bounds in enumerate(self._hit_diffs):
            if _in(*bounds, xi, yi):
                self._diff = i
                return
        if self._hit_start and _in(*self._hit_start, xi, yi):
            self._start_game()

    def on_mouse_motion(self, x: float, y: float, *_) -> None:
        if hasattr(self, "_visual_deck"):
            self._visual_deck.motion(x, y)
        xi, yi = int(x), int(y)
        self._hover_start = (
            "start" if (self._hit_start and _in(*self._hit_start, xi, yi)) else None
        )

    # ── Drawing ───────────────────────────────────────────────────────────────

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _start_game(self) -> None:
        from game.gamestate import GameState
        from game.ui.screens.management_screen import ManagementView

        corp = self._corp.strip() or "AEGIS Corporation"
        city = self._city.strip() or "Neo-Chrome City"

        gs = GameState()
        gs.corp_name = corp
        gs.city_name = city
        gs.base_name = f"{corp} · Forward Base Kilo"

        # Difficulty modifiers (light touch — no new systems)
        if self._diff == 0:  # Rookie
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
    arcade.key.KEY_1: "!",
    arcade.key.KEY_2: "@",
    arcade.key.KEY_3: "#",
    arcade.key.KEY_4: "$",
    arcade.key.KEY_5: "%",
    arcade.key.KEY_6: "^",
    arcade.key.KEY_7: "&",
    arcade.key.KEY_8: "*",
    arcade.key.KEY_9: "(",
    arcade.key.KEY_0: ")",
    arcade.key.MINUS: "_",
    arcade.key.EQUAL: "+",
    arcade.key.APOSTROPHE: '"',
    arcade.key.PERIOD: ">",
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
