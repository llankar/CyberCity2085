"""Composition invariants plus real seeded generation and engine simulations."""

from collections import Counter
import random

import pytest

from game.character import Character
from game.combat.encounter_composition import compose_encounter, enemy_spawn_positions, ROLE_COST
from game.combat.encounter_qa import objective_threat_distance, simulate_encounter, synthetic_enemy_position
from game.combat_system import create_enemy_units
from game.enemy_themes import ENEMY_THEMES
from game.mission_objectives import create_battle_objective
from game.mission_templates import MissionTemplate
from game.stats import PlayerStats
from game.unit import Unit


def test_composition_matrix_keeps_headcount_budget_frontline_and_specialist_bounds():
    for theme in ENEMY_THEMES:
        for level in (1, 3, 4, 7, 10):
            for risk in (1, 5, 10):
                for count in (0, 1, 2, 3, 6, 8, 20):
                    plan = compose_encounter(count, level, risk, theme)
                    tally = Counter(plan.roles)
                    assert len(plan.roles) == count
                    assert plan.spent <= plan.budget <= 3 * count
                    assert tally["grunt"] >= (count + 1) // 2
                    assert tally["commander"] <= 1
                    if level < 3:
                        assert tally["grunt"] == count
                    if level < 4:
                        assert not tally["elite"]
                    if level < 7:
                        assert not tally["commander"]
                    if theme == "starver":
                        assert count - tally["grunt"] <= 1


def test_faction_roles_and_risk_budget_have_real_effects_without_increasing_headcount():
    corporate = compose_encounter(8, 7, 8, "corp_37_robot")
    assert "commander" in corporate.roles and "heavy" in corporate.roles
    assert "commander" in compose_encounter(8, 7, 8, "starver").roles
    assert "elite" in compose_encounter(8, 7, 8, "novatek_hybrid").roles
    low, high = (compose_encounter(6, 4, risk, "mutant") for risk in (1, 10))
    assert high.spent > low.spent and len(low.roles) == len(high.roles) == 6
    assert compose_encounter(8, 7, 8, "37") == compose_encounter(8, 7, 8, "corp_37")


def test_seeded_generation_consumes_composition_and_never_wraps_spawn_cells():
    character = Character("Rook")
    character.stats.level = 7
    mission = MissionTemplate("qa", "QA", "Eliminate", "", "", {}, 32,
                              enemy_theme="corp_37_robot", risk_level=8)
    first, count = create_enemy_units(mission, [character], rng=random.Random(42))
    second, _ = create_enemy_units(mission, [character], rng=random.Random(42))
    assert count == 32 and len({u.position for u in first}) == 32
    assert tuple(u.enemy_subtype for u in first) == compose_encounter(32, 7, 8, mission.enemy_theme).roles
    assert [(u.stats.level, u.health, u.position) for u in first] == [(u.stats.level, u.health, u.position) for u in second]
    assert all(0 <= x < 1280 and 0 <= y < 720 and x % 32 == y % 32 == 0 for x, y in (u.position for u in first))
    assert sum(ROLE_COST[u.enemy_subtype] for u in first) <= compose_encounter(32, 7, 8, mission.enemy_theme).budget
    with pytest.raises(ValueError, match="distinct fallback"):
        enemy_spawn_positions(1000)


def test_zero_enemy_scripted_mission_stays_empty():
    mission = MissionTemplate("qa", "QA", "Event", "", "", {}, 0)
    assert create_enemy_units(mission, []) == ([], 0)


def test_simulation_is_reproducible_restores_rng_and_runs_real_enemy_telegraphs():
    before = random.getstate()
    args = dict(theme="novatek_hybrid", level=7, risk=8, count=8, seed=2, policy="counterplay", layout="cover")
    result = simulate_encounter(**args)
    assert random.getstate() == before
    assert result == simulate_encounter(**args)
    assert result["outcome"] in {"victory", "defeat", "turn_limit"}
    assert 1 <= result["turns"] <= 30
    assert result["announced"].get("LOCK", 0) > 0
    assert result["dodges"] > 0 and result["interruptions"] > 0


def test_objective_qa_prioritizes_enemies_threatening_defensive_boundaries():
    containment = create_battle_objective(MissionTemplate(
        "qa", "QA", "Contain", "", "", {}, 2, objective_type="containment"
    ))
    defend = create_battle_objective(MissionTemplate(
        "qa", "QA", "Defend", "", "", {}, 2, objective_type="defend"
    ), position=(128, 192))
    near_line = Unit(position=(288, 224), stats=PlayerStats(), health=10)
    far_from_line = Unit(position=(288, 320), stats=PlayerStats(), health=1)
    near_zone = Unit(position=(192, 192), stats=PlayerStats(), health=10)
    far_from_zone = Unit(position=(384, 320), stats=PlayerStats(), health=1)

    assert objective_threat_distance(near_line, containment) < objective_threat_distance(far_from_line, containment)
    assert objective_threat_distance(near_zone, defend) < objective_threat_distance(far_from_zone, defend)


def test_synthetic_containment_opening_preserves_a_full_response_activation():
    positions = [synthetic_enemy_position(index, "containment") for index in range(12)]
    assert len(set(positions)) == 12
    assert all(0 <= x < 640 and 0 <= y < 384 for x, y in positions)
    assert all((y - 192) // 32 > 3 for _, y in positions)


@pytest.mark.parametrize("theme", ["starver", "mutant", "raider", "corp_samurai", "corp_37_robot", "novatek_hybrid"])
def test_seeded_family_battles_stay_bounded_and_have_consistent_outcomes(theme):
    result = simulate_encounter(theme=theme, level=4, risk=5, count=6, seed=4)
    assert sum(result["roles"].values()) == 6
    assert 0 <= result["allied_losses"] <= 4
    assert 0 <= result["enemy_survivors"] <= 6
    if result["outcome"] == "victory":
        assert result["enemy_survivors"] == 0
    elif result["outcome"] == "defeat":
        assert result["allied_losses"] == 4
