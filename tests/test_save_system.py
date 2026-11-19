import json
import tempfile
import unittest
from pathlib import Path

from game.character import Character
from game.gamestate import GameState
from game.persistence import SaveSystem
from game.management.spec_ops_assets import ArmorRating, CombatRobot


class SaveSystemTests(unittest.TestCase):
    def test_release_state_roundtrip_preserves_campaign_scars_assets_and_board(self):
        agent = Character(name="Nyx", role="samurai")
        agent.temporary_scars = [{"id": "burn", "label": "Neon Burn", "days_left": 3}]
        agent.reputation = ["Pulled a civilian from the fire"]
        robot = CombatRobot(id="hound", name="Hound", armor=ArmorRating(plating=2))
        game_state = GameState(
            characters=[agent],
            selected_agent_names=["Nyx"],
            spec_ops_assets=[robot],
            selected_asset_ids=["hound"],
        )
        game_state.campaign.current_act = 3
        game_state.campaign.discovered_intel = ["pharmacorp_trial_7"]
        game_state.mission_board_generated_day = 17
        original_tag_names = [tag.name for tag in game_state.factions[0].active_tags]

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "release.json"
            SaveSystem.save_game(game_state, path)
            loaded, result = SaveSystem.load_game(path)

        self.assertTrue(result.ok)
        assert loaded is not None
        self.assertEqual(loaded.campaign.current_act, 3)
        self.assertEqual(loaded.campaign.discovered_intel, ["pharmacorp_trial_7"])
        self.assertEqual(loaded.characters[0].temporary_scars[0]["label"], "Neon Burn")
        self.assertEqual(loaded.selected_asset_ids, ["hound"])
        self.assertEqual(loaded.mission_board_generated_day, 17)
        self.assertEqual(
            [tag.name for tag in loaded.factions[0].active_tags], original_tag_names
        )
        self.assertEqual(len(loaded.mission_templates), len(game_state.mission_templates))

    def test_legacy_payload_missing_release_fields_loads_safe_defaults(self):
        game_state = GameState(characters=[Character(name="Legacy", role="sniper")])
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "legacy.json"
            game_state.save(str(path))
            data = json.loads(path.read_text(encoding="utf-8"))
            for key in (
                "campaign",
                "selected_asset_ids",
                "mission_board_generated_day",
                "tutorial_progress",
                "weekly_directive_week",
                "weekly_directive_id",
            ):
                data.pop(key, None)
            data["characters"][0].pop("temporary_scars", None)
            for faction in data["factions"]:
                faction.pop("active_tags", None)
            path.write_text(json.dumps(data), encoding="utf-8")

            loaded, result = SaveSystem.load_game(path)

        self.assertTrue(result.ok)
        assert loaded is not None
        self.assertEqual(loaded.campaign.current_act, 1)
        self.assertEqual(loaded.characters[0].temporary_scars, [])
        self.assertEqual(loaded.selected_asset_ids, [])
        self.assertEqual(loaded.mission_board_generated_day, loaded.calendar.current_day)

    def test_slot_path_returns_expected_file(self):
        self.assertEqual(SaveSystem.slot_path(1), Path("saves/slot_1.json"))
        self.assertEqual(SaveSystem.slot_path(5), Path("saves/slot_5.json"))

    def test_slot_path_rejects_out_of_range_slot(self):
        with self.assertRaises(ValueError):
            SaveSystem.slot_path(0)

    def test_load_missing_file_returns_clear_result(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.json"
            loaded, result = SaveSystem.load_game(missing)

        self.assertIsNone(loaded)
        self.assertFalse(result.ok)
        self.assertIn("No save file", result.message)

    def test_full_campaign_roundtrip_preserves_core_progress(self):
        game_state = GameState()
        game_state.characters.append(Character(name="Nyx", role="samurai"))
        game_state.advance_days(2, reason="save test")
        game_state.selected_agent_names = ["Nyx"]
        game_state.strategic_resources["credits"] = 55
        game_state.city_budget["armaments"] = 20
        game_state.combat_mission_ui_engine = "godot"
        game_state.characters[0].mentor_links = {
            "Cipher": {"agent_id": "Cipher", "bond_level": 4, "strategic_day": 12}
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "slot_a" / "campaign.json"
            save_result = SaveSystem.save_game(game_state, save_path)
            loaded, load_result = SaveSystem.load_game(save_path)

        self.assertTrue(save_result.ok)
        self.assertTrue(load_result.ok)
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.calendar.current_day, game_state.calendar.current_day)
        self.assertEqual(loaded.selected_agent_names, ["Nyx"])
        self.assertEqual(loaded.strategic_resources["credits"], 55)
        self.assertEqual(loaded.city_budget["armaments"], 20)
        self.assertEqual(loaded.combat_mission_ui_engine, "godot")
        self.assertEqual(len(loaded.characters), 1)
        self.assertEqual(
            loaded.characters[0].mentor_links,
            {"Cipher": {"agent_id": "Cipher", "bond_level": 4, "strategic_day": 12}},
        )

    def test_loading_placeholder_names_normalizes_to_codename_agents(self):
        game_state = GameState()
        game_state.characters.extend(
            [
                Character(name="Agent 1", role="samurai"),
                Character(name="Agent 2", role="sniper"),
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "slot_a" / "campaign.json"
            SaveSystem.save_game(game_state, save_path)
            loaded, load_result = SaveSystem.load_game(save_path)

        self.assertTrue(load_result.ok)
        assert loaded is not None
        self.assertNotIn("Agent 1", [character.name for character in loaded.characters])
        self.assertNotIn("Agent 2", [character.name for character in loaded.characters])


if __name__ == "__main__":
    unittest.main()
