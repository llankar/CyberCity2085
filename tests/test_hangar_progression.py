import json

from game.gamestate import GameState
from game.deployment import sanitize_selected_agent_names, toggle_agent_selection
from game.management.hangar_progression import HANGAR_LEVELS, HangarProgression
from game.recruitment import recruit_agent


def test_hangar_grid_is_fixed_and_exponential():
    assert HANGAR_LEVELS == (
        (1, "Standard Hangar", 5, 0),
        (2, "Expanded Quarters", 6, 20_000),
        (3, "Tactical Hangar", 7, 60_000),
        (4, "Operations Base", 8, 180_000),
    )
    assert sum(row[3] for row in HANGAR_LEVELS) == 260_000


def test_hangar_upgrades_are_ordered_atomic_and_stop_at_level_four():
    state = GameState()
    state.funds.current_funds = 260_000
    for level, expected_cost in ((2, 20_000), (3, 60_000), (4, 180_000)):
        before = state.available_funds
        ok, _ = state.upgrade_hangar()
        assert ok and state.hangar.level == level
        assert state.squad_capacity == level + 4
        assert state.available_funds == before - expected_cost
    before = state.available_funds
    assert state.upgrade_hangar()[0] is False
    assert state.available_funds == before


def test_failed_hangar_upgrade_changes_nothing():
    state = GameState()
    state.funds.current_funds = 19_999
    history = len(state.funds.transaction_history)
    assert state.upgrade_hangar()[0] is False
    assert state.hangar.level == 1 and state.available_funds == 19_999
    assert len(state.funds.transaction_history) == history


def test_legacy_save_preserves_large_roster_and_owned_loadouts(tmp_path):
    state = GameState()
    for role in ("samurai", "sniper", "psi", "samurai", "sniper", "psi", "samurai"):
        recruit_agent(state.characters, role)
    state.selected_agent_names = [agent.name for agent in state.characters]
    path = tmp_path / "legacy.json"
    state.save(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data.pop("hangar")
    data.pop("owned_equipment")
    path.write_text(json.dumps(data), encoding="utf-8")
    restored = GameState.load(path)
    assert len(restored.characters) == 7
    assert restored.hangar.level == 1 and restored.squad_capacity == 5
    assert restored.selected_agent_names == [agent.name for agent in restored.characters[:5]]
    assert sum(restored.owned_equipment.values()) >= 7


def test_recruitment_is_not_limited_by_hangar_squad_capacity():
    state = GameState(hangar=HangarProgression(1))
    for index in range(state.squad_capacity + 4):
        recruit_agent(state.characters, "samurai", f"Spare-{index}")
    assert len(state.characters) == 9
    assert state.can_recruit() is True
    assert state.squad_capacity == 5


def test_hangar_capacity_limits_selected_mission_squad_not_roster():
    state = GameState(hangar=HangarProgression(1))
    for index in range(9):
        recruit_agent(state.characters, "samurai", f"Reserve-{index}")
    all_names = [agent.name for agent in state.characters]

    selected = sanitize_selected_agent_names(
        state.characters, all_names, state.squad_capacity
    )
    assert selected == all_names[:5]
    selected, message = toggle_agent_selection(
        state.characters, selected, 5, state.squad_capacity
    )
    assert selected == all_names[:5]
    assert "Squad capacity reached (5)" in message
    assert len(state.characters) == 9


def test_hangar_roundtrip(tmp_path):
    state = GameState(hangar=HangarProgression(4), owned_equipment={"katana": 2})
    path = tmp_path / "state.json"
    state.save(path)
    restored = GameState.load(path)
    assert restored.hangar.level == 4
    assert restored.squad_capacity == 8
    assert restored.owned_equipment == {"katana": 2}
