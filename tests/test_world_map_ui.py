"""World map mission selection helpers."""

import unittest

from game.mission_templates import MissionTemplate
from game.ui.navigation import active_shortcuts_for_screen
from game.ui.screens.world_map import (
    WORLD_MAP_PATH,
    build_world_map_mission_nodes,
    infer_world_map_site,
    mission_label_text,
    mission_site_name,
)
from game.ui.screens.world_map_view import build_world_map_layout, _compact_briefing_lines


def _mission(title: str, district: str = "Chrome Warrens", objective_text: str = "Test the map flow.") -> MissionTemplate:
    return MissionTemplate(
        id=title.lower().replace(" ", "_"),
        title=title,
        objective_text=objective_text,
        target_faction="Test Faction",
        district=district,
        district_pressure={},
        starting_enemy_count=1,
        risk_level=2,
        fund_reward=40,
        duration_days=1,
    )


class WorldMapUITest(unittest.TestCase):
    def test_world_map_asset_reference_stays_on_the_expected_image(self):
        self.assertEqual(WORLD_MAP_PATH.name, "Player_World_Map_1778155726161.png")
        self.assertTrue(WORLD_MAP_PATH.exists())

    def test_site_inference_uses_explicit_attribute_before_keywords(self):
        mission = _mission("Harbor Echo")
        mission.world_map_site = "Tokyo"

        self.assertEqual(infer_world_map_site(mission), "tokyo")
        self.assertEqual(mission_site_name("new_york"), "NEW YORK")
        self.assertEqual(mission_label_text(mission), "HARBOR ECHO")

    def test_world_map_nodes_stay_within_the_display_area(self):
        missions = [_mission("North Grid"), _mission("East Gate", district="Badlands")]
        missions[0].world_map_site = "new_york"
        missions[1].world_map_site = "tokyo"

        nodes = build_world_map_mission_nodes(missions, 1, 100, 200, 500, 700)

        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[1].site_key, "tokyo")
        self.assertTrue(all(100 <= node.pin_x <= 500 for node in nodes))
        self.assertTrue(all(200 <= node.pin_y <= 700 for node in nodes))
        self.assertTrue(all(node.hit_left <= node.pin_x <= node.hit_right for node in nodes))
        self.assertTrue(all(node.hit_bottom <= node.pin_y <= node.hit_top for node in nodes))

    def test_world_map_layout_keeps_the_map_nearly_full_screen(self):
        right_layout = build_world_map_layout(1280, 720, selected_pin_x=1120)
        left_layout = build_world_map_layout(1280, 720, selected_pin_x=160)

        self.assertGreaterEqual(right_layout.map_right - right_layout.map_left, 1250)
        self.assertGreaterEqual(right_layout.map_top - right_layout.map_bottom, 560)
        self.assertLessEqual(right_layout.briefing_right - right_layout.briefing_left, 420)
        self.assertLess(right_layout.briefing_left, 220)
        self.assertGreater(left_layout.briefing_left, 800)
        self.assertGreater(left_layout.briefing_right, left_layout.briefing_left)

    def test_world_map_briefing_summary_stays_compact(self):
        mission = _mission("Sabotage: Jackal Relay", objective_text="Test the map flow.")
        mission.emotional_impact_hint = {
            "short_text": "High emotional stakes",
            "text": "A very long emotional summary that should not spill across the panel.",
        }

        lines = _compact_briefing_lines(mission)

        self.assertEqual(len(lines), 4)
        self.assertTrue(lines[0].startswith("Risk:"))
        self.assertTrue(all(len(line) <= 80 for line in lines))

    def test_mission_board_shortcuts_mention_map_pins(self):
        shortcuts = active_shortcuts_for_screen("mission_board", has_room_open=False)

        self.assertIn("Select mission", shortcuts)


if __name__ == "__main__":
    unittest.main()
