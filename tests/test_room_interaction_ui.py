"""Graphical room interaction rules."""

import unittest

from game.ui.room_interaction import (
    RoomUIState,
    UIRect,
    action_at_point,
    actions_for_room,
    close_room,
    layout_roster_card_rects,
    open_room,
    roster_card_at_point,
    room_at_point,
    step_room_ui,
    ROOM_TRANSITION_SECONDS,
)
from game.ui.facility import build_facility_rooms


class RoomInteractionUITest(unittest.TestCase):
    def test_clickable_rooms_open_with_icon_actions(self):
        expected_room = build_facility_rooms(1280, 720, "corp")[0]
        room = room_at_point(
            1280,
            720,
            "corp",
            expected_room.left + expected_room.width // 2,
            expected_room.bottom + expected_room.height // 2,
        )
        state = RoomUIState("corp")

        self.assertIsNotNone(room)
        buttons = open_room(state, 1280, 720, room.key)

        self.assertEqual(state.active_room_key, room.key)
        self.assertGreaterEqual(len(buttons), 1)

    def test_action_buttons_are_hit_testable(self):
        state = RoomUIState("squad")
        buttons = open_room(state, 1280, 720, "ops")
        first = buttons[0]

        action = action_at_point(buttons, first.rect.center_x, first.rect.center_y)

        self.assertEqual(action.key, "next_step")

    def test_room_animation_opens_and_closes_without_text_state(self):
        state = RoomUIState("city")
        open_room(state, 1280, 720, "district")

        step_room_ui(state, 0.25)

        self.assertGreater(state.expansion, 0.0)
        self.assertIn(
            "defense_zones",
            [action.key for action in actions_for_room("city", "district")],
        )
        close_room(state)
        self.assertFalse(state.is_open)


    def test_room_transition_speed_is_harmonized(self):
        self.assertAlmostEqual(ROOM_TRANSITION_SECONDS, 0.28)

    def test_roster_card_rects_are_hit_testable(self):
        state = RoomUIState("squad")
        buttons = open_room(state, 1280, 720, "barracks")
        expanded_rect = UIRect(64, 48, 1152, 638)

        rects = layout_roster_card_rects(expanded_rect, buttons, 3)
        selected_index = roster_card_at_point(
            expanded_rect,
            buttons,
            3,
            rects[1].center_x,
            rects[1].center_y,
        )

        self.assertEqual(selected_index, 1)


if __name__ == "__main__":
    unittest.main()
