"""Tests for compact post-mission faction narrative rewards."""

import tempfile
import unittest
from pathlib import Path

from game.gamestate import GameState
from game.mission_system import apply_faction_narrative_rewards
from game.mission_templates import MissionTemplate


def _mission(target_faction: str = "Warrens Free Clinic") -> MissionTemplate:
    return MissionTemplate(
        id="faction-reward-test",
        title="Quiet Circuit",
        objective_text="Secure a relay alley.",
        target_faction=target_faction,
        district="Chrome Warrens",
        district_pressure={},
        starting_enemy_count=2,
        risk_level=2,
    )


class FactionRewardsTest(unittest.TestCase):
    def test_assignment_matches_faction_mapping(self):
        game_state = GameState()

        entries = apply_faction_narrative_rewards(
            game_state, _mission("Warrens Free Clinic"), victory=True
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["kind"], "local_trust")
        self.assertTrue(game_state.faction_reward_journal)

    def test_no_assignment_on_total_failure(self):
        game_state = GameState()

        entries = apply_faction_narrative_rewards(
            game_state, _mission("Warrens Free Clinic"), victory=False
        )

        self.assertEqual(entries, [])
        self.assertEqual(game_state.faction_reward_journal, [])

    def test_journal_persists_through_save_load(self):
        game_state = GameState()
        apply_faction_narrative_rewards(game_state, _mission("Unknown Faction"), victory=True)

        with tempfile.TemporaryDirectory() as tmp_dir:
            save_path = Path(tmp_dir) / "savegame.json"
            game_state.save(str(save_path))
            loaded = GameState.load(str(save_path))

        self.assertEqual(len(loaded.faction_reward_journal), 1)
        self.assertEqual(loaded.faction_reward_journal[0]["kind"], "neutral_echo")


if __name__ == "__main__":
    unittest.main()
