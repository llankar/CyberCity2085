import tempfile
import unittest
from pathlib import Path

from game.character import Character
from game.gamestate import GameState
from game.persistence import SaveSystem


class SaveSystemTests(unittest.TestCase):
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
        self.assertEqual(len(loaded.characters), 1)


if __name__ == "__main__":
    unittest.main()
