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


def test_win32_overlay_stays_hidden_until_ready_then_raises_without_click():
    from types import SimpleNamespace
    from unittest.mock import Mock
    import game.ui.screens.godot_combat_handoff_view as handoff
    view=handoff.GodotCombatHandoffView.__new__(handoff.GodotCombatHandoffView)
    view.launch_result=SimpleNamespace(process_pid=42,runtime=None)
    view._arcade_hwnd=100;view._godot_hwnd=None;view._overlaid=False;view._session_ready=False
    view.window=SimpleNamespace(width=1280,height=720)
    module='game.combat.win32_embed.'
    with patch.object(handoff,'_WIN',True),patch(module+'get_process_hwnd',return_value=200),patch(module+'get_window_screen_rect',return_value=(10,20,1280,720)),patch(module+'attach_owned_window'),patch(module+'hide_window') as hide,patch(module+'make_borderless_at') as place,patch(module+'show_window') as show:
        view._try_overlay();hide.assert_called_once_with(200);place.assert_not_called()
        view._session_ready=True;view._try_overlay()
        place.assert_called_once_with(200,10,20,1280,720);show.assert_called_once_with(200)
        assert view._overlaid
