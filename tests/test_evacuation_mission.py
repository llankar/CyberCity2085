import unittest

from game.gamestate import GameState
from game.mission_generation import generate_mission_board
from game.missions.evacuation import (
    create_evacuation_template,
    evacuation_briefing_fields,
    evacuation_constraints,
    evaluate_evacuation_outcome,
)


class EvacuationMissionTest(unittest.TestCase):
    def test_evacuation_can_appear_in_generation_under_pressure(self):
        game_state = GameState(mission_templates=[])
        game_state.district.unrest = 65
        game_state.district.media_heat = 30

        board = generate_mission_board(game_state, board_size=6)

        self.assertTrue(any(m.id.startswith("evacuation") for m in board))

    def test_success_and_failure_follow_extraction_threshold(self):
        constraints = evacuation_constraints(pressure=70)

        success = evaluate_evacuation_outcome(
            extracted_agents=2,
            alive_agents=2,
            neutralized_enemies=6,
            min_extracted_agents=constraints["min_extracted_agents"],
            tolerated_losses=constraints["tolerated_losses"],
        )
        failure = evaluate_evacuation_outcome(
            extracted_agents=1,
            alive_agents=2,
            neutralized_enemies=8,
            min_extracted_agents=constraints["min_extracted_agents"],
            tolerated_losses=constraints["tolerated_losses"],
        )

        self.assertTrue(success.succeeded)
        self.assertFalse(failure.succeeded)
        self.assertGreater(success.score, failure.score)

    def test_template_tags_and_metadata_include_ui_briefing_fields(self):
        template = create_evacuation_template("Chrome Warrens", pressure=52)
        briefing = evacuation_briefing_fields(pressure=52)

        self.assertEqual(template.objective_type, "safe_extraction")
        self.assertTrue(any(tag.name == "evacuation_pressure" for tag in template.tags))
        self.assertIn("risk", briefing)
        self.assertIn("reward", briefing)
        self.assertIn("emotional_impact", briefing)


if __name__ == "__main__":
    unittest.main()
