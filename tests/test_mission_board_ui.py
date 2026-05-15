"""Mission board presentation rules."""

import unittest

from game.ui.mission_board import (
    build_mission_board_lines,
    build_selected_mission_lines,
    objective_label,
    risk_label,
)
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

        self.assertTrue(lines[1].startswith(">2. Sabotage: Jackal Relay Burn"))
        self.assertIn("SABOTAGE", lines[1])
        self.assertIn("Risk 4 (severe)", lines[1])
        self.assertIn("Reward 70 funds", lines[1])
        self.assertIn("Duration: 1 day", lines[1])
        self.assertTrue(lines[0].startswith(" 1. Extraction: Neon Witness"))

    def test_selected_mission_lines_show_pressure_complications_and_stakes(self):
        mission = create_mission_templates("Chrome Warrens")[0]

        lines = build_selected_mission_lines(mission)

        self.assertIn("Objective: Extract a clinic witness", lines[0])
        self.assertIn("Pressure: Unrest +3, Media Heat +2", lines[1])
        self.assertEqual(lines[2], "Fund Reward: 40 corporate funds")
        self.assertEqual(lines[3], "Duration: 1 day")
        self.assertEqual(lines[4], "Tags: neon_blackout")
        self.assertIn("Media Leak", lines[5])
        self.assertIn("Civilian Panic", lines[5])
        self.assertIn("Success: Warrens Free Clinic", lines[6])
        self.assertIn("Failure: Chrome Jackals", lines[7])

    def test_empty_mission_board_has_operator_guidance(self):
        self.assertEqual(build_mission_board_lines([], 0), ["No missions available."])
        self.assertEqual(
            build_selected_mission_lines(None),
            ["Select a mission to inspect launch pressure and fallout."],
        )


if __name__ == "__main__":
    unittest.main()
