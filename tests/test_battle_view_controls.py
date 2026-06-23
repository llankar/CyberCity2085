"""Focused BattleView keyboard control regressions."""

import unittest

from game import views


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


if __name__ == "__main__":
    unittest.main()
