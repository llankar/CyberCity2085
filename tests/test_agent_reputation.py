"""Tests for post-mission agent reputation and nicknames."""

import unittest

from game.character import Character
from game.mission_templates import MissionTemplate
from game.narrative.agent_reputation import (
    apply_agent_reputation_awards,
    build_agent_reputation_awards,
)


def _mission(objective_type: str = "eliminate") -> MissionTemplate:
    return MissionTemplate(
        id="rep-test",
        title="Glass Breakpoint",
        objective_text="Hold the line",
        target_faction="Three Sevens",
        district="Neon Row",
        district_pressure={},
        starting_enemy_count=3,
        risk_level=3,
        objective_type=objective_type,
    )


class AgentReputationTest(unittest.TestCase):
    def test_kill_standout_awards_nickname_and_reputation_tag(self):
        agent = Character("Vera", role="sniper")

        awards = build_agent_reputation_awards(
            [agent],
            {"Vera": {"kills": 3}},
            True,
            _mission(),
        )
        lines = apply_agent_reputation_awards([agent], awards)

        self.assertEqual(agent.nickname, "Breaker")
        self.assertIn("elite_breaker", agent.reputation)
        self.assertTrue(any("Reputation:" in line for line in lines))

    def test_rescue_objective_awards_civilian_reputation(self):
        agent = Character("Mako", role="medic")

        awards = build_agent_reputation_awards(
            [agent],
            {"Mako": {"saved_civilian": True}},
            True,
            _mission("civilian_rescue"),
        )

        self.assertEqual(awards[0].tag, "civilian_shield")
        self.assertEqual(awards[0].nickname, "Shield")

    def test_existing_reputation_tag_is_not_awarded_twice(self):
        agent = Character("Nyx", reputation=["critical_survivor"])

        awards = build_agent_reputation_awards(
            [agent],
            {"Nyx": {"damage_taken": 40}},
            True,
            _mission(),
        )

        self.assertEqual(awards, [])

    def test_existing_nickname_is_not_replaced_by_later_award(self):
        agent = Character("Patch", nickname="Shield")

        awards = build_agent_reputation_awards(
            [agent],
            {"Patch": {"kills": 3}},
            True,
            _mission(),
        )
        apply_agent_reputation_awards([agent], awards)

        self.assertEqual(agent.nickname, "Shield")
        self.assertEqual(awards[0].nickname, "")


if __name__ == "__main__":
    unittest.main()
