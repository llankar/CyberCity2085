"""Pure agent sheet calculation helpers.

Formula goals:
- Keep coefficients small and integer-friendly for UI readability.
- Keep outputs deterministic and side-effect free.

Derived formulas:
- hp = con * 5 + level * 2 + equipment.hp
- aim = agi + firearms + floor(tactics / 2) + equipment.aim
- defense = defense_attr + floor(agi / 2) + floor(stealth / 2) + equipment.defense
- crit = floor(agi / 2) + floor(close_combat / 2) + equipment.crit
- initiative = agi + cha + floor(tactics / 2) + equipment.initiative
- stress_cap = 10 + con + cha + floor(composure / 2) + equipment.stress_cap
- recovery_rate = 1 + floor(con / 2) + floor(composure / 3) + equipment.recovery_rate
- resolve = psi + cha + floor(composure / 2) + equipment.resolve

Stress-state modifiers:
- steady: no penalty
- rattled: -1 initiative
- frayed: -1 aim, -1 resolve, -1 initiative
- breaking: -2 aim, -2 resolve, -2 initiative, -1 defense
"""

from __future__ import annotations


def skill_total(
    skill_name: str,
    attributes: dict[str, int],
    skills: dict[str, int],
    temporary_mods: dict[str, int] | None,
) -> int:
    """Return a compact skill total from one linked attribute and skill rank."""
    skill_key = str(skill_name)
    linked_attr = {
        "firearms": "agi",
        "close_combat": "str",
        "tactics": "cha",
        "tech": "psi",
        "medicine": "cha",
        "influence": "cha",
        "stealth": "agi",
        "composure": "con",
        "psychokinesis": "psi",
        "pyrokinesis": "psi",
        "cryokinesis": "psi",
        "telepathy": "psi",
    }.get(skill_key, "cha")
    base_attr = int(attributes.get(linked_attr, 0))
    rank = int(skills.get(skill_key, 0))
    bonus = int((temporary_mods or {}).get(skill_key, 0))
    return max(0, base_attr + rank + bonus)


def compute_derived_stats(
    attributes: dict[str, int],
    skills: dict[str, int],
    equipment_mods: dict[str, int] | None,
    stress_state: str,
) -> dict[str, int]:
    """Compute integer-readable derived stats for combat/readiness/stress systems."""
    equipment = equipment_mods or {}
    level = int(attributes.get("level", 1))
    str_attr = int(attributes.get("str", 0))
    agi = int(attributes.get("agi", 0))
    con = int(attributes.get("con", 0))
    cha = int(attributes.get("cha", 0))
    psi = int(attributes.get("psi", 0))
    defense_attr = int(attributes.get("defense", 0))

    firearms = int(skills.get("firearms", 0))
    close_combat = int(skills.get("close_combat", 0))
    tactics = int(skills.get("tactics", 0))
    stealth = int(skills.get("stealth", 0))
    composure = int(skills.get("composure", 0))

    derived = {
        "hp": max(1, con * 5 + level * 2 + int(equipment.get("hp", 0))),
        "aim": max(0, agi + firearms + tactics // 2 + int(equipment.get("aim", 0))),
        "defense": max(
            0,
            defense_attr + agi // 2 + stealth // 2 + int(equipment.get("defense", 0)),
        ),
        "crit": max(0, agi // 2 + close_combat // 2 + int(equipment.get("crit", 0))),
        "initiative": max(
            0,
            agi + cha + tactics // 2 + int(equipment.get("initiative", 0)),
        ),
        "stress_cap": max(
            1,
            10 + con + cha + composure // 2 + int(equipment.get("stress_cap", 0)),
        ),
        "recovery_rate": max(
            1,
            1 + con // 2 + composure // 3 + int(equipment.get("recovery_rate", 0)),
        ),
        "resolve": max(0, psi + cha + composure // 2 + int(equipment.get("resolve", 0))),
        "melee_power": max(0, str_attr + close_combat + int(equipment.get("melee_power", 0))),
    }

    penalties = {
        "steady": {},
        "rattled": {"initiative": -1},
        "frayed": {"aim": -1, "resolve": -1, "initiative": -1},
        "breaking": {"aim": -2, "resolve": -2, "initiative": -2, "defense": -1},
    }.get((stress_state or "steady").lower(), {})

    for key, penalty in penalties.items():
        derived[key] = max(0, derived.get(key, 0) + penalty)

    return derived
