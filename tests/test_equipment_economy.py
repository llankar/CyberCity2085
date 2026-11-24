from game.gamestate import GameState
from game.management.equipment import (
    AVAILABILITY_COMMERCIAL,
    AVAILABILITY_RESEARCH,
    AVAILABILITY_STARTER,
    default_equipment_catalog,
    equipment_power_score,
    equipment_purchase_price,
    initial_armory_stock,
)
from game.recruitment import recruit_agent


def test_equipment_prices_are_deterministic_and_reward_power():
    catalog = default_equipment_catalog()
    pulse = next(item for item in catalog["primary_weapon"] if item.id == "pulse_rifle")
    gravity = next(item for item in catalog["primary_weapon"] if item.id == "gravity_lance")
    assert equipment_purchase_price(pulse) == equipment_purchase_price(pulse)
    assert 50 <= equipment_purchase_price(pulse) < equipment_purchase_price(gravity)
    assert equipment_purchase_price(gravity) >= 1_500


def test_equipment_purchase_adds_real_quantities():
    item = default_equipment_catalog()["sidearm"][0]
    price = equipment_purchase_price(item)
    state = GameState()
    state.funds.current_funds = price * 2
    assert state.purchase_equipment(item)[0]
    assert state.purchase_equipment(item)[0]
    assert state.available_funds == 0 and state.owned_equipment == {item.id: 2}


def test_unaffordable_equipment_purchase_has_no_partial_effect():
    item = default_equipment_catalog()["armor"][-1]
    state = GameState()
    state.funds.current_funds = equipment_purchase_price(item) - 1
    before = state.available_funds
    assert not state.purchase_equipment(item)[0]
    assert state.available_funds == before and not state.owned_equipment


def test_catalogue_classification_is_stable_and_power_ordered_per_family():
    first = default_equipment_catalog()
    second = default_equipment_catalog()
    for family, items in first.items():
        assert [(item.id, item.availability_group) for item in items] == [
            (item.id, item.availability_group) for item in second[family]
        ]
        groups = {group: [] for group in (
            AVAILABILITY_STARTER, AVAILABILITY_COMMERCIAL, AVAILABILITY_RESEARCH
        )}
        for item in items:
            groups[item.availability_group].append(equipment_power_score(item))
            assert item.family == family
        assert groups[AVAILABILITY_STARTER]
        assert groups[AVAILABILITY_COMMERCIAL]
        assert groups[AVAILABILITY_RESEARCH]
        assert max(groups[AVAILABILITY_STARTER]) <= min(groups[AVAILABILITY_COMMERCIAL])
        assert max(groups[AVAILABILITY_COMMERCIAL]) <= min(groups[AVAILABILITY_RESEARCH])


def test_initial_armory_is_six_functional_kits_and_granted_once():
    expected = initial_armory_stock(6)
    assert sum(expected.values()) == 24
    state = GameState()
    assert state.grant_initial_armory()
    assert state.owned_equipment == expected
    assert not state.grant_initial_armory()
    assert state.owned_equipment == expected


def test_loaded_legacy_save_does_not_receive_retroactive_armory(tmp_path):
    path = tmp_path / "legacy.json"
    state = GameState(owned_equipment={"pulse_rifle": 1})
    state.save(path)
    import json
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.pop("initial_armory_granted")
    path.write_text(json.dumps(payload), encoding="utf-8")
    restored = GameState.load(path)
    assert restored.initial_armory_granted
    assert restored.owned_equipment == {"pulse_rifle": 1}
    assert not restored.grant_initial_armory()


def test_recruitment_never_generates_free_equipment():
    roster = []
    recruit = recruit_agent(roster, "samurai", "Reserve")
    assert recruit.loadout.equipped_items() == []


def test_research_items_require_their_real_family_project():
    item = next(
        item
        for item in default_equipment_catalog()["primary_weapon"]
        if item.availability_group == AVAILABILITY_RESEARCH
    )
    state = GameState()
    state.funds.current_funds = equipment_purchase_price(item)
    ok, message = state.purchase_equipment(item)
    assert not ok and "Research required" in message
    assert item.research_project_id in state.research_tree.projects
    state.completed_research.append(item.research_project_id)
    ok, _ = state.purchase_equipment(item)
    assert ok and state.owned_equipment[item.id] == 1
