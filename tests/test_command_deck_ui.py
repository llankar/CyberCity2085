"""Command deck presentation rules."""

import unittest

from game.character import Character
from game.mission_templates import create_mission_templates
from game.ui.command_deck import (
    build_agent_card_lines,
    build_command_deck_layout,
    build_ops_table_header,
    deck_panel_by_key,
)


class CommandDeckUITest(unittest.TestCase):
    def test_layout_keeps_xcom_like_squad_ops_and_briefing_columns(self):
        panels = build_command_deck_layout(1280, 720)

        self.assertEqual(
            [panel.key for panel in panels],
            ["squad", "mission", "details", "briefs"],
        )
        self.assertLess(
            deck_panel_by_key(panels, "squad").left,
            deck_panel_by_key(panels, "mission").left,
        )
        self.assertLess(
            deck_panel_by_key(panels, "mission").left,
            deck_panel_by_key(panels, "briefs").left,
        )
        self.assertEqual(
            deck_panel_by_key(panels, "details").left,
            deck_panel_by_key(panels, "mission").left,
        )
        self.assertEqual(deck_panel_by_key(panels, "squad").title, "Agent Barracks")
        self.assertEqual(deck_panel_by_key(panels, "mission").title, "Operations Table")

    def test_agent_cards_show_selection_cursor_and_medbay_status(self):
        ready = Character(name="Vega", role="sniper", stress=22, loyalty=4)
        wounded = Character(name="Knox", role="samurai", recovery_turns=2)

        lines = build_agent_card_lines([ready, wounded], {"Vega"}, cursor_index=0)

        self.assertTrue(lines[0].startswith("> [X] Vega"))
        self.assertIn("Trait:", lines[1])
        self.assertIn("Sheet STR", lines[2])
        self.assertTrue(lines[3].startswith("  [ ] Knox"))
        self.assertIn("// MEDBAY 2T", lines[3])

    def test_ops_table_header_blends_district_objective_and_risk(self):
        mission = create_mission_templates("Chrome Warrens")[1]

        header = build_ops_table_header(mission, "Chrome Warrens")

        self.assertIn("CHROME WARRENS", header)
        self.assertIn("SABOTAGE", header)
        self.assertIn("RISK 4 SEVERE", header)


if __name__ == "__main__":
    unittest.main()
