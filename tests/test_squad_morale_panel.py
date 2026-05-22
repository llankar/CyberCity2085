"""Tests for squad morale aggregation and reusable widget lines."""

import unittest

from game.character import Character
from game.management.morale import aggregate_squad_morale, morale_state
from game.ui.widgets.squad_morale_panel import build_squad_morale_panel_lines


class SquadMoralePanelTest(unittest.TestCase):
    def test_aggregate_calculation_is_consistent(self):
        squad = [
            Character("Calm", loyalty=3, stress=10),
            Character("Frayed", loyalty=1, stress=40),
        ]

        summary = aggregate_squad_morale(squad, previous_global_morale=55)

        self.assertEqual(summary.global_morale, 45)
        self.assertEqual(summary.trend_delta, -10)
        self.assertEqual(summary.state, "declining")
        self.assertEqual([c.morale for c in summary.contributions], [70, 20])

    def test_state_thresholds_cover_stable_declining_critical(self):
        self.assertEqual(morale_state(75), "stable")
        self.assertEqual(morale_state(45), "declining")
        self.assertEqual(morale_state(30), "critical")

    def test_empty_squad_is_robust_and_renderable(self):
        summary = aggregate_squad_morale([])
        lines = build_squad_morale_panel_lines(summary)

        self.assertEqual(summary.global_morale, 0)
        self.assertEqual(summary.trend_delta, 0)
        self.assertEqual(summary.contributions, [])
        self.assertEqual(summary.state, "critical")
        self.assertEqual(len(lines), 2)
        self.assertIn("No active squad assigned", lines[1].text)


if __name__ == "__main__":
    unittest.main()
