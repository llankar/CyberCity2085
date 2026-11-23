from game.gamestate import GameState
from game.management.equipment import default_equipment_catalog, equipment_purchase_price


def test_equipment_prices_are_deterministic_and_reward_power():
    catalog = default_equipment_catalog()
    pulse = next(item for item in catalog["primary_weapon"] if item.id == "pulse_rifle")
    gravity = next(item for item in catalog["primary_weapon"] if item.id == "gravity_lance")
    assert equipment_purchase_price(pulse) == equipment_purchase_price(pulse)
    assert 50 <= equipment_purchase_price(pulse) < equipment_purchase_price(gravity)
    assert equipment_purchase_price(gravity) >= 1_500


def test_equipment_purchase_is_atomic_and_not_paid_twice():
    item = default_equipment_catalog()["sidearm"][0]
    price = equipment_purchase_price(item)
    state = GameState()
    state.funds.current_funds = price
    assert state.purchase_equipment(item)[0]
    assert state.available_funds == 0 and state.owned_equipment == {item.id: 1}
    history = len(state.funds.transaction_history)
    assert not state.purchase_equipment(item)[0]
    assert state.available_funds == 0 and len(state.funds.transaction_history) == history


def test_unaffordable_equipment_purchase_has_no_partial_effect():
    item = default_equipment_catalog()["armor"][-1]
    state = GameState()
    state.funds.current_funds = equipment_purchase_price(item) - 1
    before = state.available_funds
    assert not state.purchase_equipment(item)[0]
    assert state.available_funds == before and not state.owned_equipment
