"""Mission board presentation rules."""

import unittest

from game.mission_templates import create_mission_templates
from game.ui.mission_board import (
    build_mission_board_lines,
    build_selected_mission_lines,
    objective_label,
    risk_label,
)


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
        self.assertIn("Duration: 1 day", lines[1])

    def test_selected_mission_lines_are_split_in_sections(self):
        mission = create_mission_templates("Chrome Warrens")[0]
        lines = build_selected_mission_lines(mission)
        self.assertEqual(lines[0], "[Mission Summary]")
        self.assertEqual(lines[4], "[Risk & Complications]")
        self.assertEqual(lines[8], "[Squad Emotional Impact]")
        self.assertEqual(lines[12], "[Rewards & Opportunity Cost]")

    def test_selected_mission_lines_fallback_when_data_missing(self):
        mission = create_mission_templates("Chrome Warrens")[0]
        mission.tags = []
        mission.possible_complications = []
        mission.emotional_impact_hint = {}

        lines = build_selected_mission_lines(mission)

        self.assertIn("Complications: none", lines)
        self.assertIn("Mission tags (normalized): none", lines)
        self.assertIn("Stress: UNKNOWN", lines)

    def test_selected_mission_lines_show_multiple_tags_and_high_stress(self):
        mission = create_mission_templates("Chrome Warrens")[2]
        mission.emotional_impact_hint = {
            "emotional_impact_summary": "Charge émotionnelle élevée: extraction rapide exigée.",
            "risk_explanation": "Risque amplifié par propagation médiatique.",
            "expected_stress_band": "critical",
            "normalized_tags": ["ghost_signal", "media_swarm"],
        }

        lines = build_selected_mission_lines(mission)

        self.assertIn("Emotional summary: Charge émotionnelle élevée", lines[9])
        self.assertEqual(lines[10], "Stress: CRITICAL")
        self.assertEqual(lines[11], "Mission tags (normalized): ghost_signal, media_swarm")

    def test_locked_mission_state_is_explicit(self):
        mission = create_mission_templates("Chrome Warrens")[1]
        mission.launch_block_reason = "Requires squad medic"

        lines = build_selected_mission_lines(mission)

        self.assertIn("Launch status: LOCKED (Requires squad medic)", lines)


if __name__ == "__main__":
    unittest.main()
