"""Readability regressions for the tactical battle HUD."""

from __future__ import annotations

import sys
import types
import unittest


captured_draw_text: list[tuple[str, tuple, dict]] = []
captured_rects: list[tuple[float, float, float, float, tuple]] = []


def _draw_text(text, *args, **kwargs):
    captured_draw_text.append((text, args, kwargs))


def _draw_lrbt_rectangle_filled(left, right, bottom, top, color):
    captured_rects.append((float(left), float(right), float(bottom), float(top), color))


fake_arcade = types.SimpleNamespace(
    draw_text=_draw_text,
    draw_lrbt_rectangle_filled=_draw_lrbt_rectangle_filled,
    draw_line=lambda *args, **kwargs: None,
    draw_texture_rect=lambda *args, **kwargs: None,
    draw_rect_outline=lambda *args, **kwargs: None,
    LBWH=lambda *args, **kwargs: None,
    load_texture=lambda *args, **kwargs: None,
)
sys.modules["arcade"] = fake_arcade

from game.ui.screens import battle_hud


class _DummySprite:
    def __init__(self, center_x: int = 128, center_y: int = 128, width: int = 48, height: int = 48):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height


class _DummyStats:
    def __init__(self):
        self.max_hp = 20
        self.defense = 6
        self.agi = 18
        self.str = 14
        self.psi = 12


class _DummyCharacter:
    def __init__(self, name: str, role: str = "samurai"):
        self.name = name
        self.role = role
        self.stress = 37


class _DummyUnit:
    def __init__(self, name: str, role: str = "samurai"):
        self.sprite = _DummySprite()
        self.stats = _DummyStats()
        self.health = 16
        self.action_points = 2
        self.character = _DummyCharacter(name, role)
        self.spec_ops_asset = None
        self.unit_type = "agent"
        self.visible = True
        self.position = (128, 128)


class _DummyTerrainProfile:
    def __init__(self, walkable_cells: set[tuple[int, int]]):
        self.walkable_cells = frozenset(walkable_cells)

    def is_walkable(self, x: int, y: int) -> bool:
        return (x, y) in self.walkable_cells


class BattleHUDUITest(unittest.TestCase):
    def setUp(self) -> None:
        captured_draw_text.clear()
        captured_rects.clear()

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

    def _font_size_for_contains(self, fragment: str) -> int:
        for drawn_text, args, kwargs in captured_draw_text:
            if fragment in str(drawn_text):
                if "font_size" in kwargs:
                    return int(kwargs["font_size"])
                if len(args) >= 5 and isinstance(args[4], int):
                    return int(args[4])
                if len(args) >= 4 and isinstance(args[3], int):
                    return int(args[3])
        raise AssertionError(f"missing draw_text call containing {fragment!r}")

    def test_battle_hud_uses_larger_readable_labels(self) -> None:
        player = _DummyUnit("Agent 1", "sniper")
        target = _DummyUnit("Target 1", "psi")

        battle_hud.draw_unit_status_panel(1280, 720, player, "player")
        battle_hud.draw_target_lock_panel(1280, target, "shoot", player)
        battle_hud.draw_mission_status_bar(1280, 720, "Extraction: Neon Witness [JOUR 32]", 3, 2, 1)
        battle_hud.draw_resource_summary(
            1280,
            720,
            {"credits": 12, "intel": 3, "salvage": 5, "influence": 7},
            available_funds=2500,
        )
        battle_hud.draw_action_bar(1280, ["move", "shoot", "end turn"], "shoot", 0.0)

        self.assertGreaterEqual(self._font_size_for("HP"), 9)
        self.assertGreaterEqual(self._font_size_for("STRESS  37%"), 9)
        self.assertGreaterEqual(self._font_size_for_contains("TARGET LOCK"), 10)
        self.assertGreaterEqual(self._font_size_for("HIT  75%"), 13)
        self.assertGreaterEqual(self._font_size_for("EXTRACTION: NEON WITNESS [JOUR 32]"), 13)
        self.assertGreaterEqual(self._font_size_for("MOVE"), 11)
        self.assertGreaterEqual(self._font_size_for("DEF  6"), 9)
        self.assertGreaterEqual(self._font_size_for("RESOURCES"), 10)
        self.assertGreaterEqual(self._font_size_for_contains("FUNDS"), 12)
        self.assertGreaterEqual(self._font_size_for("CREDITS 12  |  INTEL 3  |  SALVAGE 5  |  INFLUENCE 7"), 11)

    def test_unit_status_panel_docks_to_the_bottom_left(self) -> None:
        player = _DummyUnit("Agent 1", "sniper")

        battle_hud.draw_unit_status_panel(1280, 720, player, "player")

        status_panels = [
            rect
            for rect in captured_rects
            if rect[0] == 12.0 and rect[1] == 332.0 and rect[3] - rect[2] == 90.0
        ]
        self.assertTrue(status_panels, "expected the active-unit panel at the bottom-left edge")
        self.assertEqual(status_panels[0][2], 12.0)

    def test_movement_range_marks_blocked_tiles_with_debug_color(self) -> None:
        player = _DummyUnit("Agent 1", "sniper")

        battle_hud.draw_movement_range(
            player,
            320,
            320,
            can_enter=lambda x, y: (x, y) != (160, 128),
        )

        blocked = [
            rect
            for rect in captured_rects
            if rect[0] == 160.0 and rect[1] == 192.0 and rect[2] == 128.0 and rect[3] == 160.0
        ]
        walkable = [
            rect
            for rect in captured_rects
            if rect[0] == 128.0 and rect[1] == 160.0 and rect[2] == 128.0 and rect[3] == 160.0
        ]
        path_blocked = [
            rect
            for rect in captured_rects
            if rect[0] == 192.0 and rect[1] == 224.0 and rect[2] == 128.0 and rect[3] == 160.0
        ]
        self.assertTrue(blocked, "expected the blocked tile to be drawn for debugging")
        self.assertEqual(blocked[0][4], battle_hud._MOVE_BLOCKED_COL)
        self.assertTrue(walkable, "expected adjacent walkable tiles to retain the normal color")
        self.assertEqual(walkable[0][4], battle_hud._MOVE_COL)
        self.assertTrue(path_blocked, "expected tiles behind a blocked route to be marked as blocked")
        self.assertEqual(path_blocked[0][4], battle_hud._MOVE_BLOCKED_COL)

    def test_path_blocking_overlay_covers_the_whole_map(self) -> None:
        player = _DummyUnit("Agent 1", "sniper")
        enemy = _DummyUnit("Enemy 1", "grunt")
        player.position = (32, 32)
        enemy.position = (64, 64)
        profile = _DummyTerrainProfile({(32, 32), (64, 64)})

        battle_hud.draw_path_blocking_overlay(profile, [player], [enemy], 128, 128)

        far_blocked = [
            rect
            for rect in captured_rects
            if rect[0] == 96.0 and rect[1] == 128.0 and rect[2] == 96.0 and rect[3] == 128.0
        ]
        occupied = [
            rect
            for rect in captured_rects
            if rect[0] == 32.0 and rect[1] == 64.0 and rect[2] == 32.0 and rect[3] == 64.0
        ]
        self.assertTrue(far_blocked, "expected blocked tiles across the map, not only near agents")
        self.assertEqual(far_blocked[0][4], battle_hud._PATH_BLOCK_TERRAIN_COL)
        self.assertTrue(occupied, "expected occupied tiles to be highlighted on the full map")
        self.assertEqual(occupied[0][4], battle_hud._PATH_BLOCK_OCCUPIED_COL)

    def test_shortcut_banner_centers_the_help_text(self) -> None:
        battle_hud.draw_battle_shortcut_banner(
            1280,
            720,
            "Raccourcis actifs: Fl\u00e8ches d\u00e9placer | E objectif",
        )

        text_calls = [call for call in captured_draw_text if "Raccourcis actifs:" in str(call[0])]
        self.assertTrue(text_calls, "expected the shortcut banner to render text")
        text_x = float(text_calls[0][1][0])
        self.assertAlmostEqual(text_x, 640.0, delta=25.0)
        self.assertGreaterEqual(self._font_size_for_contains("Raccourcis actifs:"), 12)
        banner = captured_rects[0]
        self.assertGreaterEqual(banner[3], 684.0)

    def test_aftermath_line_centers_and_docks_to_the_top(self) -> None:
        battle_hud.draw_action_aftermath_line(1280, 720, "MOVE | DMG 0")

        text_calls = [call for call in captured_draw_text if call[0] == "MOVE | DMG 0"]
        self.assertTrue(text_calls, "expected the aftermath line to render text")
        text_x = float(text_calls[0][1][0])
        self.assertAlmostEqual(text_x, 640.0, delta=25.0)
        self.assertGreaterEqual(self._font_size_for("MOVE | DMG 0"), 12)
        banner = captured_rects[0]
        self.assertGreaterEqual(banner[3], 656.0)

    def test_contextual_shortcut_banner_switches_with_input_mode(self) -> None:
        keyboard = battle_hud.battle_shortcut_banner("keyboard_mouse", False, False)
        controller = battle_hud.battle_shortcut_banner("controller", False, False)
        self.assertIn("Fl\u00e8ches d\u00e9placer", keyboard)
        self.assertIn("LS d\u00e9placer", controller)

    def test_contextual_shortcut_banner_prioritizes_end_turn_confirmation(self) -> None:
        confirm = battle_hud.battle_shortcut_banner("keyboard_mouse", True, True)
        self.assertIn("confirmer fin de tour", confirm.lower())

    def test_overwatch_preview_cells_build_forward_line_and_cone(self) -> None:
        player = _DummyUnit("Agent 1", "sniper")
        triggers, coverage = battle_hud.overwatch_preview_cells(
            player,
            (1, 0),
            640,
            480,
            reach_cells=3,
        )
        self.assertEqual(triggers, [(160, 128), (192, 128), (224, 128)])
        self.assertIn((160, 96), coverage)
        self.assertIn((224, 160), coverage)


if __name__ == "__main__":
    unittest.main()
