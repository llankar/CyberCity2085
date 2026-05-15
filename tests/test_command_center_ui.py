"""Command-center presentation rules for the city/corporate UI shell."""

import unittest

from game.ui.command_center import (
    build_action_strip,
    build_command_center_layout,
    build_command_title,
    panel_by_key,
)


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
        self.assertIn("Corporate War Room", panel_by_key(panels, "primary").title)

    def test_city_mode_uses_city_control_language(self):
        panels = build_command_center_layout(1280, 720, "city")

        self.assertIn("City Situation Room", panel_by_key(panels, "primary").title)
        self.assertIn("District Pressure", panel_by_key(panels, "top_right").title)

    def test_command_title_and_action_strip_feel_like_tactical_console(self):
        title = build_command_title("city", "Ghost Tower", "Chrome Warrens")
        strip = build_action_strip(["7-9 invest", "R squad deck"])

        self.assertEqual(title, "CITY CONTROL // GHOST TOWER // CHROME WARRENS")
        self.assertEqual(strip, "7-9 invest  ▸  R squad deck")


if __name__ == "__main__":
    unittest.main()
