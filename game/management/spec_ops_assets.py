"""Compact spec-ops asset models for robots and power armor.

These assets support agents without taking over the emotional center of the
squad: they are deployable tools with repair bills, not replacement heroes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..stats import PlayerStats
from .funds import CorporateFunds


@dataclass(frozen=True)
class WeaponHardpoint:
    """A mounted weapon slot on a combat asset."""

    name: str
    attack_stat: str = "agi"
    damage_bonus: int = 0
    range_cells: int = 1
    action_name: str = "Fire"

    def __post_init__(self) -> None:
        if self.attack_stat not in {"str", "agi", "psi"}:
            raise ValueError(f"Unsupported hardpoint attack stat: {self.attack_stat}")
        if self.range_cells < 1:
            raise ValueError("Hardpoint range must be at least 1 cell")
        if self.damage_bonus < 0:
            raise ValueError("Hardpoint damage bonus cannot be negative")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "attack_stat": self.attack_stat,
            "damage_bonus": self.damage_bonus,
            "range_cells": self.range_cells,
            "action_name": self.action_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WeaponHardpoint":
        return cls(
            name=str(data.get("name", "Hardpoint")),
            attack_stat=str(data.get("attack_stat", "agi")),
            damage_bonus=int(data.get("damage_bonus", 0)),
            range_cells=int(data.get("range_cells", 1)),
            action_name=str(data.get("action_name", "Fire")),
        )


@dataclass(frozen=True)
class ArmorRating:
    """Protection profile for a robotic or armored support asset."""

    plating: int = 1
    sealed_systems: int = 0

    def __post_init__(self) -> None:
        if self.plating < 0 or self.sealed_systems < 0:
            raise ValueError("Armor ratings cannot be negative")

    @property
    def defense_bonus(self) -> int:
        return self.plating + self.sealed_systems

    def to_dict(self) -> dict:
        return {"plating": self.plating, "sealed_systems": self.sealed_systems}

    @classmethod
    def from_dict(cls, data: dict) -> "ArmorRating":
        return cls(
            plating=int(data.get("plating", 1)),
            sealed_systems=int(data.get("sealed_systems", 0)),
        )


@dataclass
class MaintenanceState:
    """Readiness and repair cost state for a spec-ops asset."""

    integrity: int = 100
    repair_cost_per_damage: int = 1
    base_upkeep: int = 1

    def __post_init__(self) -> None:
        self.integrity = max(0, min(int(self.integrity), 100))
        self.repair_cost_per_damage = max(0, int(self.repair_cost_per_damage))
        self.base_upkeep = max(0, int(self.base_upkeep))

    @property
    def can_deploy(self) -> bool:
        return self.integrity >= 50

    @property
    def damage(self) -> int:
        return max(0, 100 - self.integrity)

    @property
    def repair_cost(self) -> int:
        return self.damage * self.repair_cost_per_damage

    @property
    def maintenance_cost(self) -> int:
        return self.base_upkeep + self.repair_cost

    def mark_repaired(self) -> None:
        self.integrity = 100

    def to_dict(self) -> dict:
        return {
            "integrity": self.integrity,
            "repair_cost_per_damage": self.repair_cost_per_damage,
            "base_upkeep": self.base_upkeep,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MaintenanceState":
        return cls(
            integrity=int(data.get("integrity", 100)),
            repair_cost_per_damage=int(data.get("repair_cost_per_damage", 1)),
            base_upkeep=int(data.get("base_upkeep", 1)),
        )


@dataclass
class SpecOpsAsset:
    """Base model shared by robots and power armor suits."""

    id: str
    name: str
    asset_type: str
    armor: ArmorRating = field(default_factory=ArmorRating)
    hardpoints: list[WeaponHardpoint] = field(default_factory=list)
    missile_capacity: int = 0
    maintenance: MaintenanceState = field(default_factory=MaintenanceState)
    pilot_required: bool = False
    action_points: int = 2

    @property
    def display_role(self) -> str:
        return self.asset_type.replace("_", " ")

    @property
    def is_deployable(self) -> bool:
        return self.maintenance.can_deploy

    @property
    def primary_range(self) -> int:
        if not self.hardpoints:
            return 1
        return max(hardpoint.range_cells for hardpoint in self.hardpoints)

    @property
    def combat_actions(self) -> list[str]:
        actions = ["Move", "Defend"]
        actions.extend(hardpoint.action_name for hardpoint in self.hardpoints)
        if self.missile_capacity > 0:
            actions.append("Missile Salvo")
        return actions

    def combat_stats(self) -> PlayerStats:
        level = 1 + self.armor.defense_bonus // 3
        strongest = max((hardpoint.damage_bonus for hardpoint in self.hardpoints), default=0)
        stats = PlayerStats(
            level=max(1, level),
            defense=max(1, self.armor.defense_bonus),
            psi=0,
            str=max(1, 2 + strongest),
            agi=max(1, 2 + len(self.hardpoints)),
            con=max(1, 2 + self.armor.plating),
        )
        stats.hp = max(1, int(stats.max_hp * self.maintenance.integrity / 100))
        return stats

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "asset_type": self.asset_type,
            "armor": self.armor.to_dict(),
            "hardpoints": [hardpoint.to_dict() for hardpoint in self.hardpoints],
            "missile_capacity": self.missile_capacity,
            "maintenance": self.maintenance.to_dict(),
            "pilot_required": self.pilot_required,
            "action_points": self.action_points,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SpecOpsAsset":
        asset_type = str(data.get("asset_type", "combat_robot"))
        asset_cls: type[SpecOpsAsset]
        if asset_type == "power_armor":
            asset_cls = PowerArmorSuit
        elif asset_type == "combat_robot":
            asset_cls = CombatRobot
        else:
            asset_cls = cls
        return asset_cls(
            id=str(data.get("id", "asset")),
            name=str(data.get("name", "Spec-Ops Asset")),
            armor=ArmorRating.from_dict(data.get("armor", {})),
            hardpoints=[
                WeaponHardpoint.from_dict(hardpoint)
                for hardpoint in data.get("hardpoints", [])
            ],
            missile_capacity=int(data.get("missile_capacity", 0)),
            maintenance=MaintenanceState.from_dict(data.get("maintenance", {})),
            pilot_required=bool(data.get("pilot_required", False)),
            action_points=int(data.get("action_points", 2)),
        )


@dataclass
class CombatRobot(SpecOpsAsset):
    """Autonomous combat robot that can deploy beside agents."""

    asset_type: str = "combat_robot"
    pilot_required: bool = False


@dataclass
class PowerArmorSuit(SpecOpsAsset):
    """Power armor suit that needs an agent pilot in the selected team."""

    asset_type: str = "power_armor"
    pilot_required: bool = True


def default_spec_ops_assets() -> list[SpecOpsAsset]:
    """Return a tiny starting pool for tests and future campaign hooks."""
    return [
        CombatRobot(
            id="robot_k9_01",
            name="K-9 Breacher Drone",
            armor=ArmorRating(plating=2, sealed_systems=1),
            hardpoints=[WeaponHardpoint("Shock Carbine", damage_bonus=1, range_cells=4, action_name="Shock Carbine")],
            missile_capacity=1,
            maintenance=MaintenanceState(base_upkeep=2),
        ),
        PowerArmorSuit(
            id="armor_aegis_01",
            name="Aegis Mantis Suit",
            armor=ArmorRating(plating=4, sealed_systems=1),
            hardpoints=[WeaponHardpoint("Servo Fist", attack_stat="str", damage_bonus=2, range_cells=1, action_name="Servo Strike")],
            missile_capacity=2,
            maintenance=MaintenanceState(base_upkeep=3),
        ),
    ]


def maintenance_cost_for_assets(assets: list[SpecOpsAsset]) -> int:
    """Total upkeep and repair cost for the supplied assets."""
    return sum(asset.maintenance.maintenance_cost for asset in assets)


def pay_asset_maintenance(funds: CorporateFunds, assets: list[SpecOpsAsset]) -> int:
    """Charge the funds ledger and restore asset integrity when affordable."""
    cost = maintenance_cost_for_assets(assets)
    if cost <= 0:
        return 0
    if not funds.spend_funds(cost, "spec_ops_maintenance", "Robot and power armor repair cycle."):
        return 0
    for asset in assets:
        asset.maintenance.mark_repaired()
    return cost
