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

    def test_mission_board_shortcuts_mention_map_pins(self):
        shortcuts = active_shortcuts_for_screen("mission_board", has_room_open=False)

        self.assertIn("Select mission", shortcuts)


if __name__ == "__main__":
    unittest.main()
