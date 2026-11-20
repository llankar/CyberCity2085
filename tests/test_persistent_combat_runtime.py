"""Real Godot process reuse; no graphical Windows claim."""
import json
from pathlib import Path
import shutil
import time
from unittest.mock import patch
import pytest
from game.combat.persistent_runtime import CombatRuntime
from test_unified_mission_resolution import scenario
from game.combat.godot_bridge import launch_godot_combat_ui

ROOT=Path(__file__).resolve().parents[1]


def wait_for(runtime,predicate):
    limit=time.monotonic()+30
    while time.monotonic()<limit:
        runtime.tick()
        status=runtime.status()
        if predicate(status):return status
        assert runtime.process.poll() is None,(runtime.directory/'godot.log').read_text()
        time.sleep(.05)
    pytest.fail((runtime.directory/'godot.log').read_text()+'\n'+str(runtime.status()))


def test_submit_never_launches_an_engine_itself(tmp_path):
    runtime=CombatRuntime(directory=tmp_path/'runtime')
    with patch('game.combat.persistent_runtime.subprocess.Popen') as launch:
        with pytest.raises(ValueError,match='not started'):runtime.submit(tmp_path/'handoff.json','session',(1280,720))
    launch.assert_not_called()


def test_actual_runtime_is_started_before_first_mission_and_reused(tmp_path):
    from game.combat.godot_bridge import find_godot_executable
    godot=find_godot_executable()
    if not godot:pytest.skip('Godot unavailable')
    runtime=CombatRuntime(project_dir=ROOT/'godot/combat_missions_ui',directory=tmp_path/'runtime',executable=godot,headless=True)
    try:
        assert runtime.start()
        wait_for(runtime,lambda s:s.get('state')=='idle')
        pid=runtime.process.pid
        for i in range(2):
            case=tmp_path/str(i);case.mkdir()
            state,mission,_,_=scenario(case)
            with patch('game.combat.godot_bridge.subprocess.Popen',side_effect=AssertionError('Mission attempted a new process')):
                result=launch_godot_combat_ui(state,mission,handoff_path=case/'runtime-handoff.json',runtime=runtime)
            assert result.launched and result.process_pid==pid
            status_path=Path(state.combat_sessions[result.session_id]['session']['status_path'])
            wait_for(runtime,lambda s:s.get('state')=='busy' and s.get('session_id')==result.session_id and status_path.is_file())
            runtime.park(result.session_id)
            wait_for(runtime,lambda s:s.get('state')=='idle' and s.get('session_id')==result.session_id)
            assert runtime.process.poll() is None and runtime.process.pid==pid
    finally:runtime.close()
    assert runtime.process.poll()==0
    assert 'SCRIPT ERROR' not in (runtime.directory/'godot.log').read_text()


def test_parked_runtime_exits_after_heartbeat_lapses(tmp_path):
    from game.combat.godot_bridge import find_godot_executable

    godot = find_godot_executable()
    if not godot:
        pytest.skip("Godot unavailable")
    runtime = CombatRuntime(project_dir=ROOT / "godot/combat_missions_ui",
                            directory=tmp_path / "runtime", executable=godot, headless=True)
    try:
        assert runtime.start()
        wait_for(runtime, lambda status: status.get("state") == "idle")
        assert runtime.process.wait(timeout=18) == 0
    finally:
        runtime.close()


def test_persistent_runtime_resumes_a_native_snapshot_after_crash(tmp_path):
    from game.combat.checkpoints import load_combat_checkpoint
    from game.combat.godot_bridge import find_godot_executable

    godot = find_godot_executable()
    if not godot:
        pytest.skip("Godot unavailable")
    runtime = CombatRuntime(project_dir=ROOT / "godot/combat_missions_ui",
                            directory=tmp_path / "runtime", executable=godot, headless=True)
    state, mission, _, _ = scenario(tmp_path)
    try:
        assert runtime.start()
        original = launch_godot_combat_ui(state, mission, handoff_path=tmp_path / "handoff.json", runtime=runtime)
        assert original.launched
        record = state.combat_sessions[original.session_id]
        snapshot = Path(record["session"]["snapshot_path"])
        wait_for(runtime, lambda status: status.get("state") == "busy" and snapshot.is_file())
        runtime.process.kill()
        runtime.process.wait(timeout=5)
        original_snapshot = json.loads(snapshot.read_text(encoding="utf-8"))

        restored, session_id = load_combat_checkpoint(record["checkpoints"]["before"])
        assert session_id == original.session_id
        assert runtime.start()
        resumed = launch_godot_combat_ui(restored, restored.active_mission, handoff_path=tmp_path / "handoff.json",
                                         resume_session_id=session_id, runtime=runtime)
        assert resumed.launched and resumed.session_id != session_id
        assert resumed.process_pid != original.process_pid
        restored_record = restored.combat_sessions[resumed.session_id]
        restored_snapshot = Path(restored_record["session"]["snapshot_path"])
        wait_for(runtime, lambda status: status.get("state") == "busy" and restored_snapshot.is_file())
        restored_state = json.loads(restored_snapshot.read_text(encoding="utf-8"))["state"]
        for key in ("turn_side", "turn_number", "player_units", "enemy_units", "objective_progress"):
            assert restored_state[key] == original_snapshot["state"][key]
        assert restored.combat_sessions[session_id]["status"] == "superseded"
    finally:
        runtime.close()


def test_win32_overlay_stays_hidden_until_ready_then_raises_without_click():
    from types import SimpleNamespace
    from unittest.mock import Mock
    import game.ui.screens.godot_combat_handoff_view as handoff
    view=handoff.GodotCombatHandoffView.__new__(handoff.GodotCombatHandoffView)
    view.launch_result=SimpleNamespace(process_pid=42,runtime=None)
    view._arcade_hwnd=100;view._godot_hwnd=None;view._overlaid=False;view._session_ready=False
    view.window=SimpleNamespace(width=1280,height=720)
    module='game.combat.win32_embed.'
    with patch.object(handoff,'_WIN',True),patch(module+'get_process_hwnd',return_value=200) as find,patch(module+'get_window_screen_rect',side_effect=[(0,0,0,0),(10,20,1280,720),(10,20,1280,720)]),patch(module+'attach_owned_window'),patch(module+'hide_window') as hide,patch(module+'make_borderless_at',side_effect=[False,True]) as place,patch(module+'show_window') as show:
        view._try_overlay();hide.assert_called_once_with(200);place.assert_not_called()
        view._session_ready=True
        view._try_overlay()
        place.assert_not_called()
        view._try_overlay()
        place.assert_called_once_with(200,10,20,1280,720)
        show.assert_not_called()
        assert not view._overlaid
        view._try_overlay()
        assert place.call_count == 2
        find.assert_called_once_with(42, include_hidden=False)
        show.assert_called_once_with(200)
        assert view._overlaid


def test_window_sync_retries_failed_resize_and_handles_minimization():
    from unittest.mock import Mock
    from game.combat import win32_embed

    if not win32_embed._WIN:
        pytest.skip("Win32 window synchronization")
    api = Mock()
    api.IsIconic.return_value = False
    api.SetWindowPos.side_effect = [False, True, True]
    api.GetForegroundWindow.return_value = 100
    before = (0, 0, 1280, 720)
    resized = (-1600, 80, 1120, 630)
    with patch.object(win32_embed, "_WIN", True), patch.object(win32_embed, "_u32", api, create=True), \
            patch.object(win32_embed, "get_window_screen_rect", return_value=resized) as get_rect:
        assert win32_embed.sync_owned_window(200, 100, before) == before
        assert win32_embed.sync_owned_window(200, 100, before) == resized
        api.SetForegroundWindow.assert_not_called()
        get_rect.return_value = (0, 0, 0, 0)
        assert win32_embed.sync_owned_window(200, 100, resized) == resized
        api.IsIconic.return_value = True
        assert win32_embed.sync_owned_window(200, 100, resized) is None
        api.ShowWindow.assert_called_once_with(200, win32_embed._SW_HIDE)
        api.IsIconic.return_value = False
        get_rect.return_value = resized
        assert win32_embed.sync_owned_window(200, 100) == resized
        api.SetForegroundWindow.assert_called_once_with(200)
