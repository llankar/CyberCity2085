import pytest

from game.battle_maps import build_battle_map_catalog
from game.combat.encounter_qa import QA_SQUAD_PROFILES, create_qa_allies, simulate_encounter


def test_real_deployment_profiles_keep_pilot_and_support_identity() -> None:
    for profile in QA_SQUAD_PROFILES:
        characters, allies = create_qa_allies(profile, 4)
        assert allies
        assert len({id(unit) for unit in allies}) == len(allies)
        assert len({unit.position for unit in allies}) == len(allies)
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
