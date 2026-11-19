"""Real application-like bootstrap and two naturally concluded campaign missions, one PID."""
import argparse,json,os,subprocess,tempfile,time
from pathlib import Path
from unittest.mock import patch


def main():
    import arcade
    from game.combat.persistent_runtime import CombatRuntime
    from game.ui.application_window import GameWindow
    from game.ui.screens.title_screen import TitleView
    from game.ui.screens.management_screen import ManagementView
    from game.ui.screens.battle_debrief_view import BattleDebriefView
    from game.ui.screens.agent_promotion_view import AgentPromotionView
    from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView
    from tools.check_unified_return import campaign_scenario
    from game.mission_system import ensure_mission_templates
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('work/persistent-runtime'))
    args=parser.parse_args();output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[1];previous=Path.cwd();original_popen=subprocess.Popen
    calls=[];cases=[]
    window=GameWindow(1280,720,'CyberCity persistent runtime validation',visible=True)
    def frame(path=None):
        window.dispatch_events();window.switch_to();window.combat_runtime.tick()
        view=window.current_view;view.on_update(.016);view.on_draw()
        if path:arcade.get_image().save(path)
        window.flip()
    try:
        with tempfile.TemporaryDirectory(prefix='cybercity-persistent-') as temp:
            sandbox=Path(temp)
            for name in ['assets','godot']:(sandbox/name).symlink_to(root/name,target_is_directory=True)
            os.chdir(sandbox)
            def launch(command,*a,**kw):
                if not isinstance(command,(list,tuple)) or 'godot' not in Path(command[0]).name.lower():
                    return original_popen(command,*a,**kw)
                calls.append(list(command));command=list(command)
                command[1:1]=['--audio-driver','Dummy','--script','res://tests/persistent_runtime_playthrough.gd']
                command+=['--qa-output',str(output)]
                return original_popen(command,*a,**kw)
            with patch('game.combat.persistent_runtime.subprocess.Popen',side_effect=launch):
                started=time.monotonic();assert window.start_combat_runtime()
                window.show_view(TitleView())
                limit=time.monotonic()+60
                while window.combat_runtime.status().get('state')!='idle':
                    frame();assert time.monotonic()<limit,(window.combat_runtime.directory/'godot.log').read_text()
                frame(output/'00-title-runtime-already-ready.png')
                boot_seconds=time.monotonic()-started;pid=window.combat_runtime.process.pid
                assert len(calls)==1
                state,_=campaign_scenario()
                for index in range(2):
                    ensure_mission_templates(state)
                    state.selected_mission_index=min(range(len(state.mission_templates)),key=lambda i:(state.mission_templates[i].risk_level,state.mission_templates[i].objective_type not in {'data_theft','data_with_detour'}))
                    mission=state.mission_templates[state.selected_mission_index]
                    case=output/str(index+1);case.mkdir(exist_ok=True)
                    hq=ManagementView(state);hq.setup();window.show_view(hq);frame(case/'hq-before.png')
                    hq._open_mission_map();frame(case/'world.png');window.current_view._launch_selected_mission();frame(case/'briefing.png')
                    mission_started=time.monotonic();window.current_view.on_key_press(arcade.key.ENTER,0)
                    bridge=window.current_view;assert isinstance(bridge,GodotCombatHandoffView)
                    assert bridge.launch_result.process_pid==pid and len(calls)==1
                    session_id=bridge.launch_result.session_id;game=output/session_id
                    mission_ready_seconds=None
                    limit=time.monotonic()+180
                    while not (game/'playthrough.json').is_file():
                        frame();assert not bridge._launch_failed,bridge._status
                        if getattr(bridge,"_session_ready",False) and mission_ready_seconds is None:mission_ready_seconds=time.monotonic()-mission_started
                        assert time.monotonic()<limit,(window.combat_runtime.directory/'godot.log').read_text()
                        time.sleep(.02)
                    play=json.loads((game/'playthrough.json').read_text());assert not play['outcome_forced']
                    before=state.available_funds
                    for _ in range(10):frame();time.sleep(.04)
                    assert window.current_view is bridge and state.available_funds==before
                    (game/'confirm.request').write_text('PLAYER CONFIRMS RETURN\n')
                    limit=time.monotonic()+30
                    while isinstance(window.current_view,GodotCombatHandoffView):
                        frame();assert time.monotonic()<limit,bridge._status
                    assert isinstance(window.current_view,BattleDebriefView)
                    frame(case/'debrief.png')
                    assert window.combat_runtime.is_idle(session_id) and window.combat_runtime.process.poll() is None
                    window.current_view._go_to_management()
                    promoted=False
                    while isinstance(window.current_view,AgentPromotionView):
                        promoted=True;frame(case/'promotion.png');window.current_view._advance()
                    assert isinstance(window.current_view,ManagementView)
                    frame(case/'hq-after.png')
                    from game.combat.godot_resolution import resolve_godot_result
                    result=state.combat_sessions[session_id]['confirmed_result']
                    funds=state.available_funds
                    assert resolve_godot_result(state,mission,result,session_id) is None and state.available_funds==funds
                    cases.append(dict(pid=pid,session_id=session_id,mission_id=mission.id,outcome=play['outcome'],
                        outcome_forced=False,engine_stayed_alive=True,promotions=promoted,mission_ready_seconds=mission_ready_seconds,elapsed_seconds=time.monotonic()-mission_started))
                window.close()
                assert window.combat_runtime.process.poll()==0 and len(calls)==1
                log=(window.combat_runtime.directory/'godot.log').read_text()
                (output/'godot.log').write_text(log)
                assert 'SCRIPT ERROR' not in log,log
                report=dict(status='PASS',boot_before_first_mission=True,boot_seconds=boot_seconds,
                    process_launches=len(calls),same_pid_all_missions=True,cases=cases,windows_graphics_verified=False,audible_audio_verified=False)
                (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
    finally:
        if hasattr(window,'combat_runtime'):window.combat_runtime.close()
        window.close();os.chdir(previous)

if __name__=='__main__':main()
