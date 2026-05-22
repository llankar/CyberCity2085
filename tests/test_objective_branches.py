import unittest

from game.mission_system import evaluate_mission_objective_phase, mission_objective_branch_summary
from game.mission_templates import MissionTemplate


def _mission(objective_type: str) -> MissionTemplate:
    return MissionTemplate(
        id="branch_test",
        title="Branch Test",
        objective_text="Test objective branching.",
        target_faction="Test",
        district="Test District",
        district_pressure={},
        starting_enemy_count=1,
        objective_type=objective_type,
    )


class ObjectiveBranchesTest(unittest.TestCase):
    def test_nominal_progression_reaches_success_end(self):
        mission = _mission("safe_extraction")

        first = evaluate_mission_objective_phase(mission, {"reached_witness": True})
        second = evaluate_mission_objective_phase(
            mission,
            {"witness_escorted": True},
            current_phase_id=first["next_phase_id"],
        )

        self.assertEqual(first["next_phase_id"], "escort_zone")
        self.assertTrue(second["finished"])
        self.assertEqual(second["next_phase_id"], "mission_success")

    def test_alternative_branch_uses_detour_then_recovers(self):
        mission = _mission("data_with_detour")

        detour = evaluate_mission_objective_phase(mission, {"terminal_breached": False})
        recovered = evaluate_mission_objective_phase(
            mission,
            {"proxy_reached": True},
            current_phase_id=detour["next_phase_id"],
        )

        self.assertEqual(detour["next_phase_id"], "field_proxy")
        self.assertEqual(recovered["next_phase_id"], "extract_data")

    def test_failure_condition_can_end_mission_early(self):
        mission = _mission("sabotage_window")

        failed = evaluate_mission_objective_phase(mission, {"charge_armed": False})

        self.assertTrue(failed["finished"])
        self.assertEqual(failed["next_phase_id"], "mission_failed")

    def test_ui_summary_exposes_readable_branch_lines(self):
        mission = _mission("safe_extraction")

        summary = mission_objective_branch_summary(mission)

        self.assertGreaterEqual(len(summary), 2)
        self.assertIn("safe_extraction", summary[0])


if __name__ == "__main__":
    unittest.main()
