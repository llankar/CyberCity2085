"""Pure combat action availability rules for tactical UI.

The battle renderer consumes this module so action visibility stays testable
without importing Arcade or binding rules to draw code.
"""

from __future__ import annotations

from dataclasses import dataclass

from .management.equipment import EquipmentItem, Weapon
from .unit import Unit


@dataclass(frozen=True)
class CombatAction:
    """One contextual action exposed by the battle command bar."""

    key: str
    label: str
    icon: str
    hotkey: str = ""


def _item_tags(item: EquipmentItem | None) -> set[str]:
    return {tag.lower() for tag in item.tags} if item else set()


def _is_medical_item(item: EquipmentItem | None) -> bool:
    if item is None:
        return False
    text = f"{item.id} {item.name}".lower()
    return "medical" in _item_tags(item) or "medkit" in text or "trauma" in text


def _weapon_supports_fire(weapon: Weapon | None) -> bool:
    return bool(weapon and (weapon.range_cells > 1 or weapon.attack_stat == "agi"))


def _weapon_supports_melee(weapon: Weapon | None) -> bool:
    return bool(weapon and (weapon.range_cells <= 1 or weapon.attack_stat == "str"))


def unit_can_fire(unit: Unit) -> bool:
    """Return whether the unit has an equipped ranged weapon or hardpoint."""
    if unit.spec_ops_asset:
        return any(
            hardpoint.range_cells > 1 or hardpoint.attack_stat == "agi"
            for hardpoint in unit.spec_ops_asset.hardpoints
        )
    loadout = unit.character.loadout if unit.character else None
    return bool(
        loadout
        and (
            _weapon_supports_fire(loadout.primary_weapon)
            or _weapon_supports_fire(loadout.sidearm)
        )
    )


def unit_can_melee(unit: Unit) -> bool:
    """Return whether the unit has a close-quarters weapon or hardpoint."""
    if unit.spec_ops_asset:
        return any(
            hardpoint.range_cells <= 1 or hardpoint.attack_stat == "str"
            for hardpoint in unit.spec_ops_asset.hardpoints
        )
    loadout = unit.character.loadout if unit.character else None
    return bool(
        loadout
        and (
            _weapon_supports_melee(loadout.primary_weapon)
            or _weapon_supports_melee(loadout.sidearm)
        )
    )


def unit_can_use_psi(unit: Unit) -> bool:
    """Return whether an agent has psi training or a psi focus equipped."""
    if not unit.character:
        return False
    loadout = unit.character.loadout
    return (
        unit.character.role == "psi"
        or bool(loadout.psi_focus)
        or "psi" in {trait.lower() for trait in unit.character.traits}
    )


def unit_can_first_aid(unit: Unit) -> bool:
    """Return whether an agent carries medical gear or has medic training."""
    if not unit.character:
        return False
    character = unit.character
    loadout = character.loadout
    skill_markers = {
        character.role.lower(),
        *(trait.lower() for trait in character.traits),
    }
    return (
        "medic" in skill_markers
        or "first aid" in skill_markers
        or _is_medical_item(loadout.utility_item)
        or any("medical" in _item_tags(item) for item in loadout.equipped_items())
    )


def unit_can_use_missiles(unit: Unit) -> bool:
    """Return whether a support asset has missile capacity."""
    return bool(unit.spec_ops_asset and unit.spec_ops_asset.missile_capacity > 0)


def available_combat_actions(unit: Unit | None) -> list[CombatAction]:
    """Build ordered, contextual combat actions for the selected unit."""
    if unit is None or unit.health <= 0:
        return []

    actions = [CombatAction("move", "Move", "radar", "Arrows")]
    if unit_can_fire(unit):
        actions.append(CombatAction("fire", "Fire", "armory", "F"))
    if unit_can_melee(unit):
        actions.append(CombatAction("melee", "Melee", "black_ops", "Space"))
    if unit_can_use_psi(unit):
        actions.append(CombatAction("psi", "Psi", "research", "P"))
    if unit_can_first_aid(unit):
        actions.append(CombatAction("first_aid", "First Aid", "medbay", "A"))
    if unit_can_use_missiles(unit):
        actions.append(CombatAction("missiles", "Missiles", "launch", "M"))
    actions.extend(
        [
            CombatAction("defend", "Defend", "shield", "D"),
            CombatAction("end_turn", "End Turn", "right", "Enter"),
        ]
    )
    return actions
