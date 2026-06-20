from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from game.character import Character
from game.gamestate import GameState
from game.mission_system import (
    launch_selected_mission,
    resolve_mission_outcome,
    selected_mission,
)
from game.persistence.save_system import SaveSystem
from game.management.equipment import default_equipment_catalog
from game.recruitment import recruit_agent
from game.ui.screens.battle_debrief_view import (
    AgentDebriefStat,
    BattleDebriefView,
    build_battle_debrief_summary,
    build_consequence_summary_lines,
)
from game.ui.screens.mission_briefing_view import MissionBriefingView


class _FakeWindow:
    def __init__(self):
        self.shown_view = None

    def show_view(self, view):
        self.shown_view = view


class _FakeBattleView:
    def __init__(self, game_state):
        self.game_state = game_state
        self.mission = None

    def setup(self, mission):
        self.mission = mission


class _FakeManagementView:
    def __init__(self, game_state):
        self.game_state = game_state
        self.active_tab = None
        self.was_setup = False

    def setup(self):
        self.was_setup = True


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


@patch("game.ui.screens.management_screen.ManagementView", new=_FakeManagementView)
@patch("game.views.BattleView", new=_FakeBattleView)
@patch("game.combat.godot_bridge.launch_godot_combat_ui")
def test_end_to_end_mission_flow_regression(launch_mock):
    state = GameState(
        characters=[Character("Vera", role="sniper")],
        selected_agent_names=["Vera"],
    )
    selected = selected_mission(state)
    launch_mock.return_value = SimpleNamespace(
        handoff_path=Path("runtime/godot_combat/mission_handoff.json"),
        command=[],
        launched=False,
        ready_for_godot=False,
        message="Godot handoff created; no executable configured.",
    )

    mission = launch_selected_mission(state)
    assert mission.id == selected.id
    assert state.active_mission is mission

    briefing = MissionBriefingView.__new__(MissionBriefingView)
    briefing.game_state = state
    briefing.mission = mission
    briefing.window = _FakeWindow()
    briefing._launch_battle()

    battle = briefing.window.shown_view
    assert isinstance(battle, _FakeBattleView)
    assert battle.mission is mission
    assert (
        "Godot unavailable; launching local Arcade battle fallback."
        in state.event_log[-1]
    )

    triggered = resolve_mission_outcome(state, mission, victory=True)
    assert state.active_mission is None
    assert state.calendar.current_day >= 2

    agent_stats = [
        AgentDebriefStat(
            name="Vera",
            role="sniper",
            portrait_path=None,
            damage_dealt=6,
            damage_taken=0,
            kills=1,
            stress_delta=4,
            xp_gained=75,
            injuries=[],
        )
    ]
    summary = build_battle_debrief_summary(state, True, mission, agent_stats, triggered)
    consequences = build_consequence_summary_lines(
        state, True, mission, agent_stats, triggered
    )
    assert summary["continue_action"] == "ManagementView"
    assert summary["outcome"] == "victory"
    assert any(line.startswith("Rewards:") for line in consequences)

    debrief = BattleDebriefView.__new__(BattleDebriefView)
    debrief.game_state = state
    debrief.window = _FakeWindow()
    debrief._go_to_management()

    management = debrief.window.shown_view
    assert isinstance(management, _FakeManagementView)
    assert management.was_setup
    assert management.active_tab == "squad"


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
