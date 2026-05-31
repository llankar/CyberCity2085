"""Context hints overlay contract for command UI views."""

import unittest

from game.ui.navigation import active_shortcuts_for_screen, build_help_lines, build_hint_banner


class ContextHintsTest(unittest.TestCase):
    def test_overlay_is_dynamic_per_view(self):
        center = build_hint_banner("command_center", "executive", has_room_open=False)
        deck = build_hint_banner("command_deck", "ops", has_room_open=True)
        self.assertNotEqual(center, deck)
        self.assertIn("Esc", deck)

    def test_active_shortcuts_include_room_close_only_when_open(self):
        closed = active_shortcuts_for_screen("command_deck", has_room_open=False)
        opened = active_shortcuts_for_screen("command_deck", has_room_open=True)
        self.assertFalse(any("Esc" in shortcut for shortcut in closed))
        self.assertTrue(any("Esc" in shortcut for shortcut in opened))

    def test_help_lines_stay_compact_and_contextual(self):
        lines = build_help_lines("mission_board", "ops", ["mission_prev", "mission_next"], has_room_open=True)
        self.assertLessEqual(len(lines), 14)
        self.assertTrue(any("Active shortcuts" in line for line in lines))


if __name__ == "__main__":
    unittest.main()
