from pathlib import Path

from game.gamestate import GameState
from game.mission_system import resolve_mission_outcome, selected_mission
from game.persistence.save_system import SaveSystem
from game.management.equipment import default_equipment_catalog
from game.recruitment import recruit_agent


def test_advancing_day_updates_calendar_and_logs():
    state = GameState()
    before_day = state.calendar.current_day
    before_log_count = len(state.event_log)

    state.advance_one_day("test progression")

    assert state.calendar.current_day == before_day + 1
    assert len(state.event_log) >= before_log_count


def test_mission_completion_applies_rewards_or_penalties():
    state = GameState()
    mission = selected_mission(state)
    before_funds = state.available_funds

    resolve_mission_outcome(
        state,
        mission,
        victory=True,
        triggered_complication=mission.possible_complications[0] if mission.possible_complications else None,
    )

    assert state.calendar.current_day >= 2
    assert state.available_funds >= before_funds
    assert state.faction_reward_journal


def test_events_research_equipment_persist_across_save_load(tmp_path: Path):
    state = GameState()
    state.active_events = state.active_events[:1]
    available = state.research_tree.available_projects(set(), set())
    if available:
        state.start_research(available[0].id)
    recruit_agent(state.characters, "samurai")
    agent = state.characters[0]
    catalog = default_equipment_catalog()
    agent.loadout.equip("primary_weapon", catalog["primary_weapon"][0])

    save_path = tmp_path / "flow_save.json"
    save_result = SaveSystem.save_game(state, save_path)
    assert save_result.ok

    loaded, load_result = SaveSystem.load_game(save_path)
    assert load_result.ok
    assert loaded is not None
    assert len(loaded.active_events) == len(state.active_events)
    assert len(loaded.active_research) == len(state.active_research)
    assert loaded.calendar.current_day == state.calendar.current_day
    assert loaded.characters[0].loadout.primary_weapon is not None
