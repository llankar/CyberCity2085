from tools.simulate_strategic_economy import simulate


def test_four_economic_strategies_are_reproducible():
    first = simulate(120)
    assert first == simulate(120)
    assert set(first["strategies"]) == {"expansion", "equipment", "cyberware", "balanced"}
    assert all(row["funds_remaining"] >= 0 for row in first["strategies"].values())
