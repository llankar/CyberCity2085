"""Strategic resource economy rules."""

import tempfile
import unittest
from pathlib import Path

from game.gamestate import GameState
from game.mission_templates import MissionTemplate


def _mission(risk_level=3, objective_type="data_theft"):
    return MissionTemplate(
        id="resource_test",
        title="Resource Test",
        objective_text="Extract leverage.",
        target_faction="Test Faction",
        district="Test District",
        district_pressure={},
        starting_enemy_count=2,
        objective_type=objective_type,
        risk_level=risk_level,
    )


class StrategicResourcesTest(unittest.TestCase):
    def test_new_game_state_has_resource_defaults(self):
        game_state = GameState()

        self.assertEqual(
            game_state.strategic_resources,
            {"credits": 0, "intel": 0, "salvage": 0, "influence": 0},
        )

    def test_resource_save_load_roundtrip(self):
        game_state = GameState()
        game_state.strategic_resources.update(
            {"credits": 25, "intel": 4, "salvage": 2, "influence": 1}
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "savegame.json"
            game_state.save(str(save_path))

            loaded = GameState.load(str(save_path))

        self.assertEqual(loaded.strategic_resources["credits"], 25)
        self.assertEqual(loaded.strategic_resources["intel"], 4)
        self.assertEqual(loaded.strategic_resources["salvage"], 2)
        self.assertEqual(loaded.strategic_resources["influence"], 1)

    def test_successful_mission_victory_awards_resources_and_logs(self):
        game_state = GameState()

        rewards = game_state.award_mission_resources(
            _mission(risk_level=3, objective_type="data_theft"), True, defeated=2
        )

        self.assertGreaterEqual(rewards["credits"], 20)
        self.assertGreaterEqual(rewards["intel"], 2)
        self.assertGreaterEqual(rewards["salvage"], 1)
        self.assertGreaterEqual(rewards["influence"], 1)
        self.assertIn("Extraction secured:", game_state.event_log[-1])

    def test_spending_fails_safely_when_resources_are_insufficient(self):
        game_state = GameState()
        game_state.strategic_resources["intel"] = 2

        self.assertFalse(game_state.spend_resource("intel", 5))
        self.assertEqual(game_state.strategic_resources["intel"], 2)
        self.assertFalse(game_state.spend_resources({"credits": 1, "intel": 1}))
        self.assertEqual(game_state.strategic_resources["intel"], 2)


if __name__ == "__main__":
    unittest.main()
