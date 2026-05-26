from game.agents.sheet_calculations import compute_derived_stats, skill_total


def test_skill_total_uses_linked_attribute_and_mods() -> None:
    attributes = {"agi": 4, "psi": 3}
    skills = {"firearms": 2, "telepathy": 1}
    mods = {"firearms": 1}

    assert skill_total("firearms", attributes, skills, mods) == 7
    assert skill_total("telepathy", attributes, skills, {}) == 4


def test_compute_derived_stats_applies_small_integer_formulas_and_stress_penalties() -> None:
    attributes = {"level": 2, "str": 3, "agi": 4, "con": 5, "cha": 2, "psi": 3, "defense": 2}
    skills = {"firearms": 2, "close_combat": 1, "tactics": 2, "stealth": 2, "composure": 3}
    equipment = {"aim": 1, "defense": 1, "recovery_rate": 1}

    steady = compute_derived_stats(attributes, skills, equipment, "steady")
    breaking = compute_derived_stats(attributes, skills, equipment, "breaking")

    assert steady["hp"] == 29
    assert steady["aim"] == 8
    assert steady["defense"] == 6
    assert steady["recovery_rate"] == 5

    assert breaking["aim"] == 6
    assert breaking["resolve"] == max(0, steady["resolve"] - 2)
    assert breaking["initiative"] == max(0, steady["initiative"] - 2)
