"""Pure combat action availability rules."""

import unittest

from game.character import Character
from game.combat_actions import available_combat_actions
from game.combat_system import create_asset_unit, create_player_units
from game.management.equipment import Weapon, default_equipment_catalog
from game.management.spec_ops_assets import ArmorRating, CombatRobot, WeaponHardpoint


def action_keys(unit):
    return [action.key for action in available_combat_actions(unit)]


class CombatActionsTest(unittest.TestCase):
    def test_ranged_agent_gets_fire_without_psi_or_missiles(self):
        catalog = default_equipment_catalog()
        agent = Character("Vega", role="sniper")
        agent.loadout.equip("primary_weapon", catalog["primary_weapon"][0])

        keys = action_keys(create_player_units([agent])[0])

        self.assertIn("move", keys)
        self.assertIn("fire", keys)
        self.assertIn("defend", keys)
        self.assertIn("end_turn", keys)
        self.assertNotIn("psi", keys)
        self.assertNotIn("missiles", keys)

    def test_psi_and_first_aid_are_contextual_agent_actions(self):
        catalog = default_equipment_catalog()
        agent = Character("Echo", role="psi")
        agent.loadout.equip("utility_item", catalog["utility_item"][0])
        agent.loadout.equip("psi_focus", catalog["psi_focus"][0])

        keys = action_keys(create_player_units([agent])[0])

        self.assertIn("psi", keys)
        self.assertIn("first_aid", keys)

    def test_melee_depends_on_close_weapon(self):
        blade = Weapon(
            "test_blade",
            "Test Blade",
            "primary_weapon",
            allowed_slots=("primary_weapon",),
            attack_stat="str",
            range_cells=1,
        )
        agent = Character("Knox")
        agent.loadout.equip("primary_weapon", blade)

        keys = action_keys(create_player_units([agent])[0])

        self.assertIn("melee", keys)
        self.assertNotIn("fire", keys)

    def test_medic_trait_unlocks_first_aid_without_item(self):
        agent = Character("Patch", traits=["first aid"])

        self.assertIn("first_aid", action_keys(create_player_units([agent])[0]))

    def test_robot_missiles_require_capacity(self):
        robot = CombatRobot(
            id="r1",
            name="Bulwark",
            armor=ArmorRating(plating=2),
            hardpoints=[WeaponHardpoint("Rail", range_cells=8)],
            missile_capacity=2,
        )
        keys = action_keys(create_asset_unit(robot, 0))
        robot.missile_capacity = 0
        no_missile_keys = action_keys(create_asset_unit(robot, 0))

        self.assertIn("fire", keys)
        self.assertIn("missiles", keys)
        self.assertNotIn("missiles", no_missile_keys)
        self.assertNotIn("psi", keys)
        self.assertNotIn("first_aid", keys)


if __name__ == "__main__":
    unittest.main()
