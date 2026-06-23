"""Regression checks for enhanced post-battle debrief content."""

from __future__ import annotations

import unittest

from game.character import Character
from game.consequences import Consequence
from game.gamestate import GameState
from game.mission_templates import MissionComplication, MissionTemplate
from game.savage_fate import tag_from_library
from game.ui.screens.battle_debrief_view import (
    AgentDebriefStat,
    build_battle_debrief_summary,
    build_consequence_summary_lines,
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
                tags=[tag_from_library("civilian_panic")],
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
        game_state = GameState(characters=[Character("Vera")])
        game_state.characters[0].nickname = "Breaker"
        game_state.characters[0].reputation = ["elite_breaker"]
        game_state.characters[0].temporary_scars = [{"title": "Nights of Sirens"}]
        game_state.unavailable_mission_ids = ["jackal_relay_lockdown"]
        game_state.campaign.discover_intel("act1_three_sevens_banner")
        game_state.campaign.world.hungry_tide_progress = 17
        game_state.campaign.world.new_york_status = "alert"
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
            "reputation_awards": [
                {
                    "agent_name": "Vera",
                    "tag": "elite_breaker",
                    "nickname": "Breaker",
                    "reason": "eliminated 3 hostiles during Glass Breakpoint",
                }
            ],
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
        self.assertEqual(summary["agent_rows"][0]["nickname"], "Breaker")
        self.assertIn("elite_breaker", summary["agent_rows"][0]["reputation"])
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
        self.assertTrue(
            any("elite_breaker" in line for line in summary["narrative_consequences"])
        )
        self.assertEqual(summary["continue_action"], "ManagementView")

        consequence_lines = build_consequence_summary_lines(
            game_state,
            True,
            _mission(),
            agent_stats,
            _complication(),
        )

        self.assertTrue(any(line.startswith("City pressure:") for line in consequence_lines))
        self.assertTrue(any("Faction Chrome Jackals:" in line for line in consequence_lines))
        self.assertTrue(any("civilian_panic" in line for line in consequence_lines))
        self.assertTrue(any("Agent scars: Vera: Nights of Sirens" in line for line in consequence_lines))
        self.assertTrue(any("Rewards: Credits: +120" in line for line in consequence_lines))
        self.assertTrue(any("jackal_relay_lockdown" in line for line in consequence_lines))
        self.assertTrue(any("act1_three_sevens_banner" in line for line in consequence_lines))
        self.assertTrue(any("Hungry Tide 17%" in line for line in consequence_lines))


if __name__ == "__main__":
    unittest.main()
