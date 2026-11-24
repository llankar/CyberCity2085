"""Reproducible comparison of four strategies using the live economy data."""

import math
import random
from statistics import mean, median

from game.gamestate import GameState
from game.management.funds import calculate_mission_fund_reward
from game.management.equipment import default_equipment_catalog, equipment_purchase_price
from game.agents.cyberware import CATALOGUE
from game.management.research import create_starter_research_tree
from game.management.spec_ops_assets import asset_catalog
from game.management.weekly_planning import DIRECTIVES
from game.recruitment import build_recruitment_candidates


def simulate(missions: int = 120) -> dict:
    state = GameState()
    rewards = [calculate_mission_fund_reward(m, True) for m in state.mission_templates]
    rewards = rewards or [0]
    durations = [max(1, int(m.duration_days)) for m in state.mission_templates] or [1]
    equipment = sorted(equipment_purchase_price(i) for items in default_equipment_catalog().values() for i in items)
    cyberware = sorted(i.credit_cost for i in CATALOGUE)
    research = sorted(p.funds_cost for p in create_starter_research_tree().projects.values())
    assets = sorted(a._acquire_cost for a in asset_catalog())
    recruits = sorted(c.price for c in build_recruitment_candidates([], rng=random.Random(2085)))
    results = {}
    for strategy in ("expansion", "equipment", "cyberware", "balanced"):
        cash, hangar, gear_spend, cyber_spend, research_spend = state.available_funds, 1, 0, 0, 0
        for turn in range(missions):
            cash += rewards[turn % len(rewards)]
            cash += state.compute_budget() * durations[turn % len(durations)]
            if strategy in {"expansion", "balanced"} and hangar < 4:
                cost = (20_000, 60_000, 180_000)[hangar - 1]
                if cash >= cost:
                    cash -= cost; hangar += 1; continue
                if strategy == "expansion" or (strategy == "balanced" and hangar == 1):
                    continue
            pool = equipment if strategy == "equipment" or strategy == "balanced" and turn % 3 == 0 else cyberware
            if strategy == "cyberware": pool = cyberware
            if strategy == "balanced" and turn % 3 == 2:
                pool = research
            affordable = [price for price in pool if price <= cash]
            if affordable:
                price = affordable[min(len(affordable)-1, turn % len(affordable))]
                cash -= price
                if pool is equipment: gear_spend += price
                elif pool is cyberware: cyber_spend += price
                else: research_spend += price
        results[strategy] = {"missions": missions, "funds_remaining": cash, "hangar_level": hangar,
                             "agents_capacity": hangar + 4, "equipment_value": gear_spend,
                             "cyberware_value": cyber_spend, "research_value": research_spend}
    ordinary_income = median(rewards) + state.compute_budget() * median(durations)
    first_hangar_missions = math.ceil(max(0, 20_000 - state.available_funds) / ordinary_income)
    return {
        "mission_reward_mean": mean(rewards),
        "mission_reward_median": median(rewards),
        "ordinary_income_per_mission": ordinary_income,
        "first_hangar_missions": first_hangar_missions,
        "price_bands": {
            "recruit": [min(recruits), max(recruits)],
            "equipment": [min(equipment), max(equipment)],
            "cyberware": [min(cyberware), max(cyberware)],
            "research": [min(research), max(research)],
            "asset": [min(assets), max(assets)],
            "directive": [min(d.cost for d in DIRECTIVES), max(d.cost for d in DIRECTIVES)],
            "hangar": [20_000, 180_000],
        },
        "strategies": results,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(simulate(), indent=2))
