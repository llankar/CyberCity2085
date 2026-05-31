from __future__ import annotations

import unittest
from types import SimpleNamespace
from pathlib import Path

from game import battle_maps


class BattleMapsTest(unittest.TestCase):
    def test_catalog_has_fifty_city_maps_and_split_pools(self) -> None:
        catalog = battle_maps.build_battle_map_catalog()

        self.assertEqual(len(catalog), len(battle_maps.CITY_BATTLE_MAPS) + len(battle_maps.WASTELAND_BATTLE_MAPS))
        self.assertEqual(len(battle_maps.CITY_BATTLE_MAPS), 50)
        self.assertTrue(battle_maps.WASTELAND_BATTLE_MAPS)
        self.assertTrue(all(entry.filename.startswith("city_") for entry in battle_maps.CITY_BATTLE_MAPS))
        self.assertTrue(all(not entry.filename.startswith("city_") for entry in battle_maps.WASTELAND_BATTLE_MAPS))

    def test_infers_city_and_wasteland_missions(self) -> None:
        city_mission = SimpleNamespace(
            id="city_relay",
            title="Relay Shutdown",
            district="Chrome Warrens",
            target_faction="Aegis Dynamics",
            objective_text="Disable the relay node in the city core",
            objective_type="sabotage",
            enemy_theme="corp_samurai",
            tags=[SimpleNamespace(name="story")],
        )
        wasteland_mission = SimpleNamespace(
            id="badlands_scout",
            title="Badlands Survey",
            district="Badlands Fringe",
            target_faction="Hungry Packs",
            objective_text="Recover the drone core from the wasteland",
            objective_type="extract",
            enemy_theme="starver",
            tags=[SimpleNamespace(name="badlands")],
        )

        self.assertEqual(battle_maps.infer_battle_environment(city_mission), "city")
        self.assertEqual(battle_maps.infer_battle_environment(wasteland_mission), "wasteland")

        city_pool = battle_maps.battle_map_pool_for_mission(city_mission)
        wasteland_pool = battle_maps.battle_map_pool_for_mission(wasteland_mission)

        self.assertTrue(all(entry.environment == "city" for entry in city_pool))
        self.assertTrue(all(entry.environment == "wasteland" for entry in wasteland_pool))

        selected_city = battle_maps.select_battle_map_entry(city_mission)
        selected_wasteland = battle_maps.select_battle_map_entry(wasteland_mission)

        self.assertIsNotNone(selected_city)
        self.assertIsNotNone(selected_wasteland)
        self.assertEqual(selected_city.environment, "city")
        self.assertEqual(selected_wasteland.environment, "wasteland")

    def test_battle_token_scale_is_one_point_five(self) -> None:
        self.assertEqual(battle_maps.BATTLE_TOKEN_SCALE, 1.5)

    def test_new_map_assets_exist_on_disk(self) -> None:
        city_files = [path for path in Path("assets/maps").iterdir() if path.is_file() and path.name.startswith("city_")]
        self.assertEqual(len(city_files), 50)
        self.assertTrue(all(path.suffix.lower() == ".png" for path in city_files))


if __name__ == "__main__":
    unittest.main()
