"""Regression checks for the Intel room Global Scenario panel."""

from __future__ import annotations

import unittest

from game.gamestate import GameState
from game.management.events import ActiveEvent, EventChoice, EventTemplate, STARVERS_OUTBREAK
from game.ui.screens.campaign_panel import (
    build_global_scenario_summary,
    build_hungry_tide_summary,
)


class CampaignPanelSummaryTest(unittest.TestCase):
    def test_global_scenario_summary_covers_wave6_required_fields(self) -> None:
        game_state = GameState()
        game_state.campaign.current_act = 2
        game_state.campaign.act_progress = 3
        game_state.campaign.discovered_intel = [
            "act1_warsaw_coup",
            "act2_tide_forming",
            "act2_new_york_target",
        ]
        game_state.campaign.world.hungry_tide_progress = 64
        game_state.campaign.world.new_york_status = "alert"
        game_state.campaign.world.warsaw_status = "three_sevens_controlled"
        game_state.campaign.world.pharmacorp_secret = "rumored"
        game_state.active_events = [
            ActiveEvent(
                id="global_starver_surge",
                template=EventTemplate(
                    title="Starver Surge",
                    category=STARVERS_OUTBREAK,
                    description="Hungry packs are moving toward the perimeter.",
                    severity=4,
                    choices=[EventChoice("monitor", "Monitor")],
                    expiration_days=3,
                ),
                created_day=game_state.calendar.current_day,
                expires_day=game_state.calendar.current_day + 2,
            )
        ]

        summary = build_global_scenario_summary(game_state)

        self.assertEqual(summary["current_act"], 2)
        self.assertEqual(summary["act_title"], "The Tide")
        self.assertEqual(summary["act_progress"], 3)
        self.assertEqual(summary["act_required"], 4)
        self.assertEqual(summary["hungry_tide_percentage"], 64)
        self.assertEqual(summary["new_york_status"], "alert")
        self.assertEqual(summary["warsaw_status"], "three_sevens_controlled")
        self.assertEqual(summary["discovered_intel_count"], 3)
        self.assertEqual(summary["discovered_intel_this_act"], 2)
        self.assertGreaterEqual(summary["known_intel_this_act"], 1)
        self.assertTrue(any("Hungry Tide at 64%" in line for line in summary["major_known_threats"]))
        self.assertTrue(any("New York Alert" in line for line in summary["major_known_threats"]))
        self.assertTrue(any("Warsaw 3-7s Controlled" in line for line in summary["major_known_threats"]))
        self.assertTrue(any("Starver Surge" in line for line in summary["unresolved_global_events"]))

        hungry_tide = summary["hungry_tide"]
        self.assertEqual(hungry_tide["progress"], 64)
        self.assertEqual(hungry_tide["threat_level"], "high")
        self.assertIn("Atlantic corridor", hungry_tide["affected_regions"])
        self.assertEqual(hungry_tide["expected_new_york_impact"], "major assault forming")
        self.assertIn("New York", hungry_tide["consequence_if_ignored"])

    def test_hungry_tide_summary_explains_new_york_siege(self) -> None:
        game_state = GameState()
        game_state.campaign.world.hungry_tide_progress = 92
        game_state.campaign.world.new_york_status = "siege"

        summary = build_hungry_tide_summary(game_state)

        self.assertEqual(summary["threat_level"], "critical")
        self.assertIn("New York perimeter", summary["affected_regions"])
        self.assertEqual(summary["expected_new_york_impact"], "New York is under siege")
        self.assertIn("worldwide", summary["consequence_if_ignored"])


if __name__ == "__main__":
    unittest.main()
