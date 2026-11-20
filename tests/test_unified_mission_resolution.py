"""Actual campaign consequences, shadow rollback, session validation and replay."""
import copy,json
from pathlib import Path
from unittest.mock import patch
import pytest
from game.character import Character
from game.gamestate import GameState
from game.mission_templates import MissionTemplate
from game.combat.godot_bridge import write_godot_combat_handoff
from game.combat.session_protocol import create_session,validate_result
from game.combat.godot_resolution import resolve_godot_result


def test_result_published_during_exit_poll_is_read_next_tick(tmp_path):
    from types import SimpleNamespace
    from unittest.mock import Mock
    from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView

    result_path = tmp_path / "result.json"
    payload = {"outcome": "victory"}

    def publish_then_exit():
        result_path.write_text(json.dumps(payload), encoding="utf-8")
        return 0

    view = GodotCombatHandoffView.__new__(GodotCombatHandoffView)
    view._result_applied = False
    view._launch_failed = False
    view.game_state = SimpleNamespace(combat_sessions={})
    view.launch_result = SimpleNamespace(
        result_path=result_path, process=SimpleNamespace(poll=publish_then_exit)
    )
    view._apply_combat_result = Mock()
    view._cleanup_godot = Mock()

    with patch("game.combat.godot_bridge.read_godot_combat_result", return_value=payload) as read:
        view.on_update(0.1)
        read.assert_not_called()
        assert not view._launch_failed
        view._cleanup_godot.assert_not_called()
        view.on_update(0.1)
        read.assert_called_once_with(result_path, raise_io_errors=True)
        view._apply_combat_result.assert_called_once_with(payload)


def test_real_mission_driver_cannot_force_terminal_state():
    source = Path("godot/combat_missions_ui/tests/unified_real_mission_flow.gd").read_text(encoding="utf-8")
    forbidden = (
        "scene._end_combat(",
        "scene._complete_mission(",
        "scene.objective_completed =",
        "scene.objective_completed=",
        "scene._results.show_results(",
    )
    assert not any(token in source for token in forbidden)
    assert "scene._move_active_unit_to(destination)" in source
    assert "scene._interact_with_objective()" in source
    assert "scene._resolve_enemy_turn()" in source


def test_godot_retreat_is_visible_confirmed_and_uses_normal_result_path():
    scene = Path("godot/combat_missions_ui/scripts/combat_mission_ui.gd").read_text(encoding="utf-8")
    hud = Path("godot/combat_missions_ui/scripts/hud_controller.gd").read_text(encoding="utf-8")
    visual = Path("godot/combat_missions_ui/scripts/visual_hud.gd").read_text(encoding="utf-8")
    assert '["RETREAT", "NEXT", "END TURN"]' in hud
    assert "RETREAT [R]" in visual
    assert 'if action_name == "RETREAT":' in scene
    assert "if pending_retreat_confirmation:" in scene
    assert '_end_combat("retreat")' in scene


def scenario(tmp_path, fund_reward=0):
    agent=Character('Vera',role='sniper')
    state=GameState(characters=[agent],selected_agent_names=['Vera'])
    mission=MissionTemplate(id='unified_test',title='Unified test',objective_text='Extract',target_faction='Corp 37',district='Chrome',district_pressure={},starting_enemy_count=3,risk_level=2,objective_type='extract',fund_reward=fund_reward)
    state.active_mission=mission
    path=write_godot_combat_handoff(state,mission,handoff_path=tmp_path/'handoff.json')
    path,session=create_session(state,mission,path)
    result=dict(protocol_version=2,session_id=session['session_id'],mission_id=mission.id,phase='confirmed',outcome='victory',turn_reached=4,initial_enemy_count=3,enemies_killed=1,agents=[dict(name='Vera',hp=7,max_hp=agent.stats.max_hp,stress=8)],support=[])
    return state,mission,session,result


def test_victory_uses_common_campaign_rules_and_does_not_trust_engine_rewards(tmp_path):
    state,mission,session,result=scenario(tmp_path, fund_reward=120)
    before=state.available_funds
    context,survivors,units=resolve_godot_result(state,mission,result,session['session_id'])
    assert state.characters[0].stats.max_hp-state.characters[0].stats.hp==4
    assert state.characters[0].stats.level==2 and state.characters[0].stats.xp==50
    assert state.characters[0]._mission_xp_gained==150  # Existing promotion/healing policy.
    assert state.strategic_resources['credits']>=26
    assert state.available_funds>=before
    assert state.active_mission is None
    assert state.latest_mission_debrief['campaign_rewards']['resources']['credits']==26
    rewards = state.latest_mission_debrief['campaign_rewards']
    assert rewards['mission_payout'] == 120
    assert rewards['mission_payout'] == sum(
        tx.amount for tx in state.funds.transaction_history if tx.source == 'mission_reward'
    )
    assert state.latest_mission_debrief and state.latest_agent_aftermath
    assert not hasattr(units[0],'_kills') and not hasattr(units[0],'_damage_taken')
    assert state.combat_sessions[session['session_id']]['status']=='applied'


@pytest.mark.parametrize('outcome',['defeat','retreat'])
def test_non_victory_keeps_failure_policy_without_synthetic_xp(tmp_path,outcome):
    state,mission,session,result=scenario(tmp_path);result['outcome']=outcome
    before = state.available_funds
    resolve_godot_result(state,mission,result,session['session_id'])
    assert state.characters[0].stats.xp==0
    assert state.active_mission is None and state.latest_mission_debrief
    rewards = state.latest_mission_debrief['campaign_rewards']
    assert rewards['mission_payout'] == 0
    assert rewards['net_funds_change'] == state.available_funds - before


@pytest.mark.parametrize('mutation',[
    lambda r:r.update(session_id='wrong'),lambda r:r.update(mission_id='wrong'),
    lambda r:r.update(phase='prepared'),lambda r:r.update(outcome='unknown'),
    lambda r:r.update(funds_earned=999999),lambda r:r.update(agents=[]),
    lambda r:r['agents'][0].update(hp=-1),lambda r:r['agents'][0].update(name='nondeployed'),
    lambda r:r['agents'][0].update(max_hp=999),lambda r:r.update(enemies_killed=5),
    lambda r:r.update(turn_reached=True),lambda r:r.update(music_playback={'position':float('nan')}),
])
def test_invalid_result_never_mutates_campaign(tmp_path,mutation):
    state,mission,session,result=scenario(tmp_path);before=copy.deepcopy(state.__dict__);mutation(result)
    with pytest.raises(ValueError):resolve_godot_result(state,mission,result,session['session_id'])
    assert state.__dict__==before


def test_resolution_failure_rolls_back_all_campaign_changes(tmp_path):
    state,mission,session,result=scenario(tmp_path);before=copy.deepcopy(state.__dict__)
    with patch('game.combat.godot_resolution.resolve_mission_outcome',side_effect=RuntimeError('fail after rewards')):
        with pytest.raises(RuntimeError):resolve_godot_result(state,mission,result,session['session_id'])
    assert state.__dict__==before


def test_replay_after_save_reload_and_changed_music_bookmark_cannot_duplicate_rewards(tmp_path):
    state,mission,session,result=scenario(tmp_path)
    resolve_godot_result(state,mission,result,session['session_id'])
    save=tmp_path/'campaign.json';state.save(str(save));restored=GameState.load(str(save));before=copy.deepcopy(restored.__dict__)
    result['music_playback']={'position':50,'path':'music'}
    assert resolve_godot_result(restored,mission,result,session['session_id']) is None
    assert restored.__dict__==before
    result['agents'][0]['hp']=6
    with pytest.raises(ValueError):resolve_godot_result(restored,mission,result,session['session_id'])
    assert restored.__dict__==before


def test_new_session_supersedes_old_pending_session_and_has_isolated_paths(tmp_path):
    state,mission,session,result=scenario(tmp_path)
    _,other=create_session(state,mission,tmp_path/'handoff.json')
    assert session['result_path']!=other['result_path']
    assert state.combat_sessions[session['session_id']]['status']=='superseded'
    with pytest.raises(ValueError):resolve_godot_result(state,mission,result,session['session_id'])


def test_downed_outcomes_reuse_campaign_injury_system(tmp_path):
    state,mission,session,result=scenario(tmp_path);result['agents'][0]['hp']=0
    with patch('game.battle_outcomes.random.choice',return_value='critically injured'):
        context,survivors,units=resolve_godot_result(state,mission,result,session['session_id'])
    assert len(state.characters)==1 and state.characters[0].stats.hp>0
    assert 'Critical battle trauma' in state.characters[0].injuries
    assert not survivors


def test_last_stand_memory_is_validated_saved_and_applied_once(tmp_path):
    state, mission, session, result = scenario(tmp_path)
    session_id = session["session_id"]
    result["agents"][0]["last_stand_hp"] = result["agents"][0]["max_hp"]
    with pytest.raises(ValueError, match="last_stand_hp"):
        resolve_godot_result(state, mission, result, session_id)
    result["agents"][0]["last_stand_hp"] = 1
    assert resolve_godot_result(state, mission, result, session_id) is not None
    path = tmp_path / "campaign.json"
    state.save(str(path))
    loaded = GameState.load(str(path))
    assert resolve_godot_result(loaded, mission, result, session_id) is None
    assert sum("held on at 1 HP" in line for line in loaded.characters[0].history) == 1
    assert loaded.latest_mission_debrief["tactical_moments"][0]["kind"] == "last_stand"


def test_native_godot_exports_last_stand_for_campaign_debrief(tmp_path):
    import subprocess
    from game.combat.godot_bridge import find_godot_executable

    godot = find_godot_executable()
    if not godot:
        pytest.skip("Godot unavailable")
    state, mission, session, _ = scenario(tmp_path)
    result_path = Path(session["result_path"])
    project = Path(__file__).resolve().parents[1] / "godot/combat_missions_ui"
    proc = subprocess.run([
        godot, "--headless", "--audio-driver", "Dummy", "--path", str(project),
        "--script", "res://tests/last_stand_regression.gd", "--",
        "--handoff", str(result_path.with_name("handoff.json")),
    ], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=25)
    assert proc.returncode == 0 and "GODOT_LAST_STAND_CHECKS_PASSED" in proc.stdout, proc.stdout + proc.stderr
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["agents"][0]["last_stand_hp"] == 1
    assert resolve_godot_result(state, mission, result, session["session_id"]) is not None
    assert state.latest_mission_debrief["tactical_moments"][0]["agent_name"] == "Vera"


def test_confirmed_death_uses_the_existing_roster_removal_rule(tmp_path):
    state,mission,session,result=scenario(tmp_path);result['agents'][0]['hp']=0
    with patch('game.battle_outcomes.random.choice',return_value='killed'):
        _,survivors,units=resolve_godot_result(state,mission,result,session['session_id'])
    assert state.characters==[] and state.selected_agent_names==[] and survivors==[]
    assert units[0].character.name=='Vera'
    assert state.latest_mission_debrief["tactical_moments"][0]["kind"] == "downed"


def test_godot_downed_agent_and_witness_remember_a_survived_injury(tmp_path):
    state, mission, _, result = scenario(tmp_path)
    witness = Character("Rook", relationships={"Vera": 5})
    state.characters.append(witness)
    state.selected_agent_names.append(witness.name)
    path = write_godot_combat_handoff(state, mission, handoff_path=tmp_path / "two-agents.json")
    _, session = create_session(state, mission, path)
    result["session_id"] = session["session_id"]
    result["agents"][0]["hp"] = 0
    result["agents"].append(dict(name="Rook", hp=witness.stats.hp, max_hp=witness.stats.max_hp))
    with patch("game.battle_outcomes.random.choice", return_value="critically injured"):
        resolve_godot_result(state, mission, result, session["session_id"])
    recovered, observer = state.characters
    assert recovered.stats.hp > 0
    assert any("Vera fell during" in line for line in recovered.history)
    assert any("saw Vera fall under fire" in line for line in observer.history)
    assert resolve_godot_result(state, mission, result, session["session_id"]) is None
    assert sum("saw Vera fall under fire" in line for line in observer.history) == 1


def test_real_support_damage_updates_maintenance_once(tmp_path):
    from game.management.spec_ops_assets import CombatRobot,ArmorRating
    state,mission,_,_=scenario(tmp_path)
    robot=CombatRobot(id='drone',name='Drone',armor=ArmorRating(),hardpoints=[])
    state.spec_ops_assets=[robot];state.selected_asset_ids=['drone']
    path=write_godot_combat_handoff(state,mission,handoff_path=tmp_path/'support-handoff.json')
    _,session=create_session(state,mission,path);record=state.combat_sessions[session['session_id']]
    maximum=record['expected_support'][0]['max_hp']
    result=dict(protocol_version=2,session_id=session['session_id'],mission_id=mission.id,phase='confirmed',outcome='retreat',turn_reached=2,initial_enemy_count=3,enemies_killed=0,agents=[dict(name='Vera',hp=7,max_hp=11)],support=[dict(id='drone',name='Drone',hp=0,max_hp=maximum)])
    resolve_godot_result(state,mission,result,session['session_id'])
    integrity=state.spec_ops_assets[0].maintenance.integrity
    assert integrity==0 and state.latest_spec_ops_outcomes[0]['damage']==100
    assert resolve_godot_result(state,mission,result,session['session_id']) is None
    assert state.spec_ops_assets[0].maintenance.integrity==integrity


def test_reinforcement_count_is_bounded_by_actual_spawned_total(tmp_path):
    state,mission,session,result=scenario(tmp_path)
    result['enemies_spawned_total']=5;result['enemies_killed']=4
    validate_result(result,state.combat_sessions[session['session_id']],session['session_id'])
    result['enemies_killed']=6
    with pytest.raises(ValueError):validate_result(result,state.combat_sessions[session['session_id']],session['session_id'])


def test_ack_io_failure_does_not_claim_campaign_rollback_or_apply_twice(tmp_path):
    from types import SimpleNamespace
    from unittest.mock import Mock
    from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView
    state,mission,session,result=scenario(tmp_path)
    bridge=GodotCombatHandoffView.__new__(GodotCombatHandoffView)
    bridge.game_state=state;bridge.mission=mission;bridge.launch_result=SimpleNamespace(session_id=session['session_id'])
    bridge._cleanup_godot=Mock();bridge._return_to_management=Mock()
    with patch('game.combat.session_protocol.atomic_json',side_effect=OSError('disk unavailable')):
        bridge._apply_combat_result(result)
        before=copy.deepcopy(state.__dict__)
        assert 'Result applied' in bridge._status and bridge._result_applied
        bridge._cleanup_godot.assert_not_called()
        bridge._apply_combat_result(result)
    assert state.__dict__==before


def test_manual_fallback_invalidates_the_pending_session(tmp_path):
    from types import SimpleNamespace
    from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView
    state,mission,session,result=scenario(tmp_path)
    bridge=GodotCombatHandoffView.__new__(GodotCombatHandoffView)
    bridge.game_state=state;bridge.launch_result=SimpleNamespace(session_id=session['session_id'])
    bridge._abandon_session()
    assert state.combat_sessions[session['session_id']]['status']=='abandoned'
    with pytest.raises(ValueError):resolve_godot_result(state,mission,result,session['session_id'])


@pytest.mark.parametrize('label', ['Vera', '  Vera  '])
def test_recover_retreat_with_original_or_legacy_display_name(tmp_path, label):
    from game.combat.checkpoints import load_combat_checkpoint
    agent = Character('  Vera  ', role='sniper')
    state = GameState(characters=[agent], selected_agent_names=[agent.name])
    _, mission, _, result = scenario(tmp_path)
    path = write_godot_combat_handoff(state, mission, handoff_path=tmp_path/'legacy.json')
    _, session = create_session(state, mission, path)
    sid = session['session_id']
    saved, _ = load_combat_checkpoint(state.combat_sessions[sid]['checkpoints']['before'])
    result.update(session_id=sid, outcome='retreat')
    result['agents'][0]['name'] = label
    resolve_godot_result(saved, mission, result, sid)
    assert saved.characters[0].name == 'Vera'
    assert saved.characters[0].stats.hp == 7
    assert resolve_godot_result(saved, mission, result, sid) is None
