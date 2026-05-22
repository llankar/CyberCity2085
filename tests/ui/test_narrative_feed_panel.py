"""Tests for compact narrative feed aggregation + widget lines."""

import unittest

from game.gamestate import GameState
from game.management.events import ActiveEvent, EventTemplate
from game.narrative.event_feed import build_narrative_event_feed
from game.ui.widgets.narrative_feed_panel import build_narrative_feed_panel_lines


class NarrativeFeedPanelTest(unittest.TestCase):
    def test_feed_aggregates_sources_and_keeps_reverse_chronological_depth(self):
        game_state = GameState()
        game_state.latest_agent_aftermath = [
            "Aftermath: Nyx carries Old Job.",
            "Aftermath: Patch carries New Job.",
        ]
        game_state.latest_recovery_dialogues = [
            {"line": "Nyx reste avec Patch jusqu'à ce que la respiration revienne."}
        ]
        game_state.faction_reward_journal = [
            {"kind": "local_trust", "text": "La clinique diffuse un mot de confiance discret."}
        ]
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
        self.assertEqual(feed[0].category, "faction")
        self.assertEqual(feed[-1].category, "agent")
        self.assertTrue(any(entry.category == "mission" for entry in feed))

    def test_widget_applies_light_visual_categories(self):
        game_state = GameState()
        game_state.latest_agent_aftermath = ["Aftermath: Echo carries Signal Run."]

        lines = build_narrative_feed_panel_lines(build_narrative_event_feed(game_state, 8))

        self.assertTrue(lines)
        self.assertTrue(lines[0].text.startswith("[AGENT]"))


if __name__ == "__main__":
    unittest.main()
