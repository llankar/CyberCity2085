"""Agent equipment loadout rules and combat integration."""

import unittest

from game.character import Character
from game.combat_system import create_player_units
from game.management.equipment import (
    AgentLoadout,
    Armor,
    EquipmentItem,
    Weapon,
    default_equipment_catalog,
)
from game.stats import PlayerStats


class AgentEquipmentTest(unittest.TestCase):
    def test_assigning_equipment_to_valid_slots_updates_loadout(self):
        loadout = AgentLoadout()
        rifle = Weapon(
            "test_rifle",
            "Test Rifle",
            "primary_weapon",
            {"agi": 1},
            allowed_slots=("primary_weapon",),
            range_cells=7,
            action_name="Test Burst",
        )
        armor = Armor(
            "test_armor",
            "Test Armor",
            "armor",
            {"max_hp": 3},
            allowed_slots=("armor",),
            mitigation=2,
        )

        self.assertIsNone(loadout.equip("primary_weapon", rifle))
        self.assertIsNone(loadout.equip("armor", armor))

        self.assertIs(loadout.primary_weapon, rifle)
        self.assertIs(loadout.armor, armor)
        self.assertEqual(loadout.total_stat_bonuses()["agi"], 1)
        self.assertEqual(loadout.total_stat_bonuses()["defense"], 2)
        self.assertIn("Test Burst", loadout.combat_actions())

    def test_replacing_equipment_returns_previous_item(self):
        loadout = AgentLoadout()
        first = Weapon("first", "First", "sidearm", allowed_slots=("sidearm",))
        second = Weapon("second", "Second", "sidearm", allowed_slots=("sidearm",))

        loadout.equip("sidearm", first)
        replaced = loadout.equip("sidearm", second)

        self.assertIs(replaced, first)
        self.assertIs(loadout.sidearm, second)

    def test_validating_equipment_rejects_wrong_slot_and_type(self):
        loadout = AgentLoadout()
        armor = Armor("coat", "Coat", "armor", allowed_slots=("armor",))
        utility = EquipmentItem("patch", "Patch", "utility_item")

        with self.assertRaises(ValueError):
            loadout.equip("primary_weapon", armor)
        with self.assertRaises(ValueError):
            loadout.equip("armor", utility)
        with self.assertRaises(ValueError):
            loadout.equip("unknown_slot", utility)

    def test_character_serializes_loadout_without_losing_item_types(self):
        catalog = default_equipment_catalog()
        character = Character("Echo")
        character.loadout.equip("primary_weapon", catalog["primary_weapon"][0])
        character.loadout.equip("armor", catalog["armor"][0])

        restored = Character.from_dict(character.to_dict())

        self.assertIsInstance(restored.loadout.primary_weapon, Weapon)
        self.assertIsInstance(restored.loadout.armor, Armor)
        self.assertEqual(restored.loadout.primary_weapon.name, "Pulse Rifle")
        self.assertEqual(restored.loadout.armor.name, "Kevlar Longcoat")

    def test_create_player_units_applies_weapon_and_armor_bonuses(self):
        character = Character("Kite", stats=PlayerStats(agi=2, defense=1))
        catalog = default_equipment_catalog()
        character.loadout.equip("primary_weapon", catalog["primary_weapon"][0])
        character.loadout.equip("armor", catalog["armor"][0])

        unit = create_player_units([character])[0]

        self.assertEqual(character.stats.agi, 2)
        self.assertGreater(unit.stats.agi, character.stats.agi)
        self.assertGreater(unit.stats.defense, character.stats.defense)
        self.assertEqual(unit.attack_range, 8)
        self.assertIn("Rifle Burst", unit.available_actions)

if __name__ == "__main__":
    unittest.main()
