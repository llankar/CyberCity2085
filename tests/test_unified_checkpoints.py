"""Durable recovery must replay presentation, never campaign rewards."""
import copy
import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from test_unified_mission_resolution import scenario
from game.combat.checkpoints import checkpoint_info, latest_combat_checkpoint, load_combat_checkpoint
from game.combat.godot_resolution import resolve_godot_result
from game.combat.return_snapshot import resume_return, complete_return
from game.combat.session_protocol import create_session


def test_before_checkpoint_recovers_pending_mission(tmp_path):
    state, mission, session, _ = scenario(tmp_path)
    path = Path(state.combat_sessions[session['session_id']]['checkpoints']['before'])
    restored, sid = load_combat_checkpoint(path)
    assert sid == session['session_id']
    assert restored.active_mission.id == mission.id
    assert restored.combat_sessions[sid]['status'] == 'pending'
    assert restored.available_funds == state.available_funds
    assert latest_combat_checkpoint(path.parent.parent) == path


@pytest.mark.parametrize('outcome', ['victory', 'defeat', 'retreat'])
def test_after_checkpoint_replays_debrief_without_reapplying_result(tmp_path, outcome):
    state, mission, session, result = scenario(tmp_path)
    result['outcome'] = outcome
    resolve_godot_result(state, mission, result, session['session_id'])
    path = Path(state.combat_sessions[session['session_id']]['checkpoints']['after'])
    restored, sid = load_combat_checkpoint(path)
    before = copy.deepcopy(restored.__dict__)
    assert resolve_godot_result(restored, mission, result, sid) is None
    assert restored.__dict__ == before
    context, survivors, units = resume_return(restored, mission, sid)
    assert context._victory == (outcome == 'victory')
    assert units[0].health == 7
    assert units[0].extraction_max_hp == result['agents'][0]['max_hp']
    assert units[0].external_metrics and not hasattr(units[0], '_kills')
    assert restored.available_funds == state.available_funds
    complete_return(restored, sid)
    again, _ = load_combat_checkpoint(path)
    assert resume_return(again, mission, sid) is None
    assert again.available_funds == state.available_funds


def test_disk_failure_before_commit_preserves_live_campaign(tmp_path):
    state, mission, session, result = scenario(tmp_path)
    before = copy.deepcopy(state.__dict__)
    with patch('game.combat.godot_resolution.write_campaign_checkpoint', side_effect=OSError('disk full')):
        with pytest.raises(OSError):
            resolve_godot_result(state, mission, result, session['session_id'])
    assert state.__dict__ == before
    assert not Path(state.combat_sessions[session['session_id']]['checkpoints']['after']).exists()


def test_preparation_disk_failure_restores_previous_session(tmp_path):
    state, mission, session, _ = scenario(tmp_path)
    before = copy.deepcopy(state.combat_sessions)
    with patch('game.combat.checkpoints.write_campaign_checkpoint', side_effect=OSError('disk full')):
        with pytest.raises(OSError):
            create_session(state, mission, tmp_path/'handoff.json')
    assert state.combat_sessions == before
    assert state.combat_sessions[session['session_id']]['status'] == 'pending'


def test_moved_checkpoint_rebases_communication_paths(tmp_path):
    state, mission, session, _ = scenario(tmp_path)
    original = Path(state.combat_sessions[session['session_id']]['checkpoints']['before'])
    moved = tmp_path/'moved'/'campaign_before.json'
    moved.parent.mkdir(); shutil.copyfile(original, moved)
    restored, sid = load_combat_checkpoint(moved)
    assert Path(restored.combat_sessions[sid]['session']['result_path']).parent == moved.parent
    assert Path(restored.combat_sessions[sid]['checkpoints']['after']).parent == moved.parent


def test_corrupt_latest_file_does_not_hide_previous_valid_checkpoint(tmp_path):
    state, _, session, _ = scenario(tmp_path)
    before = Path(state.combat_sessions[session['session_id']]['checkpoints']['before'])
    after = before.with_name('campaign_after.json'); after.write_text('{broken')
    assert latest_combat_checkpoint(before.parent.parent) == before
    with pytest.raises(ValueError): checkpoint_info(after)


def test_stored_result_tampering_is_not_presented_as_valid_debrief(tmp_path):
    state, mission, session, result = scenario(tmp_path)
    resolve_godot_result(state, mission, result, session['session_id'])
    state.combat_sessions[session['session_id']]['confirmed_result']['agents'][0]['hp'] = 6
    with pytest.raises(ValueError, match='digest'):
        resume_return(state, mission, session['session_id'])


def test_readiness_rejects_other_session_and_corrupt_status(tmp_path):
    from game.combat.session_protocol import atomic_json, read_session_status
    path = tmp_path/'status.json'
    valid = dict(protocol_version=2,session_id='current',mission_id='mission',ready=True,event='combat_started')
    atomic_json(path, valid)
    assert read_session_status(path, 'current', 'mission') == valid
    assert read_session_status(path, 'old', 'mission') is None
    assert read_session_status(path, 'current', 'other') is None
    valid['ready'] = 1; atomic_json(path, valid)
    assert read_session_status(path, 'current', 'mission') is None
    path.write_text('{broken')
    assert read_session_status(path, 'current', 'mission') is None


def test_native_command_can_start_borderless_at_existing_viewport(tmp_path):
    from game.combat.godot_bridge import build_godot_combat_command
    cmd = build_godot_combat_command(tmp_path/'handoff.json', executable='godot', window_rect=(-1600,80,1920,1080))
    assert cmd[cmd.index('--position')+1] == '-1600,80'
    assert cmd[cmd.index('--resolution')+1] == '1920x1080'
    assert '--borderless' in cmd
    assert cmd.index('--resolution') < cmd.index('--')
    with pytest.raises(ValueError):
        build_godot_combat_command(tmp_path/'handoff.json', executable='godot', window_rect=(0,0,0,720))


def test_corrupt_result_is_reported_without_campaign_mutation(tmp_path):
    from game.combat.godot_bridge import GodotCombatLaunchResult
    from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView
    state, mission, session, _ = scenario(tmp_path)
    path = Path(session['result_path']); path.write_text('{broken')
    launch = GodotCombatLaunchResult(path.parent/'handoff.json', [], True, '', session_id=session['session_id'],result_path=path)
    view = GodotCombatHandoffView(state, mission, launch, window=Mock())
    before = state.available_funds
    view.on_update(.1)
    assert view._launch_failed and 'Combat report unreadable' in view._status
    assert state.available_funds == before
    assert state.combat_sessions[session['session_id']]['status'] == 'pending'


def test_result_read_retries_transient_windows_lock(tmp_path):
    from game.combat.godot_bridge import GodotCombatLaunchResult
    from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView

    state, mission, session, result = scenario(tmp_path)
    path = Path(session["result_path"])
    path.write_text(json.dumps(result), encoding="utf-8")
    launch = GodotCombatLaunchResult(path.parent / "handoff.json", [], True, "",
                                    session_id=session["session_id"], result_path=path)
    view = GodotCombatHandoffView(state, mission, launch, window=Mock())
    with patch.object(Path, "read_text", side_effect=PermissionError("sharing violation")), \
            patch.object(view, "_apply_combat_result") as apply:
        view.on_update(.1)
        assert not view._launch_failed
        apply.assert_not_called()
    with patch.object(view, "_apply_combat_result") as apply:
        view.on_update(.1)
        apply.assert_called_once_with(result)


@pytest.mark.parametrize("phase", ["prepared", "confirmed"])
def test_interrupted_combat_opens_debrief_automatically(tmp_path, phase):
    from unittest.mock import Mock, patch
    from game.combat.godot_bridge import GodotCombatLaunchResult
    from game.combat.session_protocol import atomic_json
    from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView

    state, mission, session, result = scenario(tmp_path)
    result.update(outcome="retreat", phase=phase)
    path = Path(session["prepared_path" if phase == "prepared" else "result_path"])
    atomic_json(path, result)
    launch = GodotCombatLaunchResult(path.parent/"handoff.json", [], False, "",
        session_id=session["session_id"], result_path=Path(session["result_path"]))
    view = GodotCombatHandoffView(state, mission, launch, window=Mock())
    with patch("game.ui.screens.mission_return.show_mission_debrief") as show:
        view.on_update(.1)
        assert state.combat_sessions[session["session_id"]]["status"] == "applied"
        view.on_update(.1)
        view.on_update(.1)
        show.assert_called_once()
    assert state.latest_mission_debrief["mission_outcome"] == "retreat"
