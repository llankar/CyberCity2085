from tools.simulate_strategic_economy import simulate


def test_four_economic_strategies_are_reproducible():
    first = simulate(120)
    assert first == simulate(120)
    assert set(first["strategies"]) == {"expansion", "equipment", "cyberware", "balanced"}
    assert all(row["funds_remaining"] >= 0 for row in first["strategies"].values())
    assert 10 <= first["first_hangar_missions"] <= 15
    assert 1_400 <= first["mission_reward_median"] <= 2_000
    bands = first["price_bands"]
    assert bands["directive"][1] < first["mission_reward_median"]
    assert bands["recruit"][0] >= 1_000
    assert bands["research"] == [600, 6_500]
    assert bands["asset"][0] >= 4_000
    assert bands["hangar"] == [20_000, 180_000]
    assert first["strategies"]["expansion"]["hangar_level"] >= 3
    assert first["strategies"]["balanced"]["hangar_level"] >= 2
