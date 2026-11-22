import pytest

from game.battle_maps import build_battle_map_catalog
from game.combat.encounter_qa import QA_SQUAD_PROFILES, create_qa_allies, simulate_encounter


def test_real_deployment_profiles_keep_pilot_and_support_identity() -> None:
    for profile in QA_SQUAD_PROFILES:
        characters, allies = create_qa_allies(profile, 4)
        assert allies
        assert len({id(unit) for unit in allies}) == len(allies)
        assert len({unit.position for unit in allies}) == len(allies)
        if profile != "rifle":
            assert all(character.stats.level == 4 for character in characters)
            assert all(character.stats.hp == character.stats.max_hp for character in characters)
            by_role = {character.role: character for character in characters}
            if "samurai" in by_role:
                assert by_role["samurai"].stats.str > by_role["samurai"].stats.agi
            if "sniper" in by_role:
                assert by_role["sniper"].stats.agi > by_role["sniper"].stats.str
            if "psi" in by_role:
                assert by_role["psi"].stats.psi > by_role["psi"].stats.agi
        if profile == "support":
            assert sum(unit.spec_ops_asset is not None for unit in allies) == 2
        if profile == "piloted_armor":
            pilot = characters[0]
            assert sum(unit.character is pilot for unit in allies) == 1
            assert next(unit for unit in allies if unit.character is pilot).spec_ops_asset is not None


@pytest.mark.parametrize("profile", QA_SQUAD_PROFILES[1:])
def test_sustained_profiles_finish_on_three_representative_maps(profile: str) -> None:
    catalog = build_battle_map_catalog()
    entries = (catalog[0], catalog[len(catalog) // 2], catalog[-1])
    for entry in entries:
        row = simulate_encounter(
            theme="raider",
            level=4,
            risk=4,
            count=4,
            seed=0,
            policy="objective_counterplay",
            objective_kind="eliminate",
            max_turns=60,
            map_path=entry.path,
            squad_profile=profile,
        )
        assert row["outcome"] in {"victory", "defeat"}
        assert row["geometry_checked"]
        assert row["longest_unchanged_rounds"] < 10


@pytest.mark.parametrize(
    ("profile", "map_name"),
    [
        ("understrength", "cybercity_street_02_neon_market_alley.png"),
        ("piloted_armor", "cybercity_street_10_civic_plaza.png"),
    ],
)
def test_extreme_profiles_do_not_repeat_zero_value_actions(profile: str, map_name: str) -> None:
    row = simulate_encounter(
        theme="corp_37_robot",
        level=4,
        risk=5,
        count=6,
        seed=0,
        policy="objective_counterplay",
        objective_kind="eliminate",
        max_turns=100,
        map_path=f"assets/maps/{map_name}",
        squad_profile=profile,
    )
    assert row["longest_unchanged_rounds"] < 10
    if profile == "understrength":
        assert row["player_actions"].get("first_aid", 0) <= row["turns"]
