"""Tests for compact narrative feed aggregation + widget lines."""

import unittest

from game.gamestate import GameState
from game.management.events import ActiveEvent, EventTemplate
from game.narrative.event_feed import NarrativeFeedEntry, build_narrative_event_feed
from game.ui.widgets.narrative.feed_filters import FILTER_AGENTS, FILTER_FACTIONS, FILTER_MISSIONS
from game.ui.widgets.narrative_feed_panel import build_narrative_feed_panel_lines


class NarrativeFeedPanelTest(unittest.TestCase):
    def test_feed_aggregates_sources_and_keeps_reverse_chronological_depth(self):
        game_state = GameState()
        game_state.latest_agent_aftermath = [
            "Aftermath: Nyx carries Old Job.",
            "Aftermath: Patch carries New Job.",
        ]
        game_state.latest_recovery_dialogues = [
            {"line": "Nyx stays with Patch until the breathing steadies."}
        ]
        game_state.faction_reward_journal = [
            {"kind": "local_trust", "text": "The clinic spreads a quiet word of trust."}
        ]
        game_state.latest_mission_debrief = {
            "skill_check_outcomes": [
                "Tech Check: roll 2 -> total 5 (target 6) [FAILURE]"
            ]
        }
        game_state.active_events = [
            ActiveEvent(
                id="event-1",
                template=EventTemplate(
                    title="Neon Market Riot",
                    category="social unrest",
                    description="",
                    severity=2,
                    choices=[],
                    expiration_days=2,
                ),
                created_day=game_state.calendar.current_day,
                expires_day=game_state.calendar.current_day + 1,
            )
        ]

        feed = build_narrative_event_feed(game_state, max_entries=9)

        self.assertLessEqual(len(feed), 9)
        self.assertEqual(feed[0].category, "mission")
        self.assertEqual(feed[-1].category, "agent")
        self.assertTrue(any(entry.category == "mission" for entry in feed))
        self.assertTrue(any("Tech Check" in entry.text for entry in feed))

    def test_widget_prioritizes_agent_and_consequence_before_system_and_base(self):
        entries = [
            NarrativeFeedEntry("system", "Maintenance ping."),
            NarrativeFeedEntry("agent", "Nyx stabilise Patch."),
            NarrativeFeedEntry("base", "Energy level: stable."),
            NarrativeFeedEntry("consequence", "A lost civilian weighs on the team."),
        ]

        lines = build_narrative_feed_panel_lines(entries)

        self.assertIn("[AGENT]", lines[0].text)
        self.assertIn("[CONSEQUENCE]", lines[1].text)
        self.assertIn("[SYSTEM]", lines[2].text)
        self.assertIn("[BASE]", lines[3].text)

    def test_widget_adds_icon_tone_and_relative_timestamp_and_clips(self):
        entries = [
            NarrativeFeedEntry(
                "mission",
                "Mission long " + ("X" * 200),
            )
        ]

        lines = build_narrative_feed_panel_lines(entries)

        self.assertIn("🎯", lines[0].text)
        self.assertIn("(tense)", lines[0].text)
        self.assertIn("just now", lines[0].text)
        self.assertIn("...", lines[0].text)

    def test_widget_quick_filters_keep_main_flow_simple(self):
        entries = [
            NarrativeFeedEntry("agent", "Agent line."),
            NarrativeFeedEntry("mission", "Mission line."),
            NarrativeFeedEntry("faction", "Faction line."),
        ]

        self.assertEqual(len(build_narrative_feed_panel_lines(entries, active_filter=FILTER_AGENTS)), 1)
        self.assertEqual(len(build_narrative_feed_panel_lines(entries, active_filter=FILTER_MISSIONS)), 1)
        self.assertEqual(len(build_narrative_feed_panel_lines(entries, active_filter=FILTER_FACTIONS)), 1)


if __name__ == "__main__":
    unittest.main()
