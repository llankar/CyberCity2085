"""Tests for mission impact summary widget and emotional hint mapping."""

import unittest

from game.gamestate import GameState
from game.mission_generation import generate_mission_board
from game.mission_templates import create_mission_templates
from game.ui.widgets.mission_impact_summary import (
    NEUTRAL_IMPACT_TEXT,
    build_mission_impact_summary_lines,
    impact_hint_text,
)


class MissionImpactSummaryTest(unittest.TestCase):
    def test_summary_lines_include_operational_tags(self):
        mission = create_mission_templates("Chrome Warrens")[0]
        mission.emotional_impact_hint = {"level": "medium", "text": "test hint"}

        lines = build_mission_impact_summary_lines(mission)

        self.assertIn("Tags opérationnels: neon_blackout", lines[0])
        self.assertIn("Impact humain attendu (modéré):", lines[1])

    def test_impact_levels_are_coherent_with_generation_pressure(self):
        game_state = GameState(mission_templates=[])
        missions = generate_mission_board(game_state, board_size=3)

        allowed = {"low", "medium", "high", "critical"}
        for mission in missions:
            self.assertIn(mission.emotional_impact_hint.get("level"), allowed)
            self.assertTrue(mission.emotional_impact_hint.get("text"))

    def test_neutral_fallback_when_hint_missing_or_invalid(self):
        self.assertEqual(impact_hint_text(None), NEUTRAL_IMPACT_TEXT)
        self.assertEqual(impact_hint_text({"level": "unknown", "text": "x"}), NEUTRAL_IMPACT_TEXT)
        self.assertEqual(impact_hint_text({"level": "low", "text": ""}), NEUTRAL_IMPACT_TEXT)


if __name__ == "__main__":
    unittest.main()
