"""Compact cyberware catalogue and humanity-capacity rules."""

from __future__ import annotations

from dataclasses import dataclass

MAX_HUMANITY = 5
INELIGIBLE_ROLES = {"robot", "power_armor", "heavy_armor", "starver"}


@dataclass(frozen=True)
class Cyberware:
    id: str
    name: str
    humanity_cost: int
    description: str
    combat_bonuses: dict[str, int]


CATALOGUE: tuple[Cyberware, ...] = (
    Cyberware("kerenzikov_reflex", "Kerenzikov Reflex", 2, "Predictive nerves seize the first beat.", {"initiative": 4}),
    Cyberware("smart_eye", "Smart Targeting Eye", 1, "Ballistic overlay corrects aim in real time.", {"aim": 2, "crit": 1}),
    Cyberware("subdermal_mesh", "Subdermal Armor Mesh", 2, "Flexible plates harden beneath the skin.", {"defense": 2, "hp": 4}),
    Cyberware("titan_arm", "Titan Cyberarm", 2, "Reinforced myomers turn close combat brutal.", {"melee_power": 4}),
    Cyberware("adrenal_pump", "Adrenal Overdrive", 1, "Emergency pump sustains a wounded operator.", {"hp": 3, "initiative": 1}),
    Cyberware("tactical_coprocessor", "Tactical Co-processor", 1, "A combat cache expands moment-to-moment options.", {"action_points": 1, "initiative": 1}),
)

BY_ID = {item.id: item for item in CATALOGUE}


def normalize_installed(ids: object) -> list[str]:
    if not isinstance(ids, (list, tuple)):
        return []
    result: list[str] = []
    for raw in ids:
        key = str(raw)
        if key in BY_ID and key not in result:
            result.append(key)
    return result


def humanity_remaining(ids: object) -> int:
    installed = normalize_installed(ids)
    return max(0, MAX_HUMANITY - sum(BY_ID[key].humanity_cost for key in installed))


def can_install(ids: object, cyberware_id: str) -> bool:
    installed = normalize_installed(ids)
    item = BY_ID.get(cyberware_id)
    return bool(item and cyberware_id not in installed and item.humanity_cost <= humanity_remaining(installed))


def toggle_cyberware(ids: object, cyberware_id: str) -> tuple[list[str], bool]:
    installed = normalize_installed(ids)
    if cyberware_id in installed:
        installed.remove(cyberware_id)
        return installed, True
    if not can_install(installed, cyberware_id):
        return installed, False
    installed.append(cyberware_id)
    return installed, True


def combat_bonuses(ids: object) -> dict[str, int]:
    bonuses: dict[str, int] = {}
    for key in normalize_installed(ids):
        for stat, value in BY_ID[key].combat_bonuses.items():
            bonuses[stat] = bonuses.get(stat, 0) + value
    return bonuses


def is_eligible_role(role: str) -> bool:
    return str(role).lower() not in INELIGIBLE_ROLES
