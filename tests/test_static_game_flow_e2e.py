from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from game.character import Character
from game.gamestate import GameState
from game.missions.flow import (
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
    state.combat_mission_ui_engine = "godot"  # Exercise the explicit optional-engine fallback.
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


def test_real_battle_memory_survives_debrief_management_and_campaign_save(tmp_path):
    from game import views
    from game.combat import CombatEngine, CombatState
    from game.management.equipment import Weapon
    from game.mission_templates import MissionTemplate
    from game.stats import EnemyStats
    from game.unit import Unit
    character=Character("Rook",traits=["brave"])
    character.loadout.primary_weapon=Weapon("blade","Blade","primary_weapon",range_cells=1,attack_stat="str")
    state=GameState(characters=[character],selected_agent_names=[character.name])
    mission=MissionTemplate("memory_flow","Memory Flow","Defeat the hostile","","",{},1,duration_days=1,fund_reward=10)
    state.active_mission=mission
    actor=Unit(position=(0,0),stats=character.stats,character=character)
    enemy=Unit(position=(32,0),stats=EnemyStats(),unit_type="enemy")
    actor.health=actor.stats.hp=1
    enemy.health=enemy.stats.hp=1
    battle=views.BattleView.__new__(views.BattleView)
    battle.game_state=state
    battle.window=_FakeWindow()
    battle.mission=mission
    battle.initial_enemy_count=1
    battle.triggered_complication=None
    battle.player_units=[actor]
    battle.enemy_units=[enemy]
    battle.defeated_player_units=[]
    battle.combat_state=CombatState(mission,battle.player_units,battle.enemy_units)
    battle.combat_engine=CombatEngine(battle.combat_state)
    battle.combat_engine.start_player_turn()
    with patch("game.combat.attack_resolution.random.random",return_value=0):
        result=battle.combat_engine.perform_action("melee",actor=actor,target=enemy)
    assert result.defeated_target
    battle._set_action_aftermath(action_label="MELEE",damage=result.damage,
                                status_applied="CRITICAL" if result.attack_resolution.critical else "HIT",
                                defeated_target=result.defeated_target)
    assert "HOSTILE DOWN" in battle._aftermath_line
    assert "SUPPRESSION" not in battle._aftermath_line
    day=state.calendar.current_day
    with patch("game.gamestate.roll_random_event"), patch.object(BattleDebriefView.__bases__[0], "__init__", return_value=None):
        battle.end_battle(True)
    assert state.active_mission is None
    assert state.calendar.current_day>day
    assert state.latest_mission_debrief["tactical_moments"][0]["kind"]=="last_stand"
    assert "Memory Flow" in state.latest_mission_debrief["lines"][0]["text"]
    debrief=battle.window.shown_view
    assert isinstance(debrief,BattleDebriefView)
    summary=build_battle_debrief_summary(state,True,mission,debrief.agent_stats)
    assert "neutralized a hostile" in summary["narrative_consequences"][0]
    assert state.faction_reward_journal
    debrief.window=_FakeWindow()
    with patch("game.ui.screens.management_screen.ManagementView",new=_FakeManagementView):
        debrief._go_to_management()
    assert debrief.window.shown_view.game_state is state
    assert debrief.window.shown_view.active_tab=="squad"
    path=tmp_path/"after_real_battle.json"
    assert SaveSystem.save_game(state,path).ok
    loaded,status=SaveSystem.load_game(path)
    assert status.ok
    assert loaded.latest_mission_debrief["tactical_moments"]==state.latest_mission_debrief["tactical_moments"]
    assert any("neutralized a hostile" in line for line in loaded.characters[0].history)


def test_surviving_armor_keeps_pilot_hp_separate_and_reports_pilot_in_debrief():
    from game import views
    from game.combat_system import create_player_units
    from game.management.spec_ops_assets import default_spec_ops_assets
    from game.mission_templates import MissionTemplate
    from unittest.mock import Mock
    pilot=Character("Mara")
    pilot.stats.hp=5
    state=GameState(characters=[pilot],selected_agent_names=[pilot.name])
    suit=default_spec_ops_assets()[2]
    suit.pilot_agent_name=pilot.name
    units=create_player_units([pilot],[pilot.name],[suit],[suit.id])
    assert units[0].character is pilot and units[0].health>pilot.stats.max_hp
    battle=views.BattleView.__new__(views.BattleView)
    battle.game_state=state
    battle.window=_FakeWindow()
    battle.mission=MissionTemplate("armor_flow","Armor Flow","Hold","","",{},1)
    battle.initial_enemy_count=0
    battle.triggered_complication=None
    battle.player_units=units
    battle.enemy_units=[]
    battle.defeated_player_units=[]
    battle.resolve_mission_outcome=Mock()  # Isolate HP transfer from strategic recovery.
    with patch.object(BattleDebriefView.__bases__[0],"__init__",return_value=None):
        battle.end_battle(True)
    assert pilot.stats.hp==5
    assert any(line["agent_name"]==pilot.name for line in state.latest_mission_debrief["lines"])
