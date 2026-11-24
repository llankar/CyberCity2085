"""Research management projects, calendar progress, and unlock application."""

import tempfile
import unittest
from pathlib import Path

from game.gamestate import GameState
from game.management.research import RESEARCH_CATEGORIES, create_starter_research_tree
from game.management.equipment import AVAILABILITY_RESEARCH, default_equipment_catalog
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

    def test_starter_tree_has_at_least_twenty_projects_across_branches(self):
        tree = create_starter_research_tree()

        self.assertGreaterEqual(len(tree.projects), 20)
        for category in RESEARCH_CATEGORIES:
            self.assertGreaterEqual(len(tree.projects_for_category(category)), 3)

    def test_research_costs_use_the_current_strategic_economy_scale(self):
        tree = create_starter_research_tree()

        # Ordinary victories now pay at least roughly 1,300-2,000 funds.  Entry
        # research must remain approachable while late prototypes compete with
        # equipment purchases and long-term Hangar expansion.
        self.assertGreaterEqual(min(p.funds_cost for p in tree.projects.values()), 600)
        self.assertGreaterEqual(max(p.funds_cost for p in tree.projects.values()), 5_000)
        self.assertEqual(tree.project("weapon_smartlink_mk1").funds_cost, 800)
        self.assertEqual(tree.project("weapon_corporate_rail_lattice").funds_cost, 2_000)
        self.assertEqual(tree.project("weapon_oracle_killchain").funds_cost, 4_000)
        self.assertEqual(tree.project("weapon_arc_conduction").funds_cost, 1_800)
        self.assertEqual(tree.project("weapon_plasma_miniaturization").funds_cost, 3_200)
        self.assertEqual(tree.project("weapon_gravity_distortion").funds_cost, 6_500)

    def test_weapon_branch_covers_every_advanced_weapon_with_meaningful_projects(self):
        tree = create_starter_research_tree()
        weapon_projects = tree.projects_for_category("weapons")
        self.assertEqual(len(weapon_projects), 6)
        expected = {
            "arc_caster": "weapon_arc_conduction",
            "combat_shotgun": "weapon_corporate_rail_lattice",
            "micro_uzi": "weapon_corporate_rail_lattice",
            "sniper_rifle": "weapon_oracle_killchain",
            "heavy_pistol": "weapon_oracle_killchain",
            "plasma_pistol": "weapon_plasma_miniaturization",
            "gravity_lance": "weapon_gravity_distortion",
        }
        actual = {
            item_id: project.id
            for project in weapon_projects
            for item_id in project.unlocked_equipment_ids
        }
        self.assertEqual(actual, expected)
        self.assertEqual(
            tree.project("weapon_gravity_distortion").requires,
            ("weapon_oracle_killchain", "weapon_arc_conduction"),
        )

    def test_every_research_equipment_is_listed_by_exactly_one_real_project(self):
        tree = create_starter_research_tree()
        research_items = {
            item.id: item.research_project_id
            for items in default_equipment_catalog().values()
            for item in items
            if item.availability_group == AVAILABILITY_RESEARCH
        }
        listed = {}
        for project in tree.projects.values():
            for item_id in project.unlocked_equipment_ids:
                self.assertNotIn(item_id, listed)
                listed[item_id] = project.id
        self.assertEqual(listed, research_items)

    def test_research_completion_unlocks_purchase_right_but_grants_no_item(self):
        state = GameState()
        project = next(
            project
            for project in state.research_tree.projects.values()
            if project.unlocked_equipment_ids
        )
        before = dict(state.owned_equipment)
        state.completed_research.append(project.id)
        self.assertEqual(state.owned_equipment, before)
        item_id = project.unlocked_equipment_ids[0]
        item = next(
            item
            for items in default_equipment_catalog().values()
            for item in items
            if item.id == item_id
        )
        state.funds.current_funds = 100_000
        self.assertTrue(state.purchase_equipment(item)[0])

    def test_starting_research_pays_cost_and_queues_project(self):
        game_state = GameState()
        project = game_state.research_tree.project("weapon_smartlink_mk1")
        game_state.funds.current_funds = project.funds_cost + 500
        game_state.budget_pool = game_state.funds.current_funds
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
        game_state.funds.current_funds = project.funds_cost
        game_state.budget_pool = game_state.funds.current_funds
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
        game_state.funds.current_funds = project.funds_cost
        game_state.budget_pool = game_state.funds.current_funds
        game_state.start_research(project.id)
        game_state.advance_days(project.days_required, "save test")

        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "savegame.json"
            game_state.save(str(save_path))
            loaded = GameState.load(str(save_path))

        self.assertIn(project.id, loaded.completed_research)
        self.assertIn("vehicles.silent_wheels", loaded.research_unlock_flags)
        self.assertEqual(loaded.research_stat_modifiers["vehicle_stealth"], 1)

    def test_research_tree_contains_branching_projects_with_prerequisites(self):
        tree = create_starter_research_tree()

        doctrine = tree.project("robot_hunter_killer_doctrine")
        praetorian = tree.project("power_armor_praetorian_frame")

        self.assertEqual(doctrine.requires, ("robot_loyalty_kernel", "weapon_smartlink_mk1"))
        self.assertEqual(praetorian.requires, ("power_armor_servo_prayer", "armor_reactive_lining"))

    def test_research_lab_ui_lists_queue_and_start_actions(self):
        game_state = GameState()
        lines = build_research_lab_lines(game_state)
        actions = [action.key for action in actions_for_room("corp", "research")]

        self.assertTrue(any("Lab queue" in line for line in lines))
        self.assertTrue(any(line.startswith("Research tree:") for line in lines))
        self.assertIn("start_research_0", actions)
        self.assertIn("start_research_1", actions)


    def test_research_lab_ui_displays_all_available_branches_without_ellipsis(self):
        game_state = GameState()

        lines = build_research_lab_lines(game_state)

        self.assertFalse(any("…more branches available" in line for line in lines))
        self.assertGreaterEqual(len(lines), 10)

    def test_research_lab_ui_shows_completed_and_available_tree_states(self):
        game_state = GameState()
        starter = game_state.research_tree.project("weapon_smartlink_mk1")
        self.assertIsNotNone(starter)
        game_state.completed_research.append(starter.id)

        lines = build_research_lab_lines(game_state)

        self.assertTrue(any("✓" in line for line in lines))
        self.assertTrue(any("○" in line for line in lines))


if __name__ == "__main__":
    unittest.main()
