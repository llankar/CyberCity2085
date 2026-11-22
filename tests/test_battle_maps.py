from __future__ import annotations

import unittest
from types import SimpleNamespace
from pathlib import Path

from game import battle_maps


class BattleMapsTest(unittest.TestCase):
    def test_diagnostic_previews_are_not_playable_maps(self) -> None:
        self.assertFalse(any(entry.filename.startswith("preview_") for entry in battle_maps.build_battle_map_catalog()))

    def test_catalog_has_city_maps_and_split_pools(self) -> None:
        catalog = battle_maps.build_battle_map_catalog()

        self.assertEqual(len(catalog), len(battle_maps.CITY_BATTLE_MAPS) + len(battle_maps.WASTELAND_BATTLE_MAPS))
        self.assertEqual(len(battle_maps.CITY_BATTLE_MAPS), 77)
        self.assertEqual(len(battle_maps.WASTELAND_BATTLE_MAPS), 45)
        self.assertTrue(battle_maps.WASTELAND_BATTLE_MAPS)
        self.assertTrue(all(entry.filename.startswith(("city_", "cybercity_")) for entry in battle_maps.CITY_BATTLE_MAPS))
        self.assertTrue(all(not entry.filename.startswith(("city_", "cybercity_")) for entry in battle_maps.WASTELAND_BATTLE_MAPS))

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
        self.assertTrue(Path(selected_city.path).name.startswith(("city_", "cybercity_")))
        self.assertFalse(Path(selected_wasteland.path).name.startswith(("city_", "cybercity_")))

    def test_battle_tokens_are_ten_percent_larger(self) -> None:
        self.assertAlmostEqual(battle_maps.BATTLE_TOKEN_SCALE, 1.65)

    def test_non_robot_battle_tokens_use_half_scale(self) -> None:
        human_unit = SimpleNamespace(unit_type="agent")
        robot_asset_unit = SimpleNamespace(
            unit_type="power_armor",
            spec_ops_asset=SimpleNamespace(asset_type="power_armor"),
        )
        robot_enemy_unit = SimpleNamespace(unit_type="enemy", enemy_theme="corp_37_robot")

        self.assertAlmostEqual(battle_maps.battle_token_scale_for_unit(human_unit), 0.825)
        self.assertAlmostEqual(battle_maps.battle_token_scale_for_unit(robot_asset_unit), 0.825)
        self.assertAlmostEqual(battle_maps.battle_token_scale_for_unit(robot_enemy_unit), 1.65)

    def test_every_map_has_one_shared_unit_scale_ratio(self) -> None:
        ratios = battle_maps._load_map_height_ratios()
        units = [
            SimpleNamespace(unit_type="agent"),
            SimpleNamespace(unit_type="enemy"),
            SimpleNamespace(unit_type="power_armor"),
            SimpleNamespace(unit_type="vehicle"),
            SimpleNamespace(unit_type="enemy", enemy_theme="corp_37_robot"),
        ]

        self.assertEqual(set(ratios), {entry.filename for entry in battle_maps.BATTLE_MAP_CATALOG})
        self.assertEqual(len(ratios), 122)
        self.assertTrue(all(0.015 <= ratio <= 0.020 for ratio in ratios.values()))
        for entry in battle_maps.BATTLE_MAP_CATALOG:
            map_scale = ratios[entry.filename] / battle_maps.BASE_HUMAN_HEIGHT_RATIO
            self.assertAlmostEqual(battle_maps.battle_map_unit_scale(entry), map_scale)
            for width in (1280, 1920, 2560):
                resolution_scale = width / battle_maps.BASE_PRESENTATION_WIDTH
                for unit in units:
                    intrinsic = battle_maps.battle_token_scale_for_unit(unit)
                    self.assertAlmostEqual(
                        battle_maps.battle_token_scale_for_unit(unit, entry, width),
                        intrinsic * map_scale * resolution_scale,
                    )

    def test_interior_map_ratio_multiplies_all_unit_categories_equally(self) -> None:
        interior = next(
            entry
            for entry in battle_maps.BATTLE_MAP_CATALOG
            if entry.filename == "city_interior_safehouse.png"
        )
        exterior = next(
            entry
            for entry in battle_maps.BATTLE_MAP_CATALOG
            if entry.filename == "city_exterior_rooftop_access.png"
        )
        human = SimpleNamespace(unit_type="agent")
        robot = SimpleNamespace(unit_type="enemy", enemy_theme="corp_37_robot")

        self.assertAlmostEqual(battle_maps.battle_map_unit_scale(exterior), 1.0)
        self.assertAlmostEqual(battle_maps.battle_map_unit_scale(interior), 4 / 3)
        self.assertAlmostEqual(
            battle_maps.battle_token_scale_for_unit(human, interior)
            / battle_maps.battle_token_scale_for_unit(human, exterior),
            4 / 3,
        )
        self.assertAlmostEqual(
            battle_maps.battle_token_scale_for_unit(robot, interior)
            / battle_maps.battle_token_scale_for_unit(robot, exterior),
            4 / 3,
        )

    def test_new_map_assets_exist_on_disk(self) -> None:
        city_files = [path for path in Path("assets/maps").iterdir() if path.is_file() and path.name.startswith("city_") and path.suffix.lower() == ".png"]
        self.assertEqual(len(city_files), 36)
        self.assertTrue(all(path.suffix.lower() == ".png" for path in city_files))


if __name__ == "__main__":
    unittest.main()
