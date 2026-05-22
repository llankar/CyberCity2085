"""Command-center presentation rules for the city/corporate UI shell."""

import unittest

from game.gamestate import GameState
from game.ui.command_center import (
    build_action_strip,
    build_command_center_layout,
    build_command_title,
    panel_by_key,
)
from game.ui.dashboard import build_command_status_line
from game.ui.action_feedback import action_message
from game.ui.widgets.notification_center import NotificationCenter


class CommandCenterUITest(unittest.TestCase):
    def test_management_layout_keeps_war_room_and_city_feed_readable(self):
        panels = build_command_center_layout(1280, 720, "corp")

        self.assertEqual(
            [panel.key for panel in panels], ["primary", "top_right", "bottom_right"]
        )
        self.assertLess(
            panel_by_key(panels, "primary").left, panel_by_key(panels, "top_right").left
        )
        self.assertEqual(
            panel_by_key(panels, "top_right").left,
            panel_by_key(panels, "bottom_right").left,
        )
        self.assertIn("Executive Command Floor", panel_by_key(panels, "primary").title)

    def test_city_mode_uses_city_control_language(self):
        panels = build_command_center_layout(1280, 720, "city")

        self.assertIn("Municipal Control Floor", panel_by_key(panels, "primary").title)
        self.assertIn("District Pressure Deck", panel_by_key(panels, "top_right").title)

    def test_command_title_and_action_strip_feel_like_tactical_console(self):
        title = build_command_title("city", "Ghost Tower", "Chrome Warrens")
        strip = build_action_strip(["7-9 invest", "R squad deck"])

        self.assertEqual(
            title, "CITY CONTROL TOWER // GHOST TOWER // CHROME WARRENS"
        )
        self.assertEqual(strip, "7-9 invest  >  R squad deck")

    def test_dashboard_status_line_shows_available_funds(self):
        game_state = GameState()
        line = build_command_status_line(
            game_state.turn,
            game_state.base_name,
            game_state.strategic_resources,
            game_state.district,
            game_state.available_funds,
        )

        self.assertIn(f"FUNDS {game_state.available_funds}", line)
        self.assertIn("DISTRICT PRESSURE", line)


if __name__ == "__main__":
    unittest.main()


class NotificationCenterUITest(unittest.TestCase):
    def test_notification_center_keeps_standardized_action_feedback(self):
        center = NotificationCenter(max_items=2)
        level, text = action_message("save", True, "slot A")
        center.push(level, text)
        center.failure("Mission launch failure: no deployable agents")
        self.assertIn("[FAILURE] Mission launch failure", center.latest_text_lines(2)[0])
        self.assertIn("[SUCCESS] Action: Save", center.latest_text_lines(2)[1])
