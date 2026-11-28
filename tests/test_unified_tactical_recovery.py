"""Runtime recovery validation and real Godot roundtrip, without campaign mutation."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
from unittest.mock import Mock, patch
import pytest
from test_unified_mission_resolution import scenario
from game.combat.session_protocol import atomic_json, create_session
from game.combat.tactical_recovery import validate_tactical_snapshot, prepare_resume_payload
from game.combat.godot_bridge import launch_godot_combat_ui

ROOT = Path(__file__).resolve().parents[1]


def snapshot_for(record):
    session = record['session']
    units = [dict(name=row['name'],max_hp=row['max_hp'],hp=row['max_hp']-1,ap=2,
                  position=[3,4],role=row['role'],kind='player',status_effects=[]) for row in record['expected_agents']]
    return dict(protocol_version=2,snapshot_version=1,session_id=session['session_id'],
        mission_id=session['mission_id'],handoff_fingerprint=session['handoff_fingerprint'],
        camera=dict(position=[0.,50.],zoom=.7,visual_mode=True,top_down=True),state=dict(initial_enemy_count=0,
        turn_side='player',turn_number=3,enemy_turn_timer=0.,active_player_index=0,
        _queued_player_index=-1,selected_target_index=0,selected_action='MOVE',
        pending_end_turn_confirmation=False,show_combat_log=False,objective_progress=1,objective_completed=False,
        overwatch_indices=[0],defend_indices=[],combat_log=['Actual snapshot'],
        player_units=units,enemy_units=[],vehicle_units=[],objective=dict(cell=[5,6])))


def test_resume_preparation_is_read_only_and_new_session_preserves_runtime_state(tmp_path):
    gs, mission, session, result = scenario(tmp_path)
    record = gs.combat_sessions[session['session_id']]
    snapshot = snapshot_for(record)
    atomic_json(session['snapshot_path'],snapshot)
    before = copy.deepcopy(gs.__dict__)
    funds = gs.available_funds
    payload = prepare_resume_payload(gs,mission,session['session_id'])
    assert gs.__dict__ == before
    atomic_json(tmp_path/'resume.json', payload)
    path,new_session = create_session(gs,mission,tmp_path/'resume.json')
    resumed = json.loads(path.read_text())
    assert new_session['session_id'] != session['session_id']
    assert resumed['resume_snapshot']['state'] == snapshot['state']
    assert resumed['resume_snapshot']['session_id'] == new_session['session_id']
    assert resumed['resume_snapshot']['source_session_id'] == session['session_id']
    assert Path(new_session['snapshot_path']).is_file()
    assert prepare_resume_payload(gs,mission,new_session['session_id'])['resume_snapshot']['state']==snapshot['state']  # Recoverable even before the replacement renders a frame.
    assert gs.available_funds == funds
    from game.combat.godot_resolution import resolve_godot_result
    with pytest.raises(ValueError):resolve_godot_result(gs,mission,result,session['session_id'])


@pytest.mark.parametrize('mutate',[
 lambda s:s.update(protocol_version=1),lambda s:s.update(snapshot_version=2),
 lambda s:s.update(session_id='other'),lambda s:s.update(mission_id='other'),
 lambda s:s.update(handoff_fingerprint='changed'),lambda s:s['state'].update(turn_number=0),
 lambda s:s['state'].update(turn_side='other'),lambda s:s['state'].update(overwatch_indices=[99]),
 lambda s:s['state']['player_units'][0].update(position=[-1,5]),
 lambda s:s['state']['player_units'][0].update(position=[40,5]),
 lambda s:s['state']['player_units'][0].update(hp=10000),
 lambda s:s['state']['player_units'][0].update(ap=-1),
 lambda s:s['state']['player_units'][0].update(name='not deployed'),
 lambda s:s['state']['player_units'][0].update(max_hp=1),
 lambda s:s['state'].update(player_units=[]),lambda s:s['state'].update(objective_progress=-1),
 lambda s:s['state'].update(objective_completed='true'),
 lambda s:s['state'].update(pending_retreat_confirmation='false'),
 lambda s:s['state'].update(heavy_strike_used=1),
 lambda s:s['state'].update(pending_retreat_confirmation=True,pending_end_turn_confirmation=True),
 lambda s:s['camera'].update(zoom=float('nan')),lambda s:s['camera'].update(zoom=8),
])
def test_invalid_snapshot_never_mutates_campaign(tmp_path,mutate):
    gs, _, session, _ = scenario(tmp_path); before=copy.deepcopy(gs.__dict__)
    snapshot=snapshot_for(gs.combat_sessions[session['session_id']]);mutate(snapshot)
    with pytest.raises(ValueError):validate_tactical_snapshot(snapshot,gs.combat_sessions[session['session_id']])
    assert gs.__dict__==before


def test_existing_result_cannot_be_bypassed_by_resume(tmp_path):
    gs,mission,session,result=scenario(tmp_path)
    atomic_json(session['snapshot_path'],snapshot_for(gs.combat_sessions[session['session_id']]))
    atomic_json(session['prepared_path'],{**result,'phase':'prepared'})
    with pytest.raises(ValueError,match='result is available'):prepare_resume_payload(gs,mission,session['session_id'])


def test_failed_replacement_keeps_source_recoverable(tmp_path):
    gs,mission,session,_=scenario(tmp_path)
    atomic_json(session['snapshot_path'],snapshot_for(gs.combat_sessions[session['session_id']]))
    with patch('game.combat.godot_bridge.subprocess.Popen',side_effect=OSError('cannot launch')):
        launched=launch_godot_combat_ui(gs,mission,handoff_path=tmp_path/'new.json',executable='godot',resume_session_id=session['session_id'])
    assert not launched.launched
    assert gs.combat_sessions[session['session_id']]['status']=='pending'
    assert gs.combat_sessions[launched.session_id]['status']=='abandoned'
    assert not Path(session['control_path']).exists()


@pytest.mark.parametrize('side',['player','enemy'])
@pytest.mark.parametrize('support',[False,True],ids=['agent','agent-robot-armor'])
def test_actual_godot_tactical_checkpoint_roundtrip(tmp_path,side,support):
    _actual_roundtrip(tmp_path,side,support)


def _actual_roundtrip(tmp_path,side,support,isometric=False,classic=False,resize=False):
    godot=shutil.which('godot')
    if not godot:pytest.skip('Godot unavailable')
    state,mission,session,_=scenario(tmp_path, armed=True)
    if support:
        from game.management.spec_ops_assets import CombatRobot,PowerArmorSuit
        from game.combat.godot_bridge import write_godot_combat_handoff
        state.spec_ops_assets=[CombatRobot(id='robot',name='Drone'),PowerArmorSuit(id='suit',name='Mantis')]
        state.selected_asset_ids=['robot','suit']
        state.vehicle_upgrade_ids.append("heavy_strike")
        path=write_godot_combat_handoff(state,mission,handoff_path=tmp_path/'support.json')
        _,session=create_session(state,mission,path)
        assert len(state.combat_sessions[session['session_id']]['expected_support'])==2
    path=Path(session['snapshot_path']).with_name('handoff.json')
    result=subprocess.run([godot,'--headless','--quit-after','120','--audio-driver','Dummy','--path',str(ROOT/'godot/combat_missions_ui'),
        '--script','tests/tactical_checkpoint_roundtrip.gd','--','--handoff',str(path),'--phase',side]+(['--qa-isometric'] if isometric else [])+(['--qa-classic'] if classic else [])+(['--qa-resize'] if resize else []),capture_output=True,text=True,timeout=45)
    output=result.stdout+result.stderr
    assert result.returncode==0 and 'SCRIPT ERROR' not in output,output
    assert 'TACTICAL_CHECKPOINT_ROUNDTRIP_PASS '+side in output,output
    snapshot=json.loads(Path(session['snapshot_path']).read_text())
    assert snapshot['state']['turn_side']=='player'  # Enemy case also exercises one real AI turn.
    assert snapshot['state']['turn_number']==(4 if side=='enemy' else 3)


def test_godot_refuses_corrupt_resume_without_silent_fresh_battle(tmp_path):
    godot=shutil.which('godot')
    if not godot:pytest.skip('Godot unavailable')
    _,_,session,_=scenario(tmp_path, armed=True)
    path=Path(session['snapshot_path']).with_name('handoff.json')
    result=subprocess.run([godot,'--headless','--quit-after','120','--audio-driver','Dummy',
        '--path',str(ROOT/'godot/combat_missions_ui'),'--script','tests/tactical_checkpoint_roundtrip.gd',
        '--','--handoff',str(path),'--reject-resume'],capture_output=True,text=True,timeout=45)
    output=result.stdout+result.stderr
    assert result.returncode==0 and 'SCRIPT ERROR' not in output,output
    assert 'TACTICAL_CHECKPOINT_REJECT_PASS' in output,output


def test_actual_godot_checkpoint_preserves_isometric_projection(tmp_path):
    _actual_roundtrip(tmp_path,'player',False,isometric=True)


def test_actual_godot_checkpoint_preserves_legacy_visuals(tmp_path):
    _actual_roundtrip(tmp_path,'player',False,classic=True)


def test_explicit_fresh_restart_also_releases_old_instance(tmp_path):
    state,mission,session,_=scenario(tmp_path)
    with patch('game.combat.godot_bridge.subprocess.Popen',return_value=Mock(pid=123456)):
        result=launch_godot_combat_ui(state,mission,handoff_path=tmp_path/'restart.json',executable='godot')
    assert result.launched and state.combat_sessions[session['session_id']]['status']=='superseded'
    assert json.loads(Path(session['control_path']).read_text())==dict(protocol_version=2,session_id=session['session_id'],event='superseded')


def test_abandon_after_host_restart_requests_old_godot_to_close(tmp_path):
    from types import SimpleNamespace
    from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView
    state,_,session,_=scenario(tmp_path)
    view=GodotCombatHandoffView.__new__(GodotCombatHandoffView)
    view.game_state=state;view.launch_result=SimpleNamespace(session_id=session['session_id'])
    view._abandon_session()
    assert state.combat_sessions[session['session_id']]['status']=='abandoned'
    assert json.loads(Path(session['control_path']).read_text())['event']=='superseded'


def test_host_exposes_rejected_snapshot_without_campaign_mutation(tmp_path):
    from game.combat.godot_bridge import GodotCombatLaunchResult
    from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView
    state,mission,session,_=scenario(tmp_path)
    atomic_json(session['status_path'],dict(protocol_version=2,session_id=session['session_id'],
        mission_id=mission.id,event='error',ready=False,message='Invalid tactical unit'))
    view=GodotCombatHandoffView(state,mission,GodotCombatLaunchResult(tmp_path/'handoff.json',[],True,'',
        session_id=session['session_id'],result_path=Path(session['result_path'])),window=Mock())
    view._cleanup_godot=Mock();before=copy.deepcopy(state.__dict__)
    view.on_update(.1)
    assert view._launch_failed and 'Combat recovery was rejected' in view._status
    assert 'Invalid tactical unit' not in view._status
    assert state.__dict__==before


def test_restarted_host_acknowledges_applied_result_without_awarding_again(tmp_path):
    from game.combat.godot_resolution import resolve_godot_result
    from game.combat.session_protocol import acknowledge_applied_session
    state,mission,session,result=scenario(tmp_path)
    resolve_godot_result(state,mission,result,session['session_id'])
    before=copy.deepcopy(state.__dict__)
    acknowledge_applied_session(state.combat_sessions[session['session_id']],session['session_id'])
    assert state.__dict__==before
    assert json.loads(Path(session['ack_path']).read_text())['status']=='accepted'
    state.combat_sessions[session['session_id']]['confirmed_result']['agents'][0]['hp']=1
    with pytest.raises(ValueError,match='digest'):
        acknowledge_applied_session(state.combat_sessions[session['session_id']],session['session_id'])


def test_actual_godot_checkpoint_reframes_and_preserves_clicks_at_new_resolution(tmp_path):
    _actual_roundtrip(tmp_path,'player',False,resize=True)
