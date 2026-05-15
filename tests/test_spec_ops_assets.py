"""Spec-ops robot and power armor support assets."""

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
from game.management.spec_ops_assets import (
    ArmorRating,
    CombatRobot,
    MaintenanceState,
    PowerArmorSuit,
    WeaponHardpoint,
)


class SpecOpsAssetsTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
