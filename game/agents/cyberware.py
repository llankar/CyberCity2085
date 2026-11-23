"""Compact cyberware catalogue and humanity-capacity rules."""

from __future__ import annotations

from dataclasses import dataclass

MAX_HUMANITY = 5
INELIGIBLE_ROLES = {"robot", "power_armor", "heavy_armor", "starver"}
ZONE_ORDER = ("HEAD", "EYES", "ARMS", "TORSO", "CIRCULATORY", "NERVOUS SYSTEM")


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
    Cyberware("mnemonic_buffer", "Mnemonic Combat Buffer", "HEAD", 1, 1, 550, "A compact threat cache sharpens first reactions.", {"initiative": 2}),
    Cyberware("tactical_coprocessor", "Tactical Co-processor", "HEAD", 3, 3, 2200, "A combat cache expands moment-to-moment options.", {"action_points": 1, "initiative": 1}),
    Cyberware("smart_eye", "Smart Targeting Eye", "EYES", 1, 1, 450, "Ballistic overlay corrects aim in real time.", {"aim": 2, "crit": 1}),
    Cyberware("predator_optics", "Predator Optics", "EYES", 2, 2, 1350, "Multispectral acquisition exposes lethal openings.", {"aim": 3, "crit": 2}),
    Cyberware("recoil_dampers", "Recoil Dampers", "ARMS", 1, 1, 500, "Forearm stabilizers steady firearms and close strikes.", {"aim": 1, "melee_power": 1}),
    Cyberware("titan_arm", "Titan Cyberarm", "ARMS", 2, 2, 1100, "Reinforced myomers turn close combat brutal.", {"melee_power": 4}),
    Cyberware("reinforced_ribs", "Reinforced Rib Cage", "TORSO", 1, 1, 600, "A light internal frame keeps the operator standing.", {"hp": 3}),
    Cyberware("subdermal_mesh", "Subdermal Armor Mesh", "TORSO", 2, 2, 1400, "Flexible plates harden beneath the skin.", {"defense": 2, "hp": 4}),
    Cyberware("adrenal_pump", "Adrenal Overdrive", "CIRCULATORY", 1, 1, 600, "Emergency pump sustains a wounded operator.", {"hp": 3, "initiative": 1}),
    Cyberware("combat_blood", "Combat Blood Filter", "CIRCULATORY", 2, 2, 1250, "Synthetic filtration resists shock and trauma.", {"hp": 5, "defense": 1}),
    Cyberware("kerenzikov_reflex", "Kerenzikov Reflex", "NERVOUS SYSTEM", 2, 2, 1200, "Predictive nerves seize the first beat.", {"initiative": 4}),
    Cyberware("synaptic_accelerator", "Synaptic Accelerator", "NERVOUS SYSTEM", 3, 3, 2400, "Military synapses compress perception under fire.", {"initiative": 5, "aim": 2}),
)

BY_ID = {item.id: item for item in CATALOGUE}


def normalize_installed(ids: object) -> list[str]:
    if not isinstance(ids, (list, tuple)):
        return []
    result: list[str] = []
    occupied_zones: set[str] = set()
    for raw in ids:
        key = str(raw)
        if key in BY_ID and key not in result and BY_ID[key].zone not in occupied_zones:
            result.append(key)
            occupied_zones.add(BY_ID[key].zone)
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
    same_zone = [key for key in installed if BY_ID[key].zone == item.zone]
    replacement_ids = [key for key in installed if key not in same_zone]
    if item.humanity_cost > humanity_remaining(replacement_ids):
        return installed, funds, False, "humanity"
    if item.credit_cost > funds:
        return installed, funds, False, "funds"
    replacement_ids.append(cyberware_id)
    reason = "replaced" if same_zone else "installed"
    return replacement_ids, funds - item.credit_cost, True, reason


def catalogue_for_zone(zone: str) -> tuple[Cyberware, ...]:
    return tuple(item for item in CATALOGUE if item.zone == str(zone).upper())


def combat_bonuses(ids: object) -> dict[str, int]:
    bonuses: dict[str, int] = {}
    for key in normalize_installed(ids):
        for stat, value in BY_ID[key].combat_bonuses.items():
            bonuses[stat] = bonuses.get(stat, 0) + value
    return bonuses


def is_eligible_role(role: str) -> bool:
    return str(role).lower() not in INELIGIBLE_ROLES
