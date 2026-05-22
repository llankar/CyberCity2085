import unittest

from game.character import Character
from game.gamestate import GameState
from game.management.stress import daily_stress_recovery


class StressManagementTests(unittest.TestCase):
    def test_daily_stress_recovery_relieves_active_agents_slowly(self):
        agent = Character(name="Echo", stress=12)

        result = daily_stress_recovery(agent)

        self.assertTrue(result.changed)
        self.assertEqual(result.amount, 1)
        self.assertEqual(agent.stress, 11)

    def test_daily_stress_recovery_relieves_recovering_agents_faster(self):
        agent = Character(name="Mender", stress=12, recovery_turns=2)

        result = daily_stress_recovery(agent)

        self.assertTrue(result.changed)
        self.assertEqual(result.amount, 2)
        self.assertEqual(agent.stress, 10)

    def test_advance_day_applies_stress_recovery_and_logs_event(self):
        game_state = GameState(
            characters=[
                Character(name="Ghost", stress=8),
                Character(name="Stitch", stress=9, recovery_turns=1),
            ]
        )

        game_state.advance_one_day("stress recovery test")

        self.assertEqual(game_state.characters[0].stress, 7)
        self.assertEqual(game_state.characters[1].stress, 7)
        self.assertTrue(
            any("Ghost decompresses (1 stress relief, 7/100)." in entry for entry in game_state.event_log)
        )
        self.assertTrue(
            any("Stitch decompresses (2 stress relief, 7/100)." in entry for entry in game_state.event_log)
        )


if __name__ == "__main__":
    unittest.main()
