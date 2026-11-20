import json

from game.campaign.ending import evaluate_campaign_ending
from game.campaign.service import record_story_mission_complete, tick_campaign
from game.character import Character
from game.gamestate import GameState
from game.ui.screens.campaign_ending_view import build_ending_summary


ACT_MISSIONS = {
    1: ("sm_act1_espionage", "sm_act1_recon", "sm_act1_witnesses"),
    2: ("sm_act2_drone", "sm_act2_data", "sm_act2_breakwater"),
    3: ("sm_act3_perf", "sm_act3_delhi", "sm_act3_names_below"),
    4: ("sm_act4_hungry", "sm_act4_archive", "sm_act4_two_voices"),
    5: ("sm_act5_citadel", "sm_act5_expose", "sm_act5_seven_minutes"),
}


def test_campaign_can_progress_from_act_one_to_a_finale() -> None:
    state = GameState(characters=[Character("Mara", nickname="Ghost")])

    for act, mission_ids in ACT_MISSIONS.items():
        assert state.campaign.current_act == act
        for mission_id in mission_ids:
            record_story_mission_complete(state, mission_id)

    assert state.campaign.current_act == 5
    assert state.campaign.ending is not None
    assert state.campaign.ending.outcome_id
    assert any("Mara" in line for line in state.campaign.ending.agent_epilogues)
    assert "campaign_complete" in state.campaign.act_triggers_seen


def test_each_act_has_exactly_the_story_missions_required_to_progress() -> None:
    from game.campaign.campaign_state import CampaignState
    from game.campaign.story_missions import story_missions_for_act

    campaign = CampaignState()
    all_ids: list[str] = []
    for act in range(1, 6):
        campaign.current_act = act
        missions = story_missions_for_act(act)
        assert len(missions) == campaign.missions_required == 3
        assert all(mission.briefing and mission.objective_text for mission in missions)
        all_ids.extend(mission.id for mission in missions)
    assert len(all_ids) == len(set(all_ids)) == 15


def test_story_mission_completion_is_idempotent() -> None:
    state = GameState()

    record_story_mission_complete(state, "sm_act1_espionage")
    record_story_mission_complete(state, "sm_act1_espionage")

    assert state.campaign.act_progress == 1
    assert state.campaign.completed_story_missions == ["sm_act1_espionage"]


def test_finale_evaluation_uses_world_and_agent_history() -> None:
    state = GameState(characters=[Character("Iris", reputation=["the Warsaw witness"])])
    state.campaign.discovered_intel = [f"intel_{index}" for index in range(18)]
    state.campaign.world.pharmacorp_secret = "exposed"
    state.campaign.world.ai_factions_status = "confirmed"
    state.campaign.world.perfs_status = "understood"
    state.campaign.world.new_delhi_status = "revealed"

    ending = evaluate_campaign_ending(state)

    assert ending.outcome_id == "human_coalition"
    assert any("P-77" in line for line in ending.world_lines)
    assert any("Iris" in line and "Warsaw witness" in line for line in ending.agent_epilogues)


def test_finale_round_trips_and_old_saves_default_safely(tmp_path) -> None:
    state = GameState(characters=[Character("Kade")])
    state.campaign.ending = evaluate_campaign_ending(state)
    save_path = tmp_path / "finale.json"
    state.save(str(save_path))

    loaded = GameState.load(str(save_path))
    assert loaded.campaign.ending == state.campaign.ending

    payload = json.loads(save_path.read_text(encoding="utf-8"))
    payload["campaign"].pop("ending")
    payload["campaign"].pop("completed_story_missions")
    save_path.write_text(json.dumps(payload), encoding="utf-8")
    legacy = GameState.load(str(save_path))
    assert legacy.campaign.ending is None
    assert legacy.campaign.completed_story_missions == []


def test_resolved_campaign_stops_ticking_and_builds_ui_payload() -> None:
    state = GameState(characters=[Character("Nyx")])
    state.campaign.ending = evaluate_campaign_ending(state)
    before = state.campaign.world.hungry_tide_progress
    state.calendar.current_day = 14

    tick_campaign(state)
    summary = build_ending_summary(state)

    assert state.campaign.world.hungry_tide_progress == before
    assert summary["outcome_id"] == state.campaign.ending.outcome_id
    assert summary["continue_action"] == "TitleView"
    assert any("Nyx" in line for line in summary["agent_epilogues"])


def test_fallen_agent_is_remembered_after_save_reload(tmp_path) -> None:
    fallen = Character("Rook", nickname="Ghost")
    state = GameState(characters=[fallen, Character("Nyx")])
    state.record_agent_death(fallen)
    state.record_agent_death(fallen)
    path = tmp_path / "memorial.json"
    state.save(str(path))

    loaded = GameState.load(str(path))
    ending = evaluate_campaign_ending(loaded)
    assert [agent.name for agent in loaded.characters] == ["Nyx"]
    assert ending.agent_epilogues.count('Rook "Ghost" lives on in the squad\'s roll of honour.') == 1
