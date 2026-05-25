"""Readability regressions for the tactical battle HUD."""

from __future__ import annotations

import sys
import types
import unittest


captured_draw_text: list[tuple[str, tuple, dict]] = []


def _draw_text(text, *args, **kwargs):
    captured_draw_text.append((text, args, kwargs))


fake_arcade = types.SimpleNamespace(
    draw_text=_draw_text,
    draw_lrbt_rectangle_filled=lambda *args, **kwargs: None,
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


class BattleHUDUITest(unittest.TestCase):
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
        self.assertGreaterEqual(self._font_size_for("◉  TARGET LOCK"), 10)
        self.assertGreaterEqual(self._font_size_for("HIT  75%"), 13)
        self.assertGreaterEqual(self._font_size_for("EXTRACTION: NEON WITNESS [JOUR 32]"), 13)
        self.assertGreaterEqual(self._font_size_for("MOVE"), 11)
        self.assertGreaterEqual(self._font_size_for("DEF  6"), 9)
        self.assertGreaterEqual(self._font_size_for("RESOURCES"), 10)
        self.assertGreaterEqual(self._font_size_for("FUNDS  ¥ 2,500"), 12)
        self.assertGreaterEqual(self._font_size_for("CREDITS 12  |  INTEL 3  |  SALVAGE 5  |  INFLUENCE 7"), 11)


if __name__ == "__main__":
    unittest.main()
