"""Reproducible comparison of four spending strategies using real mission rewards."""

from statistics import mean, median

from game.gamestate import GameState
from game.management.funds import calculate_mission_fund_reward
from game.management.equipment import default_equipment_catalog, equipment_purchase_price
from game.agents.cyberware import CATALOGUE


def simulate(missions: int = 120) -> dict:
    state = GameState()
    rewards = [calculate_mission_fund_reward(m, True) for m in state.mission_templates]
    rewards = rewards or [0]
    equipment = sorted(equipment_purchase_price(i) for items in default_equipment_catalog().values() for i in items)
    cyberware = sorted(i.credit_cost for i in CATALOGUE)
    results = {}
    for strategy in ("expansion", "equipment", "cyberware", "balanced"):
        cash, hangar, gear_spend, cyber_spend = state.available_funds, 1, 0, 0
        for turn in range(missions):
            cash += rewards[turn % len(rewards)]
            if strategy in {"expansion", "balanced"} and hangar < 4:
                cost = (20_000, 60_000, 180_000)[hangar - 1]
                if cash >= cost and (strategy == "expansion" or turn % 3 == 0):
                    cash -= cost; hangar += 1; continue
            pool = equipment if strategy == "equipment" or strategy == "balanced" and turn % 2 else cyberware
            if strategy == "cyberware": pool = cyberware
            affordable = [price for price in pool if price <= cash]
            if affordable:
                price = affordable[min(len(affordable)-1, turn % len(affordable))]
                cash -= price
                if pool is equipment: gear_spend += price
                else: cyber_spend += price
        results[strategy] = {"missions": missions, "funds_remaining": cash, "hangar_level": hangar,
                             "agents_capacity": hangar + 4, "equipment_value": gear_spend,
                             "cyberware_value": cyber_spend}
    return {"mission_reward_mean": mean(rewards), "mission_reward_median": median(rewards), "strategies": results}


if __name__ == "__main__":
    import json
    print(json.dumps(simulate(), indent=2))
