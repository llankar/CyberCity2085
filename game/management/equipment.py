"""Small equipment models for agent loadouts.

Equipment is intentionally data-only: characters own a loadout, while combat
systems decide how those items become tactical stats or actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field

EQUIPMENT_SLOTS = (
    "primary_weapon",
    "sidearm",
    "armor",
    "utility_item",
    "psi_focus",
    "special_gear",
)

COMBAT_STAT_KEYS = ("defense", "psi", "str", "agi", "con", "hp", "max_hp")


@dataclass(frozen=True)
class EquipmentItem:
    """Base item that can be assigned to one or more agent equipment slots."""

    id: str
    name: str
    slot: str
    stat_bonuses: dict[str, int] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    description: str = ""
    allowed_slots: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        slots = self.allowed_slots or (self.slot,)
        invalid_slots = [slot for slot in slots if slot not in EQUIPMENT_SLOTS]
        if self.slot not in EQUIPMENT_SLOTS:
            invalid_slots.append(self.slot)
        if invalid_slots:
            raise ValueError(f"Unknown equipment slot: {invalid_slots[0]}")
        invalid_stats = [key for key in self.stat_bonuses if key not in COMBAT_STAT_KEYS]
        if invalid_stats:
            raise ValueError(f"Unknown equipment stat bonus: {invalid_stats[0]}")
        object.__setattr__(self, "allowed_slots", tuple(slots))
        object.__setattr__(self, "tags", list(self.tags))
        object.__setattr__(self, "stat_bonuses", dict(self.stat_bonuses))

    def can_equip_to(self, slot: str) -> bool:
        """Return whether this item fits the requested loadout slot."""
        return slot in self.allowed_slots

    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "id": self.id,
            "name": self.name,
            "slot": self.slot,
            "stat_bonuses": dict(self.stat_bonuses),
            "tags": list(self.tags),
            "description": self.description,
            "allowed_slots": list(self.allowed_slots),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EquipmentItem":
        item_type = data.get("type", "EquipmentItem")
        item_cls = {"Weapon": Weapon, "Armor": Armor}.get(item_type, EquipmentItem)
        if item_cls is Weapon:
            return Weapon(
                id=data.get("id", "unknown_weapon"),
                name=data.get("name", "Unknown weapon"),
                slot=data.get("slot", "primary_weapon"),
                stat_bonuses=dict(data.get("stat_bonuses", {})),
                tags=list(data.get("tags", [])),
                description=data.get("description", ""),
                allowed_slots=tuple(data.get("allowed_slots", []) or ()),
                attack_stat=data.get("attack_stat", "agi"),
                damage_bonus=data.get("damage_bonus", 0),
                range_cells=data.get("range_cells", 1),
                action_name=data.get("action_name", "Attack"),
            )
        if item_cls is Armor:
            return Armor(
                id=data.get("id", "unknown_armor"),
                name=data.get("name", "Unknown armor"),
                slot=data.get("slot", "armor"),
                stat_bonuses=dict(data.get("stat_bonuses", {})),
                tags=list(data.get("tags", [])),
                description=data.get("description", ""),
                allowed_slots=tuple(data.get("allowed_slots", []) or ()),
                mitigation=data.get("mitigation", 0),
            )
        return cls(
            id=data.get("id", "unknown_item"),
            name=data.get("name", "Unknown item"),
            slot=data.get("slot", "utility_item"),
            stat_bonuses=dict(data.get("stat_bonuses", {})),
            tags=list(data.get("tags", [])),
            description=data.get("description", ""),
            allowed_slots=tuple(data.get("allowed_slots", []) or ()),
        )


@dataclass(frozen=True)
class Weapon(EquipmentItem):
    """Weapon data used by combat setup to expose an attack option."""

    attack_stat: str = "agi"
    damage_bonus: int = 0
    range_cells: int = 1
    action_name: str = "Attack"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.attack_stat not in {"str", "agi", "psi"}:
            raise ValueError(f"Unsupported weapon attack stat: {self.attack_stat}")
        if self.range_cells < 1:
            raise ValueError("Weapon range must be at least 1 cell")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(
            {
                "attack_stat": self.attack_stat,
                "damage_bonus": self.damage_bonus,
                "range_cells": self.range_cells,
                "action_name": self.action_name,
            }
        )
        return data


@dataclass(frozen=True)
class Armor(EquipmentItem):
    """Armor data used by combat setup to increase survivability."""

    mitigation: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.slot != "armor" or not self.can_equip_to("armor"):
            raise ValueError("Armor must be equippable to the armor slot")
        if self.mitigation < 0:
            raise ValueError("Armor mitigation cannot be negative")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["mitigation"] = self.mitigation
        return data


@dataclass
class AgentLoadout:
    """Equipment assigned to an agent, keyed by explicit loadout slot."""

    primary_weapon: Weapon | None = None
    sidearm: Weapon | None = None
    armor: Armor | None = None
    utility_item: EquipmentItem | None = None
    psi_focus: EquipmentItem | None = None
    special_gear: EquipmentItem | None = None

    def item_for_slot(self, slot: str) -> EquipmentItem | None:
        self._validate_slot_name(slot)
        return getattr(self, slot)

    def equip(self, slot: str, item: EquipmentItem | None) -> EquipmentItem | None:
        """Assign an item to a slot, returning the replaced item if any."""
        self._validate_slot_name(slot)
        if item is not None and not item.can_equip_to(slot):
            raise ValueError(f"{item.name} cannot be equipped to {slot}")
        if (
            slot in {"primary_weapon", "sidearm"}
            and item is not None
            and not isinstance(item, Weapon)
        ):
            raise ValueError(f"{slot} requires a Weapon")
        if slot == "armor" and item is not None and not isinstance(item, Armor):
            raise ValueError("armor requires Armor")
        previous = getattr(self, slot)
        setattr(self, slot, item)
        return previous

    def equipped_items(self) -> list[EquipmentItem]:
        """Return currently assigned items in stable slot order."""
        return [item for slot in EQUIPMENT_SLOTS if (item := getattr(self, slot))]

    def total_stat_bonuses(self) -> dict[str, int]:
        """Aggregate all stat bonuses from equipped items."""
        totals: dict[str, int] = {}
        for item in self.equipped_items():
            for stat_key, amount in item.stat_bonuses.items():
                totals[stat_key] = totals.get(stat_key, 0) + amount
            if isinstance(item, Weapon) and item.damage_bonus:
                totals[item.attack_stat] = (
                    totals.get(item.attack_stat, 0) + item.damage_bonus
                )
            if isinstance(item, Armor) and item.mitigation:
                totals["defense"] = totals.get("defense", 0) + item.mitigation
        return totals

    def combat_actions(self) -> list[str]:
        """Describe equipment-provided actions for UI and battle setup."""
        actions = ["Move", "Defend"]
        for weapon in (self.primary_weapon, self.sidearm):
            if weapon:
                actions.append(weapon.action_name)
        if self.psi_focus:
            actions.append("Psi Focus")
        if self.utility_item:
            actions.append(self.utility_item.name)
        return actions

    def summary_lines(self) -> list[str]:
        """Build compact human-readable slot lines for management UI."""
        lines = []
        for slot in EQUIPMENT_SLOTS:
            item = getattr(self, slot)
            label = slot.replace("_", " ").title()
            lines.append(f"{label}: {item.name if item else 'Empty'}")
        return lines

    def to_dict(self) -> dict:
        return {
            slot: (getattr(self, slot).to_dict() if getattr(self, slot) else None)
            for slot in EQUIPMENT_SLOTS
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "AgentLoadout":
        loadout = cls()
        if not data:
            return loadout
        for slot in EQUIPMENT_SLOTS:
            item_data = data.get(slot)
            if item_data:
                loadout.equip(slot, EquipmentItem.from_dict(item_data))
        return loadout

    @staticmethod
    def _validate_slot_name(slot: str) -> None:
        if slot not in EQUIPMENT_SLOTS:
            raise ValueError(f"Unknown equipment slot: {slot}")


def default_equipment_catalog() -> dict[str, list[EquipmentItem]]:
    """Return a tiny starter catalog for barracks assignment actions."""
    return {
        "primary_weapon": [
            Weapon(
                "pulse_rifle",
                "Pulse Rifle",
                "primary_weapon",
                {"agi": 1},
                ["rifle"],
                "Reliable mid-range corp rifle.",
                ("primary_weapon",),
                attack_stat="agi",
                damage_bonus=1,
                range_cells=8,
                action_name="Rifle Burst",
            ),
            Weapon(
                "monoblade",
                "Monoblade",
                "primary_weapon",
                {"str": 1},
                ["blade"],
                "Close combat blade with a memory edge.",
                ("primary_weapon",),
                attack_stat="str",
                damage_bonus=1,
                range_cells=1,
                action_name="Blade Strike",
            ),
        ],
        "sidearm": [
            Weapon(
                "shock_pistol",
                "Shock Pistol",
                "sidearm",
                {"agi": 1},
                ["pistol"],
                "Compact backup weapon.",
                ("sidearm",),
                attack_stat="agi",
                damage_bonus=0,
                range_cells=5,
                action_name="Pistol Shot",
            )
        ],
        "armor": [
            Armor(
                "kevlar_longcoat",
                "Kevlar Longcoat",
                "armor",
                {"max_hp": 2},
                ["coat"],
                "Armored street coat with hidden plates.",
                ("armor",),
                mitigation=1,
            )
        ],
        "utility_item": [
            EquipmentItem(
                "trauma_patch",
                "Trauma Patch",
                "utility_item",
                {"hp": 1},
                ["medical"],
                "Emergency stabilizer carried into the zone.",
            )
        ],
        "psi_focus": [
            EquipmentItem(
                "echo_implant",
                "Echo Implant",
                "psi_focus",
                {"psi": 2},
                ["implant", "psi"],
                "Whispering wetware focus for psi agents.",
            )
        ],
        "special_gear": [
            EquipmentItem(
                "ghost_cloak",
                "Ghost Cloak",
                "special_gear",
                {"defense": 1},
                ["stealth"],
                "Corporate prototype optical smear.",
            )
        ],
    }
