"""Regression checks for enhanced post-battle debrief content."""

from __future__ import annotations

import unittest

from game.consequences import Consequence
from game.gamestate import GameState
from game.mission_templates import MissionComplication, MissionTemplate
from game.ui.screens.battle_debrief_view import (
    AgentDebriefStat,
    build_battle_debrief_summary,
)


def _mission() -> MissionTemplate:
    return MissionTemplate(
        id="debrief_test",
        title="Extraction: Neon Witness",
        objective_text="Extract the witness.",
        target_faction="Chrome Jackals",
        district="Chrome Warrens",
        district_pressure={},
        starting_enemy_count=3,
        risk_level=4,
        fund_reward=120,
        success_consequences=[
            Consequence(
                affected_district="Chrome Warrens",
                affected_faction="Warrens Free Clinic",
                narrative_text="The witness reaches the clinic and safehouse routes open.",
                mechanical_effects={"stability": 5, "unrest": -4},
            )
        ],
    )


def _complication() -> MissionComplication:
    return MissionComplication(
        key="media_leak",
        name="Media Leak",
        trigger_text="A pirate news relay leaks the squad route.",
        risk_threshold=2,
        consequence=Consequence(
            affected_district="Chrome Warrens",
            affected_faction="Chrome Jackals",
            narrative_text="The leaked route turns the firefight into a public scandal.",
            mechanical_effects={"media_heat": 8},
        ),
    )


class BattleDebriefSummaryTest(unittest.TestCase):
    def test_summary_covers_wave6_required_debrief_fields(self) -> None:
        game_state = GameState()
        game_state.latest_mission_debrief = {
            "lines": [
                {
                    "agent_name": "Vera",
                    "emotional_tone": "tense",
                    "consequence_type": "injured",
                    "text": "Vera returns injured but keeps the witness alive.",
                }
            ],
            "decision_key": "Hold extraction under pressure.",
            "risk_taken": "Major narrative risk accepted.",
            "heroic_action": "Vera held the line.",
            "rpg_links": ["Stress: Vera at 62/100, recovery priority."],
        }
        agent_stats = [
            AgentDebriefStat(
                name="Vera",
                role="sniper",
                portrait_path=None,
                damage_dealt=18,
                damage_taken=7,
                kills=2,
                stress_delta=12,
                xp_gained=150,
                injuries=["Shrapnel cuts"],
            )
        ]

        summary = build_battle_debrief_summary(
            game_state,
            True,
            _mission(),
            agent_stats,
            _complication(),
        )

        self.assertEqual(summary["objective_result"], "All objectives completed")
        self.assertEqual(summary["outcome"], "victory")
        self.assertIn("Credits: +120", summary["rewards"])
        self.assertEqual(summary["agent_rows"][0]["kills"], 2)
        self.assertEqual(summary["agent_rows"][0]["damage_dealt"], 18)
        self.assertEqual(summary["agent_rows"][0]["damage_taken"], 7)
        self.assertEqual(summary["agent_rows"][0]["stress_delta"], 12)
        self.assertEqual(summary["agent_rows"][0]["xp_gained"], 150)
        self.assertEqual(summary["agent_rows"][0]["injuries"], ["Shrapnel cuts"])
        self.assertEqual(
            summary["triggered_complications"],
            ["A pirate news relay leaks the squad route."],
        )
        self.assertTrue(any("Chrome Jackals" in line for line in summary["faction_changes"]))
        self.assertTrue(any("Chrome Warrens" in line for line in summary["district_changes"]))
        self.assertTrue(
            any("Vera returns injured" in line for line in summary["narrative_consequences"])
        )
        self.assertEqual(summary["continue_action"], "ManagementView")


if __name__ == "__main__":
    unittest.main()
