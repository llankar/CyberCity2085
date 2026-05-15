"""Research management projects, calendar progress, and unlock application."""

import tempfile
import unittest
from pathlib import Path

from game.gamestate import GameState
from game.management.research import RESEARCH_CATEGORIES, create_starter_research_tree
from game.ui.research_lab import build_research_lab_lines
from game.ui.room_interaction import actions_for_room


class ResearchManagementTest(unittest.TestCase):
    def test_starter_tree_has_requested_upgrade_categories(self):
        tree = create_starter_research_tree()

        categories = {project.category for project in tree.projects.values()}

        self.assertEqual(categories, set(RESEARCH_CATEGORIES))
        for project in tree.projects.values():
            self.assertGreater(project.funds_cost, 0)
            self.assertGreater(project.days_required, 0)

    def test_starting_research_pays_cost_and_queues_project(self):
        game_state = GameState()
        project = game_state.research_tree.project("weapon_smartlink_mk1")
        starting_funds = game_state.available_funds

        started = game_state.start_research(project.id)

        self.assertTrue(started)
        self.assertEqual(
            game_state.available_funds, starting_funds - project.funds_cost
        )
        self.assertEqual(game_state.budget_pool, game_state.available_funds)
        self.assertEqual(game_state.active_research[0].project_id, project.id)
        self.assertTrue(
            any(
                transaction.source == "research"
                for transaction in game_state.funds.transaction_history
            )
        )

    def test_starting_research_requires_available_funds(self):
        game_state = GameState()
        game_state.spend_funds(game_state.available_funds, "test", "empty ledger")

        started = game_state.start_research("power_armor_servo_prayer")

        self.assertFalse(started)
        self.assertEqual(game_state.active_research, [])

    def test_calendar_advances_active_research_and_unlocks_upgrade(self):
        game_state = GameState()
        project = game_state.research_tree.project("equipment_field_mender")
        self.assertTrue(game_state.start_research(project.id))

        game_state.advance_days(project.days_required, "research test")

        self.assertEqual(game_state.active_research, [])
        self.assertIn(project.id, game_state.completed_research)
        self.assertIn("equipment.field_mender", game_state.research_unlock_flags)
        self.assertEqual(game_state.research_stat_modifiers["medkit_quality"], 1)
        self.assertTrue(
            any("Research complete" in event for event in game_state.event_log)
        )

    def test_completed_research_serializes_through_game_state_save(self):
        game_state = GameState()
        project = game_state.research_tree.project("vehicle_silent_wheels")
        game_state.start_research(project.id)
        game_state.advance_days(project.days_required, "save test")

        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "savegame.json"
            game_state.save(str(save_path))
            loaded = GameState.load(str(save_path))

        self.assertIn(project.id, loaded.completed_research)
        self.assertIn("vehicles.silent_wheels", loaded.research_unlock_flags)
        self.assertEqual(loaded.research_stat_modifiers["vehicle_stealth"], 1)

    def test_research_lab_ui_lists_queue_and_start_actions(self):
        game_state = GameState()
        lines = build_research_lab_lines(game_state)
        actions = [action.key for action in actions_for_room("corp", "research")]

        self.assertTrue(any("Lab queue" in line for line in lines))
        self.assertTrue(any("funds" in line.lower() and "/" in line for line in lines))
        self.assertIn("start_research_0", actions)
        self.assertIn("start_research_1", actions)


if __name__ == "__main__":
    unittest.main()
