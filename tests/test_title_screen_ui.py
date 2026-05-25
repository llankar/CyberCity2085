"""Readability regressions for the title screen."""

from __future__ import annotations

import sys
import types
import unittest


captured_draw_text: list[tuple[str, tuple, dict]] = []


def _draw_text(text, *args, **kwargs):
    captured_draw_text.append((text, args, kwargs))


fake_arcade = types.SimpleNamespace(
    View=type("View", (), {"__init__": lambda self, *a, **k: None, "clear": lambda self: None}),
    draw_text=_draw_text,
    draw_lrbt_rectangle_filled=lambda *args, **kwargs: None,
    draw_line=lambda *args, **kwargs: None,
    draw_texture_rect=lambda *args, **kwargs: None,
    set_background_color=lambda *args, **kwargs: None,
    load_texture=lambda *args, **kwargs: None,
    LBWH=lambda *args, **kwargs: None,
    key=types.SimpleNamespace(RETURN=13, ENTER=13, SPACE=32, ESCAPE=27, UP=38, W=87, DOWN=40, S=83),
)
sys.modules["arcade"] = fake_arcade

from game.ui.screens.title_screen import TitleView


class _FakeWindow:
    width = 1280
    height = 720

    def show_view(self, _view):
        pass


class TitleScreenUITest(unittest.TestCase):
    def setUp(self) -> None:
        captured_draw_text.clear()

    def _font_size_for(self, text: str) -> int:
        for drawn_text, args, kwargs in captured_draw_text:
            if drawn_text == text:
                if "font_size" in kwargs:
                    return int(kwargs["font_size"])
                if len(args) >= 5 and isinstance(args[4], int):
                    return int(args[4])
                if len(args) >= 4 and isinstance(args[3], int):
                    return int(args[3])
        raise AssertionError(f"missing draw_text call for {text!r}")

    def test_title_buttons_use_more_readable_label_size(self) -> None:
        view = TitleView()
        view.window = _FakeWindow()

        view.on_draw()

        self.assertGreaterEqual(self._font_size_for("NEW GAME"), 18)
        self.assertGreaterEqual(self._font_size_for("CONTINUE"), 18)
        self.assertGreaterEqual(self._font_size_for("SETTINGS"), 18)
        self.assertGreaterEqual(self._font_size_for("QUIT"), 18)


if __name__ == "__main__":
    unittest.main()
