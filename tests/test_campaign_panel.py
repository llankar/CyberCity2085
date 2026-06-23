"""Regression checks for the Intel room Global Scenario panel."""

from __future__ import annotations

import unittest

from game.gamestate import GameState
from game.management.events import ActiveEvent, EventChoice, EventTemplate, STARVERS_OUTBREAK
from game.ui.screens.campaign_panel import (
    build_act_transition_summary,
    build_global_scenario_summary,
    build_hidden_ai_conspiracy_summary,
    build_hungry_tide_summary,
    build_intel_fragment_browser,
    build_novatek_experiment_thread_summary,
    build_pharmacorp_cure_thread_summary,
    build_three_sevens_presence_summary,
    build_world_state_change_feed,
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
        self.assertIn("pharmacorp", summary)
        self.assertIn("novatek", summary)
        self.assertIn("hidden_ai", summary)

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

    def test_world_state_change_feed_records_major_global_changes(self) -> None:
        game_state = GameState()
        game_state.campaign.discovered_intel = [
            "act2_new_york_target",
            "act2_warsaw_lockdown",
            "act4_pharmacorp_secret",
            "act4_ai_existence",
        ]
        game_state.campaign.world.hungry_tide_progress = 86
        game_state.campaign.world.new_york_status = "siege"
        game_state.campaign.world.warsaw_status = "three_sevens_controlled"
        game_state.campaign.world.pharmacorp_secret = "exposed"
        game_state.campaign.world.ai_factions_status = "suspected"
        game_state.event_log.append("[INTEL] New York: The Tide Arrives.")

        feed = build_world_state_change_feed(game_state)
        titles = [entry["title"] for entry in feed]
        summaries = [entry["summary"] for entry in feed]

        self.assertIn("New York siege escalation", titles)
        self.assertIn("Warsaw occupation confirmed", titles)
        self.assertIn("Pharmacorp cure thread", titles)
        self.assertIn("Hidden AI signal", titles)
        self.assertIn("Hungry Tide critical milestone", titles)
        self.assertTrue(any("Updates new york status" in summary for summary in summaries))
        self.assertLessEqual(len(feed), 12)

    def test_pharmacorp_cure_thread_summary_exposes_campaign_hooks(self) -> None:
        game_state = GameState()
        game_state.campaign.current_act = 5
        game_state.campaign.world.pharmacorp_secret = "exposed"
        game_state.campaign.discovered_intel = [
            "act3_cure_signal",
            "act4_hungry_thinks",
            "act4_pharmacorp_secret",
        ]

        summary = build_pharmacorp_cure_thread_summary(game_state)

        self.assertEqual(summary["world_status"], "Pharmacorp: EXPOSED")
        self.assertTrue(any("Pharmacorp" in title for title in summary["story_mission_hooks"]))
        self.assertIn("Pharmacorp: Anomalous Research Log", summary["intel_fragments"])
        self.assertIn("The Cure Has Always Existed", summary["intel_fragments"])
        self.assertIn("Black-Market Cure Vials", summary["event_hooks"])
        self.assertIn("Buy samples from the clinic", summary["black_market_choices"])
        self.assertIn("Project P-77 cure data is exposed.", summary["hidden_cure"])
        self.assertIn("Cured Starver subject hooks are visible.", summary["cured_starvers"])
        self.assertTrue(any("containment" in line for line in summary["containment_failures"]))
        self.assertTrue(any("leverage" in line for line in summary["moral_ambiguity"]))

    def test_novatek_experiment_thread_summary_exposes_hybrid_hooks(self) -> None:
        game_state = GameState()
        game_state.campaign.current_act = 4
        game_state.campaign.discovered_intel = ["act4_novatek_hybrids"]

        summary = build_novatek_experiment_thread_summary(game_state)

        self.assertIn("Novatek Containment Site Delta-9", summary["event_hooks"])
        self.assertIn("Novatek: Hybrid Containment Failure", summary["intel_fragments"])
        self.assertIn("Novatek containment-site breach", summary["mission_hooks"])
        self.assertIn("cyborg-Starver hybrids", summary["experiment_themes"])
        self.assertIn("mutant escalation", summary["experiment_themes"])
        self.assertIn("failed containment sites", summary["experiment_themes"])
        self.assertEqual(summary["special_enemy_themes"], ["novatek_hybrid"])
        self.assertIn("Expose the hybrid program", summary["event_choices"])

    def test_hidden_ai_summary_stays_gated_until_late_campaign(self) -> None:
        game_state = GameState()
        game_state.campaign.current_act = 3
        game_state.campaign.discovered_intel = ["act4_ai_existence"]

        summary = build_hidden_ai_conspiracy_summary(game_state)

        self.assertFalse(summary["revealed"])
        self.assertEqual(summary["intel_fragments"], [])
        self.assertEqual(summary["event_hooks"], [])
        self.assertEqual(summary["faction_roles"], {})
        self.assertIn("Act 4+", summary["reveal_timing"])

    def test_hidden_ai_summary_exposes_two_late_act_factions(self) -> None:
        game_state = GameState()
        game_state.campaign.current_act = 5
        game_state.campaign.world.ai_factions_status = "confirmed"
        game_state.campaign.discovered_intel = [
            "act4_ai_existence",
            "act4_ai_factions",
            "act5_final_choice",
        ]

        summary = build_hidden_ai_conspiracy_summary(game_state)

        self.assertTrue(summary["revealed"])
        self.assertEqual(summary["active_status"], "CONFIRMED")
        self.assertIn("They Have Been Watching", summary["intel_fragments"])
        self.assertIn("Preservationists vs Exterminators", summary["intel_fragments"])
        self.assertIn("The AI Message", summary["event_hooks"])
        self.assertIn("The Final Decision", summary["event_hooks"])
        self.assertIn("protect humanity", summary["faction_roles"]["Preservationist AIs"])
        self.assertIn("human extinction", summary["faction_roles"]["Exterminator AIs"])

    def test_act_transition_summary_exposes_stakes_and_consequences(self) -> None:
        summary = build_act_transition_summary(4, "The Truth")

        self.assertEqual(summary["act_number"], 4)
        self.assertEqual(summary["act_title"], "The Truth")
        self.assertIn("truth", summary["summary"].lower())
        self.assertTrue(
            any("AI" in line for line in summary["newly_revealed_stakes"])
        )
        self.assertTrue(
            any(
                "World-state" in line
                for line in summary["immediate_strategic_consequences"]
            )
        )

    def test_three_sevens_presence_summary_exposes_campaign_antagonist_hooks(self) -> None:
        game_state = GameState()
        game_state.campaign.current_act = 5
        game_state.campaign.world.warsaw_status = "three_sevens_controlled"
        game_state.campaign.discovered_intel = [
            "act1_three_sevens_banner",
            "act5_twenty_one",
        ]
        game_state.active_events = [
            ActiveEvent(
                id="three_sevens_decrees",
                template=EventTemplate(
                    title="Three Sevens Emergency Decrees",
                    category=STARVERS_OUTBREAK,
                    description="Warsaw authority broadcasts are rewriting response law.",
                    severity=5,
                    choices=[
                        EventChoice(
                            "jam",
                            "Jam broadcast",
                            summary="Risk conflict with Three Sevens.",
                        )
                    ],
                    expiration_days=2,
                ),
                created_day=game_state.calendar.current_day,
                expires_day=game_state.calendar.current_day + 1,
            )
        ]

        summary = build_three_sevens_presence_summary(game_state)

        self.assertTrue(any("Warsaw" in title for title in summary["story_mission_hooks"]))
        self.assertTrue(any("Three Sevens" in title for title in summary["intel_fragments"]))
        self.assertEqual(summary["event_hooks"], ["Three Sevens Emergency Decrees"])
        self.assertIn("corp_37_power_armor", summary["special_enemy_themes"])
        self.assertIn("propaganda", summary["propaganda"].lower())
        self.assertEqual(summary["warsaw_reference"], "Warsaw: 3-7s Controlled")
        self.assertIn("Emergency authority decrees", summary["late_campaign_escalation"])

    def test_intel_fragment_browser_groups_known_and_unknown_entries(self) -> None:
        game_state = GameState()
        game_state.campaign.discovered_intel = [
            "act1_three_sevens_banner",
            "act3_cure_signal",
        ]

        browser = build_intel_fragment_browser(game_state)

        self.assertEqual(browser["known_count"], 2)
        self.assertGreater(browser["unknown_count"], 0)
        self.assertIn(1, browser["groups_by_act"])
        self.assertIn("mission_reward", browser["groups_by_source"])
        self.assertIn("Three Sevens", browser["groups_by_faction"])
        self.assertIn("Pharmacorp", browser["groups_by_faction"])

        known_titles = [entry["title"] for entry in browser["known_entries"]]
        self.assertIn("The Three Sevens Banner", known_titles)
        self.assertIn("Pharmacorp: Anomalous Research Log", known_titles)
        self.assertTrue(
            any(
                "Pharmacorp research log" in entry["lore_text"]
                for entry in browser["known_entries"]
            )
        )
        self.assertTrue(
            any(
                "Updates pharmacorp secret" in entry["mechanical_relevance"]
                for entry in browser["known_entries"]
            )
        )
        self.assertTrue(
            all(
                entry["title"].startswith("Unknown Act")
                for entry in browser["unknown_entries"]
            )
        )
        self.assertTrue(
            all(
                "Undiscovered fragment" in entry["lore_text"]
                for entry in browser["unknown_entries"]
            )
        )


if __name__ == "__main__":
    unittest.main()
