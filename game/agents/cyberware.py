"""Compact cyberware catalogue and humanity-capacity rules."""

from __future__ import annotations

from dataclasses import dataclass

MAX_HUMANITY = 5
INELIGIBLE_ROLES = {"robot", "power_armor", "heavy_armor", "starver"}


@dataclass(frozen=True)
class Cyberware:
    id: str
    name: str
    zone: str
    power_tier: int
    humanity_cost: int
    credit_cost: int
    description: str
    combat_bonuses: dict[str, int]


CATALOGUE: tuple[Cyberware, ...] = (
    Cyberware("smart_eye", "Smart Targeting Eye", "EYES", 1, 1, 450, "Ballistic overlay corrects aim in real time.", {"aim": 2, "crit": 1}),
    Cyberware("tactical_coprocessor", "Tactical Co-processor", "HEAD", 3, 3, 2200, "A combat cache expands moment-to-moment options.", {"action_points": 1, "initiative": 1}),
    Cyberware("kerenzikov_reflex", "Kerenzikov Reflex", "NERVOUS SYSTEM", 2, 2, 1200, "Predictive nerves seize the first beat.", {"initiative": 4}),
    Cyberware("titan_arm", "Titan Cyberarm", "ARMS", 2, 2, 1100, "Reinforced myomers turn close combat brutal.", {"melee_power": 4}),
    Cyberware("subdermal_mesh", "Subdermal Armor Mesh", "TORSO", 2, 2, 1400, "Flexible plates harden beneath the skin.", {"defense": 2, "hp": 4}),
    Cyberware("adrenal_pump", "Adrenal Overdrive", "CIRCULATORY", 1, 1, 600, "Emergency pump sustains a wounded operator.", {"hp": 3, "initiative": 1}),
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


def purchase_or_remove(
    ids: object, cyberware_id: str, available_funds: int
) -> tuple[list[str], int, bool, str]:
    """Apply one clinic transaction without allowing negative funds or Humanity.

    Removal restores Humanity but does not refund surgery or hardware costs.
    """
    installed = normalize_installed(ids)
    item = BY_ID.get(cyberware_id)
    funds = max(0, int(available_funds))
    if item is None:
        return installed, funds, False, "unknown"
    if cyberware_id in installed:
        installed.remove(cyberware_id)
        return installed, funds, True, "removed"
    if item.humanity_cost > humanity_remaining(installed):
        return installed, funds, False, "humanity"
    if item.credit_cost > funds:
        return installed, funds, False, "funds"
    installed.append(cyberware_id)
    return installed, funds - item.credit_cost, True, "installed"


def combat_bonuses(ids: object) -> dict[str, int]:
    bonuses: dict[str, int] = {}
    for key in normalize_installed(ids):
        for stat, value in BY_ID[key].combat_bonuses.items():
            bonuses[stat] = bonuses.get(stat, 0) + value
    return bonuses


def is_eligible_role(role: str) -> bool:
    return str(role).lower() not in INELIGIBLE_ROLES
