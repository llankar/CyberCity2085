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
    Cyberware("threat_predictor", "Threat Predictor", "HEAD", 2, 2, 1150, "A cranial model anticipates hostile attack lanes.", {"initiative": 3, "defense": 1}),
    Cyberware("combat_memory", "Combat Memory Shard", "HEAD", 2, 2, 1300, "Indexed combat patterns guide aim and tempo.", {"aim": 2, "initiative": 2}),
    Cyberware("tactical_coprocessor", "Tactical Co-processor", "HEAD", 3, 3, 2200, "A combat cache expands moment-to-moment options.", {"action_points": 1, "initiative": 1}),
    Cyberware("focus_governor", "Focus Governor", "HEAD", 1, 1, 420, "Filters panic noise while preserving combat awareness.", {"defense": 1}),
    Cyberware("language_spike", "Command Language Spike", "HEAD", 1, 1, 610, "Compresses squad calls into instinctive tactical cues.", {"initiative": 1, "aim": 1}),
    Cyberware("pain_editor_lite", "Pain Editor Lite", "HEAD", 1, 1, 760, "Suppresses distracting pain without masking lethal trauma.", {"hp": 2, "defense": 1}),
    Cyberware("trajectory_archive", "Trajectory Archive", "HEAD", 2, 2, 1500, "Replays hostile firing solutions from a curated combat library.", {"aim": 3, "defense": 1}),
    Cyberware("command_mesh", "Command Mesh", "HEAD", 2, 2, 1800, "Shares target priorities through a hardened cranial relay.", {"initiative": 3, "aim": 2}),
    Cyberware("war_savant", "War Savant Core", "HEAD", 3, 3, 2700, "A restricted strategist predicts several exchanges ahead.", {"action_points": 1, "aim": 2, "initiative": 2}),
    Cyberware("smart_eye", "Smart Targeting Eye", "EYES", 1, 1, 450, "Ballistic overlay corrects aim in real time.", {"aim": 2, "crit": 1}),
    Cyberware("thermal_optic", "Thermal Veil Optic", "EYES", 1, 1, 550, "Heat-layer contrast reveals movement through clutter.", {"aim": 1, "crit": 1}),
    Cyberware("predator_optics", "Predator Optics", "EYES", 2, 2, 1350, "Multispectral acquisition exposes lethal openings.", {"aim": 3, "crit": 2}),
    Cyberware("ballistic_oracle", "Ballistic Oracle", "EYES", 3, 3, 2300, "Paired predictive lenses solve firing windows before recoil.", {"aim": 4, "crit": 3}),
    Cyberware("lowlight_retina", "Low-Light Retina", "EYES", 1, 1, 400, "Amplifies edges and motion in blackout conditions.", {"aim": 1}),
    Cyberware("rangefinder_lens", "Rangefinder Lens", "EYES", 1, 1, 650, "Measures distance and lead without breaking sight picture.", {"aim": 2}),
    Cyberware("flashguard_iris", "Flashguard Iris", "EYES", 1, 1, 780, "Reactive shutters preserve vision through muzzle flash and glare.", {"defense": 1, "initiative": 1}),
    Cyberware("ghost_spectrum", "Ghost-Spectrum Array", "EYES", 2, 2, 1550, "Fuses thermal, ultraviolet and motion traces into one image.", {"aim": 3, "initiative": 2}),
    Cyberware("duelist_reticle", "Duelist Reticle", "EYES", 2, 2, 1850, "A precision reticle isolates exposed joints and weapon hands.", {"aim": 3, "crit": 3}),
    Cyberware("omniscient_optics", "Omniscient Optics", "EYES", 3, 3, 2800, "Military sensor fusion turns peripheral movement into firing data.", {"aim": 5, "crit": 3}),
    Cyberware("recoil_dampers", "Recoil Dampers", "ARMS", 1, 1, 500, "Forearm stabilizers steady firearms and close strikes.", {"aim": 1, "melee_power": 1}),
    Cyberware("arc_tendons", "Arc Tendon Weave", "ARMS", 2, 2, 1050, "Conductive tendons accelerate committed close attacks.", {"melee_power": 3, "crit": 1}),
    Cyberware("titan_arm", "Titan Cyberarm", "ARMS", 2, 2, 1100, "Reinforced myomers turn close combat brutal.", {"melee_power": 4}),
    Cyberware("siege_myomers", "Siege Myomer Pair", "ARMS", 3, 3, 2250, "Military myomers deliver crushing force behind armored joints.", {"melee_power": 6, "defense": 1}),
    Cyberware("grip_locks", "Grip Locks", "ARMS", 1, 1, 430, "Magnetic tendon locks steady weapons under impact.", {"aim": 1, "defense": 1}),
    Cyberware("quickdraw_servos", "Quickdraw Servos", "ARMS", 1, 1, 620, "Compact wrist motors accelerate weapon presentation.", {"initiative": 2}),
    Cyberware("shock_knuckles", "Shock Knuckles", "ARMS", 1, 1, 790, "Conductive knuckles add force to close strikes.", {"melee_power": 2, "crit": 1}),
    Cyberware("gunslinger_frame", "Gunslinger Frame", "ARMS", 2, 2, 1450, "Linked shoulder servos control recoil across both arms.", {"aim": 3, "crit": 2}),
    Cyberware("monowire_tendons", "Monowire Tendons", "ARMS", 2, 2, 1750, "High-tension fibers make every committed strike decisive.", {"melee_power": 5, "initiative": 1}),
    Cyberware("juggernaut_arms", "Juggernaut Armature", "ARMS", 3, 3, 2750, "Full combat armatures combine siege force with weapon stability.", {"melee_power": 7, "aim": 2}),
    Cyberware("reinforced_ribs", "Reinforced Rib Cage", "TORSO", 1, 1, 600, "A light internal frame keeps the operator standing.", {"hp": 3}),
    Cyberware("trauma_lattice", "Trauma Lattice", "TORSO", 2, 2, 1200, "A flexible inner cage disperses blunt trauma.", {"hp": 5, "defense": 1}),
    Cyberware("subdermal_mesh", "Subdermal Armor Mesh", "TORSO", 2, 2, 1400, "Flexible plates harden beneath the skin.", {"defense": 2, "hp": 4}),
    Cyberware("reactive_carapace", "Reactive Carapace", "TORSO", 3, 3, 2500, "Layered smart plates tense milliseconds before impact.", {"defense": 3, "hp": 7}),
    Cyberware("impact_gel", "Impact Gel Pockets", "TORSO", 1, 1, 460, "Subcutaneous gel cushions blunt trauma around vital organs.", {"hp": 2, "defense": 1}),
    Cyberware("spinal_brace", "Carbon Spinal Brace", "TORSO", 1, 1, 640, "A flexible brace stabilizes the operator under heavy recoil.", {"hp": 3}),
    Cyberware("organ_shield", "Organ Shielding", "TORSO", 1, 1, 800, "Thin ceramic shells protect the most vulnerable organs.", {"hp": 3, "defense": 1}),
    Cyberware("kinetic_baffles", "Kinetic Baffles", "TORSO", 2, 2, 1600, "Layered baffles spread projectile energy across the chest.", {"hp": 5, "defense": 2}),
    Cyberware("combat_chassis", "Combat Chassis", "TORSO", 2, 2, 1900, "An internal frame anchors armor and distributes load.", {"hp": 7, "defense": 1}),
    Cyberware("fortress_shell", "Fortress Dermal Shell", "TORSO", 3, 3, 2950, "A military dermal lattice hardens the entire core on impact.", {"hp": 9, "defense": 3}),
    Cyberware("adrenal_pump", "Adrenal Overdrive", "CIRCULATORY", 1, 1, 600, "Emergency pump sustains a wounded operator.", {"hp": 3, "initiative": 1}),
    Cyberware("coagulant_nanites", "Coagulant Nanites", "CIRCULATORY", 1, 1, 500, "Medical nanites seal minor trauma before shock spreads.", {"hp": 2, "defense": 1}),
    Cyberware("combat_blood", "Combat Blood Filter", "CIRCULATORY", 2, 2, 1250, "Synthetic filtration resists shock and trauma.", {"hp": 5, "defense": 1}),
    Cyberware("phoenix_pump", "Phoenix Cardiac Pump", "CIRCULATORY", 3, 3, 2350, "A redundant combat heart floods muscles under lethal stress.", {"hp": 6, "initiative": 3}),
    Cyberware("oxygen_reservoir", "Oxygen Reservoir", "CIRCULATORY", 1, 1, 410, "A compact reservoir keeps muscles supplied during shock.", {"hp": 2}),
    Cyberware("platelet_forge", "Platelet Forge", "CIRCULATORY", 1, 1, 670, "Artificial marrow accelerates clotting after penetration trauma.", {"hp": 3}),
    Cyberware("combat_metabolism", "Combat Metabolism", "CIRCULATORY", 1, 1, 810, "Regulated stimulants sustain short bursts of violent exertion.", {"initiative": 2, "hp": 2}),
    Cyberware("vascular_weave", "Vascular Weave", "CIRCULATORY", 2, 2, 1520, "Reinforced vessels resist pressure loss and internal bleeding.", {"hp": 6, "defense": 1}),
    Cyberware("redline_glands", "Redline Glands", "CIRCULATORY", 2, 2, 1880, "Synthetic glands deliver measured combat stimulants on demand.", {"initiative": 4, "hp": 3}),
    Cyberware("hydra_heart", "Hydra Heart Array", "CIRCULATORY", 3, 3, 2850, "Three micro-pumps maintain pressure through catastrophic injury.", {"hp": 9, "initiative": 3}),
    Cyberware("nerve_stabilizer", "Nerve Stabilizer", "NERVOUS SYSTEM", 1, 1, 500, "Signal damping steadies hands without dulling reactions.", {"initiative": 1, "aim": 1}),
    Cyberware("kerenzikov_reflex", "Phase-Shift Reflex", "NERVOUS SYSTEM", 2, 2, 1200, "Predictive nerves seize the first beat.", {"initiative": 4}),
    Cyberware("ghost_reflex", "Ghost Reflex Matrix", "NERVOUS SYSTEM", 2, 2, 1450, "Parallel motor signals exploit brief openings with precision.", {"initiative": 3, "crit": 2}),
    Cyberware("synaptic_accelerator", "Synaptic Accelerator", "NERVOUS SYSTEM", 3, 3, 2400, "Military synapses compress perception under fire.", {"initiative": 5, "aim": 2}),
    Cyberware("tremor_filter", "Tremor Filter", "NERVOUS SYSTEM", 1, 1, 440, "Signal correction removes involuntary motion from fine aim.", {"aim": 1, "crit": 1}),
    Cyberware("balance_tail", "Vestibular Regulator", "NERVOUS SYSTEM", 1, 1, 690, "An inner-ear regulator keeps footing through impacts and recoil.", {"defense": 1, "aim": 1}),
    Cyberware("reaction_gate", "Reaction Gate", "NERVOUS SYSTEM", 1, 1, 820, "A motor gate shortens the delay between threat and movement.", {"initiative": 2, "defense": 1}),
    Cyberware("combat_reflex_bus", "Combat Reflex Bus", "NERVOUS SYSTEM", 2, 2, 1580, "A parallel nerve bus routes urgent motion around hesitation.", {"initiative": 4, "defense": 1}),
    Cyberware("razor_synapses", "Razor Synapses", "NERVOUS SYSTEM", 2, 2, 1920, "Overclocked sensory loops sharpen aim at dangerous speed.", {"initiative": 4, "aim": 3}),
    Cyberware("temporal_overclock", "Temporal Overclock", "NERVOUS SYSTEM", 3, 3, 3000, "Perception stretches into tactical intervals under fire.", {"action_points": 1, "initiative": 5, "aim": 2}),
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
