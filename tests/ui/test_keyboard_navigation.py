"""Keyboard navigation contract for command UI views."""

import unittest

from game.ui.navigation import build_help_lines, build_hint_banner, build_view_focus_model
from game.ui.room_interaction import RoomUIState, open_room


class KeyboardNavigationTest(unittest.TestCase):
    def test_common_focus_model_cycles_rooms(self):
        model = build_view_focus_model("squad", 1280, 720)
        first = model.active()
        self.assertIsNotNone(first)
        self.assertEqual(first.kind, "room")
        wrapped = None
        for _ in range(len(model.room_keys)):
            wrapped = model.move(1)
        self.assertIsNotNone(wrapped)
        self.assertEqual(wrapped.kind, "room")

    def test_room_actions_are_focusable_for_keyboard_parity(self):
        state = RoomUIState("squad")
        buttons = open_room(state, 1280, 720, "ops")
        model = build_view_focus_model("squad", 1280, 720)
        model.set_actions([button.action.key for button in buttons])
        active_action = None
        for _ in range(len(model.room_keys) + 1):
            active_action = model.move(1)
            if active_action and active_action.kind == "action":
                break
        self.assertIsNotNone(active_action)
        self.assertEqual(active_action.kind, "action")
        self.assertIn(active_action.key, {button.action.key for button in buttons})

    def test_mission_selection_is_part_of_shared_tab_order(self):
        model = build_view_focus_model("squad", 1280, 720)
        model.mission_count = 3
        model.current_index = len(model.room_keys)
        mission = model.move(len(model.action_keys) + 1)
        self.assertIsNotNone(mission)
        self.assertEqual(mission.kind, "mission")
        self.assertEqual(mission.key, "mission_1")

    def test_contextual_hints_and_help_overlay_stay_compact(self):
        hint = build_hint_banner("corp", "executive")
        help_lines = build_help_lines("corp", "executive", ["Advance day", "Fund politics"])
        self.assertIn("Tab focus", hint)
        self.assertLessEqual(len(help_lines), 12)
        self.assertTrue(any("Raccourcis contextuels" in line for line in help_lines))


if __name__ == "__main__":
    unittest.main()
