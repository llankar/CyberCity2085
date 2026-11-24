"""Cross-system contracts for the single strategic economy scale."""

import random
import json

from game.gamestate import GameState
from game.management.spec_ops_assets import SpecOpsAsset, asset_catalog
from game.management.weekly_planning import DIRECTIVES
from game.management.weekly_planning import build_management_forecast
from game.recruitment import build_recruitment_candidates


def test_new_campaign_starts_with_opening_capital_and_four_free_hires():
    state = GameState()

    assert state.grant_initial_recruitment() is True
    assert state.available_funds == 1_500
    assert state.free_recruits_remaining == 4
    assert state.grant_initial_recruitment() is False
    assert state.available_funds == 1_500
    assert state.free_recruits_remaining == 4


def test_opening_hires_are_consumed_before_paid_recruitment():
    state = GameState()
    state.grant_initial_recruitment()

    for remaining in range(3, -1, -1):
        assert state.pay_recruitment(1_300, "Candidate") == (True, True)
        assert state.free_recruits_remaining == remaining
        assert state.available_funds == 1_500

    assert state.pay_recruitment(1_300, "Paid Candidate") == (True, False)
    assert state.available_funds == 200


def test_opening_recruitment_round_trip_and_legacy_save_compatibility(tmp_path):
    state = GameState()
    state.grant_initial_recruitment()
    state.pay_recruitment(1_300, "Candidate")
    path = tmp_path / "opening-recruitment.json"
    state.save(path)

    restored = GameState.load(path)
    assert restored.initial_recruitment_granted is True
    assert restored.free_recruits_remaining == 3
    assert restored.available_funds == 1_500

    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.pop("initial_recruitment_granted")
    payload.pop("free_recruits_remaining")
    path.write_text(json.dumps(payload), encoding="utf-8")
    legacy = GameState.load(path)
    assert legacy.initial_recruitment_granted is True
    assert legacy.free_recruits_remaining == 0
    assert legacy.grant_initial_recruitment() is False


def test_core_spending_systems_share_the_mission_reward_scale():
    state = GameState()
    rewards = [mission.fund_reward for mission in state.mission_templates]
    recruits = build_recruitment_candidates([], rng=random.Random(2085))
    assets = asset_catalog()

    assert min(rewards) >= 1_400
    assert all(400 <= directive.cost <= 800 for directive in DIRECTIVES)
    assert all(1_000 <= recruit.price <= 3_500 for recruit in recruits)
    assert all(4_000 <= asset._acquire_cost <= 12_000 for asset in assets)
    assert all(100 <= asset.deploy_cost <= 500 for asset in assets)


def test_financial_forecast_combines_daily_and_weekly_income():
    state = GameState()
    state.spec_ops_assets = asset_catalog()[:2]
    forecast = build_management_forecast(state)

    assert forecast.projected_income == (
        state.projected_weekly_income
        + state.compute_budget() * state.calendar.days_per_week
    )
    assert forecast.projected_net == forecast.projected_income - forecast.asset_upkeep


def test_legacy_asset_costs_migrate_without_losing_integrity():
    asset = asset_catalog()[0]
    payload = asset.to_dict()
    payload["deploy_cost"] = 10
    payload["maintenance"].update(
        {"integrity": 73, "repair_cost_per_damage": 1, "base_upkeep": 2}
    )

    restored = SpecOpsAsset.from_dict(payload)

    assert restored.maintenance.integrity == 73
    assert restored.deploy_cost == 200
    assert restored.maintenance.base_upkeep == 50
    assert restored.maintenance.repair_cost_per_damage == 15


def test_legacy_save_rewards_and_weekly_finance_migrate_to_current_scale(tmp_path):
    state = GameState()
    path = tmp_path / "legacy-economy.json"
    state.save(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["mission_templates"][0]["fund_reward"] = 40
    payload["corporation_finance"]["weekly_stipend"] = 75
    payload["corporation_finance"]["debt_upkeep"] = 15
    path.write_text(json.dumps(payload), encoding="utf-8")

    restored = GameState.load(path)

    assert restored.mission_templates[0].fund_reward >= 1_400
    assert restored.corporation_finance.weekly_stipend == 750
    assert restored.corporation_finance.debt_upkeep == 150
