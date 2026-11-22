"""Focused BattleView keyboard control regressions."""

import unittest
from types import SimpleNamespace

from game import views
from game import battle_maps


class _Player:
    pass


class BattleViewControlsTest(unittest.TestCase):
    def _view(self):
        view = views.BattleView.__new__(views.BattleView)
        view.map_index = 0
        view._paused = False
        view._show_combat_log = False
        view._deploying = False
        view.turn = "player"
        view.player_units = [_Player()]
        view.active_index = 0
        view.selecting_target = False
        view.selecting_overwatch_orientation = False
        view.pending_end_turn_confirmation = False
        return view

    def test_tab_toggles_combat_log_side_panel_state(self):
        view = self._view()

        view.on_key_press(views.arcade.key.TAB, 0)
        self.assertTrue(view._show_combat_log)

        view.on_key_press(views.arcade.key.TAB, 0)
        self.assertFalse(view._show_combat_log)

    def test_escape_opens_and_closes_pause_overlay(self):
        view = self._view()

        view.on_key_press(views.arcade.key.ESCAPE, 0)
        self.assertTrue(view._paused)

        view.on_key_press(views.arcade.key.ESCAPE, 0)
        self.assertFalse(view._paused)

    def test_map_change_reapplies_one_ratio_to_every_existing_sprite(self):
        view = self._view()
        view.active_map_entry = next(
            entry
            for entry in battle_maps.BATTLE_MAP_CATALOG
            if entry.filename == "city_interior_safehouse.png"
        )
        human = SimpleNamespace(unit_type="agent", sprite=SimpleNamespace(scale=0.0))
        robot = SimpleNamespace(
            unit_type="enemy",
            enemy_theme="corp_37_robot",
            sprite=SimpleNamespace(scale=0.0),
        )
        view.player_units = [human]
        view.enemy_units = [robot]
        view.defeated_player_units = []

        view._apply_active_map_unit_scale()

        self.assertAlmostEqual(human.sprite.scale, 1.1)
        self.assertAlmostEqual(robot.sprite.scale, 2.2)


if __name__ == "__main__":
    unittest.main()
