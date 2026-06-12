import unittest
from collections import defaultdict

import arcade

from game.ui.screens import battle_hud


captured_draw_text = []
captured_rects = []


def _draw_text(text, *args, **kwargs):
    captured_draw_text.append((text, args, kwargs))


def _draw_lrbt_rectangle_filled(left, right, bottom, top, color):
    captured_rects.append((float(left), float(right), float(bottom), float(top), color))


def _draw_line(*args, **kwargs):
    return None


class _DummyUnit:
    def __init__(self, name, subtype="grunt"):
        self.name = name
        self.subtype = subtype
        self.position = (0, 0)
        self.action_points = 1


class BattleHUDUITest(unittest.TestCase):
    def setUp(self) -> None:
        captured_draw_text.clear()
        captured_rects.clear()
        self._orig_draw_text = arcade.draw_text
        self._orig_rect = arcade.draw_lrbt_rectangle_filled
        self._orig_line = arcade.draw_line
        arcade.draw_text = _draw_text
        arcade.draw_lrbt_rectangle_filled = _draw_lrbt_rectangle_filled
        arcade.draw_line = _draw_line

    def tearDown(self) -> None:
        arcade.draw_text = self._orig_draw_text
        arcade.draw_lrbt_rectangle_filled = self._orig_rect
        arcade.draw_line = self._orig_line

    def _font_size_for_contains(self, needle: str) -> int:
        for text, args, kwargs in captured_draw_text:
            if needle in str(text):
                return int(kwargs.get("font_size", args[3] if len(args) > 3 else 0))
        raise AssertionError(f"Could not find text containing {needle!r}")

    def test_shortcut_banner_centers_the_help_text(self):
        battle_hud.draw_battle_shortcut_banner(
            1280,
            720,
            "Active shortcuts: Arrow keys move | E objective",
        )

        text_calls = [call for call in captured_draw_text if "Active shortcuts:" in str(call[0])]
        self.assertTrue(text_calls, "expected the shortcut banner to render text")
        text_x = float(text_calls[0][1][0])
        self.assertAlmostEqual(text_x, 640.0, delta=25.0)
        self.assertGreaterEqual(self._font_size_for_contains("Active shortcuts:"), 12)
        banner = captured_rects[0]
        self.assertGreaterEqual(banner[3], 684.0)

    def test_aftermath_line_centers_and_docks_to_the_top(self) -> None:
        battle_hud.draw_action_aftermath_line(1280, 720, "MOVE | DMG 0")

        text_calls = [call for call in captured_draw_text if call[0] == "MOVE | DMG 0"]
        self.assertTrue(text_calls, "expected the aftermath line to render text")
        text_x = float(text_calls[0][1][0])
        self.assertAlmostEqual(text_x, 640.0, delta=25.0)
        self.assertGreaterEqual(self._font_size_for_contains("MOVE | DMG 0"), 12)
        banner = captured_rects[0]
        self.assertGreaterEqual(banner[3], 656.0)

    def test_contextual_shortcut_banner_switches_with_input_mode(self) -> None:
        keyboard = battle_hud.battle_shortcut_banner("keyboard_mouse", False, False)
        controller = battle_hud.battle_shortcut_banner("controller", False, False)
        self.assertIn("Arrow keys move", keyboard)
        self.assertIn("LS move", controller)

    def test_contextual_shortcut_banner_prioritizes_end_turn_confirmation(self) -> None:
        confirm = battle_hud.battle_shortcut_banner("keyboard_mouse", True, True)
        self.assertIn("confirm end turn", confirm.lower())

    def test_overwatch_preview_cells_build_forward_line_and_cone(self) -> None:
        player = _DummyUnit("Agent 1", "sniper")
        player.position = (4, 4)
        triggers, coverage = battle_hud.overwatch_preview_cells(
            player,
            (1, 0),
            640,
            480,
            reach_cells=3,
        )
        self.assertEqual(triggers, [(36, 4), (68, 4), (100, 4)])
        self.assertIn((36, 36), coverage)
        self.assertIn((100, 100), coverage)

    def test_movement_range_draws_half_size_cells(self) -> None:
        unit = _DummyUnit("Agent 1")
        unit.position = (32, 32)

        battle_hud.draw_movement_range(unit, 96, 96)

        self.assertEqual(len(captured_rects), 5)
        for left, right, bottom, top, _color in captured_rects:
            self.assertAlmostEqual(right - left, 16.0)
            self.assertAlmostEqual(top - bottom, 16.0)
            self.assertAlmostEqual(left % 32.0, 8.0)
            self.assertAlmostEqual(bottom % 32.0, 8.0)


if __name__ == "__main__":
    unittest.main()
