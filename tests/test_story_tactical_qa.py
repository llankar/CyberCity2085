from game.campaign.story_missions import STORY_MISSIONS
from game.gamestate import GameState
from game.mission_generation import story_mission_to_template, generate_mission_board
from game.combat.encounter_qa import simulate_encounter


def test_board_and_qa_share_exact_authored_story_template():
    state=GameState()
    for act in range(1,6):
        state.campaign.current_act=act
        board=generate_mission_board(state)
        mission=next(m for m in board if m.id.startswith("sm_"))
        story=next(s for s in STORY_MISSIONS if s.id==mission.id)
        assert story_mission_to_template(story,state).to_dict()==mission.to_dict()


def test_every_story_objective_survives_launch_and_save_cloning():
    from game.mission_templates import MissionTemplate
    state=GameState()
    for story in STORY_MISSIONS:
        mission=story_mission_to_template(story,state)
        assert MissionTemplate.from_dict(mission.to_dict()).objective_type==story.objective_type


def test_authored_mission_overrides_generic_qa_parameters_without_mutation():
    from game.battle_maps import select_battle_map_entry
    mission=story_mission_to_template(STORY_MISSIONS[0],GameState())
    before=mission.to_dict()
    row=simulate_encounter(theme="starver",level=4,risk=1,count=1,seed=0,
                            objective_kind="eliminate",mission_template=mission,
                            map_path=select_battle_map_entry(mission).path,
                            policy="objective_counterplay",max_turns=2)
    assert row["mission_id"]==mission.id
    assert row["count"]==mission.starting_enemy_count
    assert row["risk"]==mission.risk_level and row["objective_kind"]=="data_theft"
    assert row["theme"]==mission.enemy_theme
    assert mission.to_dict()==before
