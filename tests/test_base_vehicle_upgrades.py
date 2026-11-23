from game.gamestate import GameState


def test_base_and_vehicle_upgrades_purchase_atomically_and_persist(tmp_path):
    state = GameState()
    state.funds.current_funds = 100_000
    assert state.purchase_base_upgrade("trauma_center")[0]
    assert state.purchase_base_upgrade("field_medevac", vehicle=True)[0]
    balance = state.available_funds
    assert not state.purchase_base_upgrade("field_medevac", vehicle=True)[0]
    assert state.available_funds == balance
    path = tmp_path / "upgrades.json"
    state.save(path)
    restored = GameState.load(path)
    assert restored.base_upgrade_ids == ["trauma_center"]
    assert restored.vehicle_upgrade_ids == ["field_medevac"]
