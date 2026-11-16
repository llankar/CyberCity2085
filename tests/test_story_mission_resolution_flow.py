"""Story progression uses the shared mission lifecycle, independently of UI."""

from unittest.mock import patch

from game.character import Character
from game.gamestate import GameState
from game.missions.flow import ensure_mission_templates, launch_selected_mission, resolve_mission_outcome
from game.persistence import SaveSystem


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
