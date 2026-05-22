"""Keyboard navigation contract for command UI views."""

import unittest

from game.ui.navigation import build_help_lines, build_hint_banner, build_view_focus_model, keyboard_action_for_focus
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
        model.set_list_counts(mission_count=3, agent_count=2)
        model.current_index = len(model.room_keys)
        mission = model.move(len(model.action_keys) + 1)
        self.assertIsNotNone(mission)
        self.assertEqual(mission.kind, "mission")
        self.assertEqual(mission.key, "mission_1")

    def test_contextual_hints_and_help_overlay_stay_compact(self):
        hint = build_hint_banner("command_center", "executive", has_room_open=True)
        help_lines = build_help_lines("command_center", "executive", ["Advance day", "Fund politics"], has_room_open=True)
        self.assertIn("Tab focus", hint)
        self.assertLessEqual(len(help_lines), 14)
        self.assertTrue(any("Raccourcis actifs" in line for line in help_lines))

    def test_focus_item_maps_to_same_keyboard_activation_intent(self):
        model = build_view_focus_model("command_deck", 1280, 720)
        model.set_actions(["launch"])
        model.set_list_counts(mission_count=1, agent_count=1)
        self.assertEqual(keyboard_action_for_focus(model.active()), "open_room")
        model.current_index = len(model.room_keys)
        self.assertEqual(keyboard_action_for_focus(model.active()), "launch")


if __name__ == "__main__":
    unittest.main()
