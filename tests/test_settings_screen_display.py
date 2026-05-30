"""Display-selection regressions for the settings screen."""

from __future__ import annotations

import json
import sys
import tempfile
import types
import unittest
from pathlib import Path


class _FakeView:
    def __init__(self, *args, **kwargs):
        self.window = None

    def clear(self):
        pass


class _FakeScreen:
    def __init__(self, x: int, y: int, width: int, height: int, name: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._name = name

    def get_monitor_name(self):
        return self._name

    def get_device_name(self):
        return self._name


captured_draw_text: list[str] = []
captured_draw_text_calls: list[tuple[str, int | None]] = []


def _capture_draw_text(text, *args, **kwargs):
    font_size = kwargs.get("font_size")
    if font_size is None and len(args) >= 5:
        font_size = args[4]
    captured_draw_text.append(str(text))
    captured_draw_text_calls.append((str(text), int(font_size) if font_size is not None else None))


fake_arcade = types.SimpleNamespace(
    View=_FakeView,
    key=types.SimpleNamespace(ESCAPE=27),
    draw_text=_capture_draw_text,
    draw_lrbt_rectangle_filled=lambda *args, **kwargs: None,
    draw_line=lambda *args, **kwargs: None,
    set_background_color=lambda *args, **kwargs: None,
    get_screens=lambda: [
        _FakeScreen(0, 0, 1920, 1080, "Primary"),
        _FakeScreen(1920, 0, 2560, 1440, "Studio"),
    ],
)
sys.modules["arcade"] = fake_arcade

from game.ui.screens import settings_screen


class _FakeWindow:
    def __init__(self):
        self.width = 1280
        self.height = 720
        self.calls: list[tuple[str, tuple, dict]] = []

    def set_fullscreen(self, *args, **kwargs):
        self.calls.append(("set_fullscreen", args, kwargs))

    def set_size(self, *args, **kwargs):
        self.calls.append(("set_size", args, kwargs))

    def set_location(self, *args, **kwargs):
        self.calls.append(("set_location", args, kwargs))

    def show_view(self, view):
        self.calls.append(("show_view", (view,), {}))


class SettingsScreenDisplayTest(unittest.TestCase):
    def setUp(self) -> None:
        captured_draw_text.clear()
        captured_draw_text_calls.clear()
        self._tmpdir = tempfile.TemporaryDirectory()
        self._old_cwd = Path.cwd()
        self._old_settings_path = settings_screen._SETTINGS_PATH
        Path(self._tmpdir.name, "saves").mkdir(parents=True, exist_ok=True)
        settings_screen._SETTINGS_PATH = str(Path(self._tmpdir.name, "saves", "settings.json"))
        settings_screen.save_settings(settings_screen.SettingsState())

    def tearDown(self) -> None:
        settings_screen.save_settings(settings_screen.SettingsState())
        settings_screen._SETTINGS_PATH = self._old_settings_path
        self._tmpdir.cleanup()

    def test_settings_round_trip_includes_display_index_and_text_size(self) -> None:
        state = settings_screen.SettingsState(display_index=1, resolution_index=2, text_size="large")
        settings_screen.save_settings(state)

        with open(settings_screen._SETTINGS_PATH, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        self.assertEqual(raw["display_index"], 1)
        self.assertEqual(raw["text_size"], "large")

        loaded = settings_screen.load_settings()
        self.assertEqual(loaded.display_index, 1)
        self.assertEqual(loaded.resolution_index, 2)
        self.assertEqual(loaded.text_size, "large")

    def test_settings_panel_exposes_display_and_text_size_selectors(self) -> None:
        view = settings_screen.SettingsView()
        view.window = _FakeWindow()
        view.on_draw()

        self.assertTrue(any(action == "screen_prev" for *_hit, action in view._hits))
        self.assertTrue(any(action == "screen_next" for *_hit, action in view._hits))
        self.assertTrue(any(action == "text_prev" for *_hit, action in view._hits))
        self.assertTrue(any(action == "text_next" for *_hit, action in view._hits))
        self.assertTrue(any("Display Screen" in text for text in captured_draw_text))
        self.assertTrue(any("Text Size" in text for text in captured_draw_text))

    def test_apply_uses_selected_screen(self) -> None:
        view = settings_screen.SettingsView()
        view.window = _FakeWindow()
        view._settings.display_index = 1
        view._settings.resolution_index = 0
        view._settings.fullscreen = False

        view._apply_and_save()

        self.assertTrue(Path(settings_screen._SETTINGS_PATH).exists())
        self.assertIn(("set_fullscreen", (False,), {}), view.window.calls)
        self.assertIn(("set_size", (1280, 720), {}), view.window.calls)
        self.assertIn(("set_location", (2560, 360), {}), view.window.calls)

    def test_apply_fullscreen_targets_selected_screen(self) -> None:
        view = settings_screen.SettingsView()
        view.window = _FakeWindow()
        view._settings.display_index = 1
        view._settings.fullscreen = True

        view._apply_and_save()

        fullscreen_calls = [call for call in view.window.calls if call[0] == "set_fullscreen"]
        self.assertTrue(fullscreen_calls)
        self.assertEqual(fullscreen_calls[-1][2].get("screen").get_monitor_name(), "Studio")

    def test_text_size_scales_title_font(self) -> None:
        settings_screen.save_settings(settings_screen.SettingsState(text_size="medium"))
        medium_view = settings_screen.SettingsView()
        medium_view.window = _FakeWindow()
        medium_view.on_draw()
        medium_title = next(font for text, font in captured_draw_text_calls if text == "SYSTEM SETTINGS")

        captured_draw_text.clear()
        captured_draw_text_calls.clear()

        settings_screen.save_settings(settings_screen.SettingsState(text_size="large"))
        large_view = settings_screen.SettingsView()
        large_view.window = _FakeWindow()
        large_view.on_draw()
        large_title = next(font for text, font in captured_draw_text_calls if text == "SYSTEM SETTINGS")

        self.assertIsNotNone(medium_title)
        self.assertIsNotNone(large_title)
        self.assertGreater(large_title, medium_title)


if __name__ == "__main__":
    unittest.main()
