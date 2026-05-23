"""Spec-ops robot and power armor support assets."""

import os
import tempfile
import unittest

from game.character import Character
from game.combat_system import create_player_units
from game.deployment import (
    deployable_assets,
    sanitize_selected_asset_ids,
    selected_deployment_manifest,
    toggle_asset_selection,
)
from game.gamestate import GameState
from game.management.research import advance_research_days
from game.management.spec_ops_assets import (
    ArmorRating,
    CombatRobot,
    MaintenanceState,
    PowerArmorSuit,
    WeaponHardpoint,
)


class SpecOpsAssetsTest(unittest.TestCase):
    def test_unlock_path_research_to_available_asset_project(self):
        state = GameState()
        project = state.research_tree.project("power_armor_servo_prayer")
        self.assertTrue(state.start_research(project.id))
        advance_research_days(state, project.days_required, state.research_tree)
        self.assertIn(project.id, state.completed_research)
        self.assertTrue(
            any(
                "power_armor" in p.category
                for p in state.research_tree.projects.values()
            )
        )

    def test_create_combat_robot_and_power_armor_models(self):
        robot = CombatRobot(
            id="drone_01",
            name="K-9 Breacher",
            armor=ArmorRating(plating=2, sealed_systems=1),
            hardpoints=[WeaponHardpoint("Shock Carbine", damage_bonus=1, range_cells=4)],
            missile_capacity=2,
        )
        suit = PowerArmorSuit(id="suit_01", name="Mantis Suit")

        self.assertEqual(robot.asset_type, "combat_robot")
        self.assertFalse(robot.pilot_required)
        self.assertEqual(robot.armor.defense_bonus, 3)
        self.assertEqual(robot.primary_range, 4)
        self.assertIn("Missile Salvo", robot.combat_actions)
        self.assertTrue(suit.pilot_required)


    def test_toggle_asset_selection_adds_ready_support_without_agent_selection(self):
        robot = CombatRobot(id="drone", name="Drone")

        selected_ids, message = toggle_asset_selection([robot], [])

        self.assertEqual(selected_ids, ["drone"])
        self.assertEqual(message, "Drone added as support asset.")

    def test_deployment_eligibility_requires_readiness_and_pilot_when_needed(self):
        agent = Character("Vega")
        robot = CombatRobot(id="drone", name="Drone")
        damaged = CombatRobot(
            id="wreck", name="Wreck", maintenance=MaintenanceState(integrity=40)
        )
        suit = PowerArmorSuit(id="armor", name="Armor")

        self.assertEqual(deployable_assets([robot, damaged, suit], []), [robot])
        self.assertEqual(deployable_assets([robot, damaged, suit], [agent]), [robot, suit])
        self.assertEqual(
            sanitize_selected_asset_ids([robot, damaged, suit], ["wreck", "armor", "armor"], [agent]),
            ["armor"],
        )

    def test_power_armor_pilot_is_replaced_in_mission_manifest(self):
        vega = Character("Vega")
        nova = Character("Nova")
        suit = PowerArmorSuit(id="armor", name="Armor", pilot_agent_name="Vega")

        manifest = selected_deployment_manifest(
            [vega, nova], ["Vega", "Nova"], [suit], ["armor"]
        )

        self.assertEqual([agent.name for agent in manifest.agents], ["Nova"])
        self.assertEqual(manifest.assets, [suit])

    def test_selected_deployment_manifest_includes_agents_robots_and_power_armor(self):
        agent = Character("Vega")
        robot = CombatRobot(id="drone", name="Drone")
        suit = PowerArmorSuit(id="armor", name="Armor")

        manifest = selected_deployment_manifest(
            [agent], ["Vega"], [robot, suit], ["drone", "armor"]
        )

        self.assertEqual(manifest.agents, [agent])
        self.assertEqual(manifest.assets, [robot, suit])
        self.assertTrue(manifest.has_units)

    def test_combat_unit_conversion_uses_distinct_asset_stats_actions_and_equipment(self):
        agent = Character("Vega")
        robot = CombatRobot(
            id="drone",
            name="Drone",
            armor=ArmorRating(plating=3, sealed_systems=1),
            hardpoints=[WeaponHardpoint("Rail Stubber", damage_bonus=2, range_cells=5, action_name="Rail Burst")],
            missile_capacity=1,
        )

        units = create_player_units([agent], ["Vega"], [robot], ["drone"])

        self.assertEqual(len(units), 2)
        self.assertEqual(units[0].unit_type, "agent")
        self.assertIs(units[1].spec_ops_asset, robot)
        self.assertEqual(units[1].unit_type, "combat_robot")
        self.assertEqual(units[1].attack_range, 5)
        self.assertIn("Rail Burst", units[1].available_actions)
        self.assertIn("Missile Salvo", units[1].available_actions)
        self.assertIn("Rail Stubber", units[1].equipment_summary)
        self.assertGreater(units[1].stats.defense, units[0].stats.defense)

    def test_maintenance_costs_spend_funds_and_restore_integrity(self):
        robot = CombatRobot(
            id="drone",
            name="Drone",
            maintenance=MaintenanceState(
                integrity=80, repair_cost_per_damage=2, base_upkeep=3
            ),
        )
        state = GameState(spec_ops_assets=[robot])
        starting_funds = state.available_funds

        paid = state.service_spec_ops_assets()

        self.assertEqual(paid, 43)
        self.assertEqual(state.available_funds, starting_funds - 43)
        self.assertEqual(robot.maintenance.integrity, 100)
        self.assertEqual(state.funds.transaction_history[-1].source, "spec_ops_maintenance")

    def test_asset_outcome_state_persists_after_save_load(self):
        robot = CombatRobot(id="drone", name="Drone")
        state = GameState(spec_ops_assets=[robot])
        state.latest_spec_ops_outcomes = [
            {"id": "drone", "name": "Drone", "damage": 35, "repair_cost": 70, "cooldown_days": 1}
        ]
        robot.maintenance.cooldown_days = 1
        robot.maintenance.integrity = 65

        # Windows holds an exclusive lock on NamedTemporaryFile while it's open,
        # so we use delete=False and clean up manually after the round-trip.
        tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        try:
            tmp.close()
            state.save(tmp.name)
            restored = GameState.load(tmp.name)
        finally:
            os.unlink(tmp.name)

        self.assertEqual(restored.latest_spec_ops_outcomes[0]["damage"], 35)
        self.assertEqual(restored.spec_ops_assets[0].maintenance.cooldown_days, 1)
        self.assertEqual(restored.spec_ops_assets[0].maintenance.integrity, 65)


if __name__ == "__main__":
    unittest.main()
