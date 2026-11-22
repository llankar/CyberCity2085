"""Story progression uses the shared mission lifecycle, independently of UI."""

from types import SimpleNamespace
from unittest.mock import patch

from game.character import Character
from game.gamestate import GameState
from game.missions.flow import ensure_mission_templates, launch_selected_mission, resolve_mission_outcome
from game.persistence import SaveSystem


def _resolve_arcade_simulation(state, mission, result):
    """Feed a completed real-engine simulation through Arcade's shared resolver."""
    from game.combat.mission_resolution import resolve_campaign_battle
    from game.combat.state import CombatState
    from game.mission_system import resolve_mission_outcome
    from game.unit import Unit

    units = [
        Unit((64, 64 + index * 64), stats=character.stats,
             health=character.stats.hp, character=character)
        for index, character in enumerate(state.characters)
    ]
    combat_state = CombatState(mission, units, [])
    context = SimpleNamespace(
        game_state=state,
        mission=mission,
        player_units=units,
        defeated_player_units=[],
        enemy_units=[],
        initial_enemy_count=result["count"],
        triggered_complication=None,
        combat_state=combat_state,
        resolve_defeated_player_unit=lambda _unit: None,
    )
    context.resolve_mission_outcome = lambda victory: setattr(
        context,
        "triggered_complication",
        resolve_mission_outcome(state, mission, victory, context.triggered_complication),
    )
    return resolve_campaign_battle(
        context,
        True,
        defeated_override=result["count"] - result["enemy_survivors"],
    )


def launch_story(state):
    ensure_mission_templates(state)
    state.selected_mission_index=next(i for i,m in enumerate(state.mission_templates) if m.id.startswith("sm_"))
    return launch_selected_mission(state)


def test_shared_resolution_reaches_finale_through_fifteen_actual_board_missions(tmp_path):
    state=GameState(characters=[Character("Mara")],selected_agent_names=["Mara"])
    completed=[]
    with patch("game.gamestate.roll_random_event"), patch("game.audio.SoundManager.get"):
        state.advance_one_day("refresh introductory board")
        for index in range(15):
            mission=launch_story(state)
            assert mission.id not in completed
            assert state.campaign.current_act==index//3+1
            resolve_mission_outcome(state,mission,True)
            completed.append(mission.id)
            assert mission.id in state.campaign.completed_story_missions
            assert f"story_complete_{mission.id}" in state.campaign.act_triggers_seen
            assert state.active_mission is None
            path=tmp_path/"story_flow.json"
            assert SaveSystem.save_game(state,path).ok
            state,status=SaveSystem.load_game(path)
            assert status.ok
    assert state.campaign.completed_story_missions==completed
    assert state.campaign.ending is not None
    assert "campaign_complete" in state.campaign.act_triggers_seen


def test_failed_story_mission_remains_available_without_progress():
    state=GameState()
    with patch("game.gamestate.roll_random_event"), patch("game.audio.SoundManager.get"):
        state.advance_one_day("refresh introductory board")
        mission=launch_story(state)
        resolve_mission_outcome(state,mission,False)
        assert not state.campaign.completed_story_missions
        assert state.campaign.act_progress==0
        assert launch_story(state).id==mission.id


def test_fifteen_real_arcade_fallback_combats_reach_finale_with_save_reload(tmp_path):
    from game.battle_maps import select_battle_map_entry
    from game.combat.encounter_qa import simulate_encounter

    state = GameState(
        characters=[Character(name) for name in ("Rook", "Echo", "Nyx", "Mara")],
        selected_agent_names=["Rook", "Echo", "Nyx", "Mara"],
    )
    combat_rows = []
    with patch("game.gamestate.roll_random_event"), patch("game.audio.SoundManager.get"):
        state.advance_one_day("refresh introductory board")
        for index in range(15):
            mission = launch_story(state)
            entry = select_battle_map_entry(mission)
            result = simulate_encounter(
                theme=mission.enemy_theme,
                level=4,
                risk=mission.risk_level,
                count=mission.starting_enemy_count,
                seed=1,
                policy="objective_counterplay",
                max_turns=60,
                map_path=entry.path,
                mission_template=mission,
            )
            assert result["outcome"] == "victory", (mission.id, result)
            assert result["mission_id"] == mission.id
            assert result["geometry_checked"] and result["terrain_source"] == "manual_wall_traces_v1"
            _resolve_arcade_simulation(state, mission, result)
            combat_rows.append((mission.id, result["turns"], result["objective_reason"]))
            assert state.latest_mission_debrief["mission_title"] == mission.title
            assert state.latest_mission_debrief["mission_outcome"] == "victory"
            assert state.active_mission is None
            save = tmp_path / "fallback_campaign.json"
            assert SaveSystem.save_game(state, save).ok
            state, status = SaveSystem.load_game(save)
            assert status.ok
            assert len(state.campaign.completed_story_missions) == index + 1

    assert len(combat_rows) == 15
    assert state.campaign.ending is not None
    assert "campaign_complete" in state.campaign.act_triggers_seen
