"""Mission board generation keeps daily flavor while staying deterministic."""

import unittest

from game.gamestate import GameState
from game.mission_system import ensure_mission_templates


class MissionGenerationTest(unittest.TestCase):
    def test_daily_generation_creates_day_tagged_board(self):
        game_state = GameState(mission_templates=[])

        ensure_mission_templates(game_state)

        self.assertEqual(game_state.mission_board_generated_day, game_state.calendar.current_day)
        self.assertTrue(game_state.mission_templates)
        self.assertTrue(all(f"Day {game_state.calendar.current_day}" in m.title for m in game_state.mission_templates))

    def test_same_day_generation_is_stable(self):
        game_state = GameState(mission_templates=[])

        ensure_mission_templates(game_state)
        first_ids = [m.id for m in game_state.mission_templates]
        ensure_mission_templates(game_state)
        second_ids = [m.id for m in game_state.mission_templates]

        self.assertEqual(first_ids, second_ids)

    def test_next_day_regenerates_board(self):
        game_state = GameState(mission_templates=[])

        ensure_mission_templates(game_state)
        day_one_ids = [m.id for m in game_state.mission_templates]

        game_state.advance_one_day("test")
        ensure_mission_templates(game_state)
        day_two_ids = [m.id for m in game_state.mission_templates]

        self.assertNotEqual(day_one_ids, day_two_ids)


if __name__ == "__main__":
    unittest.main()
