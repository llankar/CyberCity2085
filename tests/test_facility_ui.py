"""Corporate tower backdrop presentation rules."""

import unittest
from pathlib import Path

from PIL import Image

from game.ui.facility import (
    BASE_BACKDROP_ASSET,
    BASE_BACKDROP_SIZE,
    ROOM_IMAGE_DIR,
    build_facility_rooms,
    facility_room_by_key,
)
from game.ui.portraits import AGENT_PORTRAIT_COUNT, PORTRAIT_DIR, ROBOT_PORTRAIT_COUNT
from game.ui.portraits import LEGACY_AGENT_PORTRAIT_COUNT


class FacilityUITest(unittest.TestCase):
    def test_corporate_backdrop_builds_stacked_base_rooms(self):
        rooms = build_facility_rooms(1280, 720, "corp")

        self.assertEqual(len(rooms), 8)
        self.assertEqual(rooms[0].key, "executive")
        self.assertEqual(rooms[0].title, "Executive War Room")
        self.assertGreater(facility_room_by_key(rooms, "hangar").left, rooms[0].left)

    def test_city_and_squad_modes_use_city_corporate_language(self):
        city_rooms = build_facility_rooms(1280, 720, "city")
        squad_rooms = build_facility_rooms(1280, 720, "squad")

        self.assertEqual(
            facility_room_by_key(city_rooms, "municipal").title,
            "Municipal Control",
        )
        self.assertEqual(
            facility_room_by_key(squad_rooms, "barracks").title,
            "Agent Barracks",
        )

    def test_hub_mode_exposes_the_six_room_tower_layout(self):
        hub_rooms = build_facility_rooms(1280, 720, "hub")

        self.assertEqual([room.key for room in hub_rooms], [
            "command",
            "city",
            "squad",
            "assets",
            "research",
            "intel",
        ])
        self.assertEqual(facility_room_by_key(hub_rooms, "command").title, "Command Core")
        self.assertLess(facility_room_by_key(hub_rooms, "command").left, facility_room_by_key(hub_rooms, "city").left)
        self.assertLess(facility_room_by_key(hub_rooms, "squad").bottom, facility_room_by_key(hub_rooms, "command").bottom)
        self.assertGreater(facility_room_by_key(hub_rooms, "research").bottom, int(720 * 0.32))
        self.assertGreater(facility_room_by_key(hub_rooms, "intel").bottom, int(720 * 0.32))

    def test_rooms_stay_inside_visible_command_area(self):
        rooms = build_facility_rooms(900, 600, "battle")

        for room in rooms:
            self.assertGreaterEqual(room.left, 0)
            self.assertGreaterEqual(room.bottom, 0)
            self.assertLessEqual(room.left + room.width, 900)
            self.assertLessEqual(room.bottom + room.height, 600)

    def test_graphical_backdrop_asset_is_project_bound(self):
        asset = Path(BASE_BACKDROP_ASSET)

        self.assertTrue(asset.exists())
        self.assertGreater(asset.stat().st_size, 500_000)

    def test_each_backdrop_room_has_a_crop_asset(self):
        rooms = build_facility_rooms(*BASE_BACKDROP_SIZE, mode="corp")

        self.assertEqual(len({room.image_path for room in rooms}), 8)
        for room in rooms:
            asset = Path(room.image_path)
            self.assertTrue(asset.exists(), room.image_path)
            self.assertGreater(asset.stat().st_size, 50_000)
            self.assertEqual(asset.parent.as_posix(), ROOM_IMAGE_DIR)

    def test_lower_hub_crops_stay_aligned_to_the_room_rects(self):
        rooms = build_facility_rooms(*BASE_BACKDROP_SIZE, mode="hub")
        research = facility_room_by_key(rooms, "research")
        intel = facility_room_by_key(rooms, "intel")

        with Image.open(Path(research.image_path)) as img:
            self.assertEqual(img.size, (research.width + 20, research.height + 20))
        with Image.open(Path(intel.image_path)) as img:
            self.assertEqual(img.size, (intel.width + 20, intel.height + 20))

    def test_hit_zones_are_aligned_to_generated_image_rooms(self):
        width, height = BASE_BACKDROP_SIZE
        rooms = build_facility_rooms(width, height, "corp")
        executive = facility_room_by_key(rooms, "executive")
        hangar = facility_room_by_key(rooms, "hangar")
        server = facility_room_by_key(rooms, "server")

        self.assertLess(executive.left, width * 0.25)
        self.assertGreater(hangar.left, width * 0.50)
        self.assertLess(server.bottom, height * 0.08)

    def test_generated_agent_portrait_set_is_project_bound(self):
        portrait_dir = Path(PORTRAIT_DIR)
        legacy_portraits = sorted(portrait_dir.glob("agent_[0-9][0-9].png"))
        female_portraits = sorted(portrait_dir.glob("agent_female_*.png"))
        male_portraits = sorted(portrait_dir.glob("agent_male_*.png"))
        robot_portraits = sorted(portrait_dir.glob("robot_[0-9][0-9].png"))

        self.assertEqual(len(legacy_portraits), LEGACY_AGENT_PORTRAIT_COUNT)
        self.assertEqual(len(female_portraits), AGENT_PORTRAIT_COUNT)
        self.assertEqual(len(male_portraits), AGENT_PORTRAIT_COUNT)
        self.assertEqual(len(robot_portraits), ROBOT_PORTRAIT_COUNT)
        self.assertTrue((portrait_dir / "portrait_sheet.png").exists())
        for portrait in legacy_portraits + female_portraits + male_portraits + robot_portraits:
            self.assertGreater(portrait.stat().st_size, 50_000)


if __name__ == "__main__":
    unittest.main()
