"""UI accessibility states and non-chromatic markers."""

import unittest

from game.gamestate import GameState
from game.ui.accessibility.states import ClickableStates, label_with_non_color_indicator
from game.ui.mission_board import build_mission_board_lines
from game.ui.palette import accessibility_palette


class AccessibilityStatesTest(unittest.TestCase):
    def test_palette_exposes_high_contrast_and_default_modes(self):
        standard = accessibility_palette(False)
        high = accessibility_palette(True)

        self.assertNotEqual(standard.background, high.background)
        self.assertEqual(high.background, (0, 0, 0))
        self.assertEqual(high.text, (255, 255, 255))

    def test_clickable_states_cover_expected_interaction_states(self):
        for state in ("normal", "hover", "active", "disabled", "focus"):
            self.assertIn(state, ClickableStates)

    def test_non_color_label_prefix_is_added(self):
        label = label_with_non_color_indicator("Launch mission", "active")
        self.assertTrue(label.startswith("[A]"))
        self.assertIn("◆", label)

    def test_mission_board_lines_include_focus_marker_on_selected_line(self):
        gs = GameState()
        lines = build_mission_board_lines(gs.mission_templates, gs.selected_mission_index)
        self.assertTrue(any(line.startswith("[F]") for line in lines))

    def test_gamestate_exposes_central_high_contrast_flag(self):
        gs = GameState()
        self.assertFalse(gs.ui_high_contrast)


if __name__ == "__main__":
    unittest.main()
