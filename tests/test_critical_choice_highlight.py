"""Tests for relationship-critical choice highlighting."""

import unittest

from game.management.events import ActiveEvent, EventChoice, EventTemplate, apply_event_choice
from game.gamestate import GameState
from game.ui.command_deck import build_event_panel_lines
from game.ui.widgets.critical_choice_highlight import (
    build_critical_choice_highlight,
    format_critical_choice_suffix,
)


class CriticalChoiceHighlightTest(unittest.TestCase):
    def test_render_logic_for_each_impact_level(self):
        low = build_critical_choice_highlight("low")
        medium = build_critical_choice_highlight("medium")
        high = build_critical_choice_highlight("high")

        self.assertEqual(low.marker, "")
        self.assertIn("modéré", medium.text)
        self.assertEqual(high.marker, "◆")
        self.assertIn("élevé", format_critical_choice_suffix("high"))

    def test_marker_presence_for_critical_choices(self):
        event = ActiveEvent(
            id="event-1",
            template=EventTemplate(
                title="Crossfire",
                category="social unrest",
                description="desc",
                severity=3,
                choices=[
                    EventChoice("calm", "Calmer", relation_impact="high"),
                    EventChoice("delay", "Reporter", relation_impact="low"),
                ],
            ),
            created_day=1,
            expires_day=3,
        )

        lines = build_event_panel_lines([event], current_day=1)

        self.assertTrue(any("◆" in line for line in lines))
        self.assertTrue(any("impact élevé" in line for line in lines))

    def test_neutral_choices_do_not_regress_and_high_impact_is_logged(self):
        game_state = GameState()
        game_state.active_events = [
            ActiveEvent(
                id="event-2",
                template=EventTemplate(
                    title="Council Vote",
                    category="city politics",
                    description="desc",
                    severity=2,
                    choices=[
                        EventChoice("safe", "Safe option", relation_impact="low"),
                        EventChoice("bond", "Bond option", relation_impact="high"),
                    ],
                ),
                created_day=1,
                expires_day=2,
            )
        ]

        neutral_lines = build_event_panel_lines(game_state.active_events, current_day=1)
        self.assertFalse(any("impact modéré" in line for line in neutral_lines if "Safe option" in line))

        resolved = apply_event_choice(game_state, "event-2", "bond")

        self.assertTrue(resolved)
        self.assertTrue(hasattr(game_state, "relation_impact_log"))
        self.assertEqual(game_state.relation_impact_log[-1]["level"], "high")


if __name__ == "__main__":
    unittest.main()
