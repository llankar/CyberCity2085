"""Mission board presentation rules."""

import unittest

from game.ui.mission_board import (
    build_mission_board_lines,
    build_selected_mission_lines,
    objective_label,
    risk_label,
)
from game.narrative.mission_briefing_conventions import NEUTRAL_IMPACT_FALLBACK
from game.mission_templates import create_mission_templates


class MissionBoardUITest(unittest.TestCase):
    def test_risk_and_objective_labels_keep_mission_rows_readable(self):
        self.assertEqual(risk_label(1), "contained")
        self.assertEqual(risk_label(3), "elevated")
        self.assertEqual(risk_label(4), "severe")
        self.assertEqual(objective_label("data_theft"), "DATA THEFT")
        self.assertEqual(objective_label("unknown"), "ELIMINATE")

    def test_mission_board_lines_mark_selected_mission(self):
        missions = create_mission_templates("Chrome Warrens")

        lines = build_mission_board_lines(missions, selected_index=1)

        self.assertIn(">2. Sabotage: Jackal Relay Burn", lines[1])
        self.assertIn("SABOTAGE", lines[1])
        self.assertIn("Risk 4 (severe)", lines[1])
        self.assertIn("Reward 70 funds", lines[1])
        self.assertIn("Duration: 1 day", lines[1])
        self.assertIn("1. Extraction: Neon Witness", lines[0])

    def test_selected_mission_lines_show_pressure_complications_and_stakes(self):
        mission = create_mission_templates("Chrome Warrens")[0]

        lines = build_selected_mission_lines(mission)

        self.assertIn("Objective: Extract a clinic witness", lines[0])
        self.assertIn("Pressure: Unrest +3, Media Heat +2", lines[1])
        self.assertEqual(lines[2], "Fund Reward: 40 corporate funds")
        self.assertEqual(lines[3], "Duration: 1 day")
        self.assertEqual(lines[4], "Mission tags (normalized): neon_blackout")
        self.assertIn("Emotional impact (short):", lines[5])
        self.assertIn("Tags opérationnels: neon_blackout", lines[6])
        self.assertIn("Impact humain attendu", lines[7])
        self.assertIn("Media Leak", lines[8])
        self.assertIn("Civilian Panic", lines[8])
        self.assertIn("Success: Warrens Free Clinic", lines[9])
        self.assertIn("Failure: Chrome Jackals", lines[10])

    def test_selected_mission_lines_fallback_when_tags_and_emotional_impact_are_missing(self):
        mission = create_mission_templates("Chrome Warrens")[0]
        mission.tags = []
        mission.emotional_impact_hint = {}

        lines = build_selected_mission_lines(mission)

        self.assertEqual(lines[4], "Mission tags (normalized): none")
        self.assertEqual(lines[5], f"Emotional impact (short): {NEUTRAL_IMPACT_FALLBACK}")

    def test_selected_mission_lines_show_multiple_tags_and_existing_emotional_short_text(self):
        mission = create_mission_templates("Chrome Warrens")[2]
        mission.emotional_impact_hint = {
            "level": "high",
            "short_text": "Charge émotionnelle élevée: extraction rapide exigée.",
            "normalized_tags": ["ghost_signal", "media_swarm"],
        }

        lines = build_selected_mission_lines(mission)

        self.assertEqual(lines[4], "Mission tags (normalized): ghost_signal, media_swarm")
        self.assertIn("Charge émotionnelle élevée", lines[5])

    def test_empty_mission_board_has_operator_guidance(self):
        self.assertEqual(build_mission_board_lines([], 0), ["No missions available."])
        self.assertEqual(
            build_selected_mission_lines(None),
            ["Select a mission to inspect launch pressure and fallout."],
        )


if __name__ == "__main__":
    unittest.main()
