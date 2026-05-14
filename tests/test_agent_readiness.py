"""Pre-mission readiness briefing rules."""

import unittest

from game.agent_readiness import (
    build_agent_readiness_lines,
    estimate_mission_stress,
    projected_stress,
    stress_state_label,
)
from game.character import Character
from game.mission_templates import MissionTemplate


def _mission(risk_level=3):
    return MissionTemplate(
        id="readiness_test",
        title="Readiness Test",
        objective_text="Test the deployment briefing.",
        target_faction="Test Faction",
        district="Test District",
        district_pressure={},
        starting_enemy_count=1,
        risk_level=risk_level,
    )


class AgentReadinessTest(unittest.TestCase):
    def test_stress_state_labels_keep_dashboard_readable(self):
        self.assertEqual(stress_state_label(10), "steady")
        self.assertEqual(stress_state_label(40), "rattled")
        self.assertEqual(stress_state_label(70), "frayed")
        self.assertEqual(stress_state_label(90), "breaking")

    def test_projected_stress_uses_mission_risk_without_exceeding_cap(self):
        agent = Character("Wire", stress=96)
        mission = _mission(risk_level=4)

        self.assertEqual(estimate_mission_stress(mission), 14)
        self.assertEqual(projected_stress(agent, mission), 100)

    def test_readiness_lines_rank_most_at_risk_agent_first(self):
        steady = Character("Calm", stress=5)
        frayed = Character("Ghost", stress=78, trauma=["Haunted by Faction Retaliation"])
        mission = _mission(risk_level=3)

        lines = build_agent_readiness_lines([steady, frayed], mission)

        self.assertIn("Ghost: breaking after op (78->88)", lines[0])
        self.assertIn("breakdown risk", lines[0])
        self.assertIn("Calm: steady after op (5->15)", lines[1])

    def test_no_deployable_agents_gets_launch_guidance(self):
        downed = Character("Downed")
        downed.stats.hp = 0

        self.assertEqual(
            build_agent_readiness_lines([downed], _mission()),
            ["No deployable agents. Recruit or recover someone before launch."],
        )


if __name__ == "__main__":
    unittest.main()
