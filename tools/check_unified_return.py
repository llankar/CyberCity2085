"""Native Linux integration evidence; forced outcomes test plumbing, not Windows embedding."""
from __future__ import annotations
import argparse,json,os,subprocess,sys,tempfile,time
from pathlib import Path
from unittest.mock import patch


def _link_directory(link: Path, target: Path) -> None:
    """Create an isolated directory link without requiring Windows dev mode."""
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        if os.name != "nt":
            raise
        completed = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode:
            raise OSError(completed.stderr or completed.stdout)


def campaign_scenario(mission_id=None):
    """Use the real daily board and normal equipped recruits, with no stat overrides."""
    from game.gamestate import GameState
    from game.recruitment import recruit_agent
    from game.management.equipment import equip_starter_loadout
    from game.mission_system import ensure_mission_templates
    roster=[]
    for role in ['samurai','sniper','psi','samurai','sniper']:
        recruit_agent(roster,role)
    state=GameState(characters=roster,selected_agent_names=[c.name for c in roster])
    state.grant_initial_armory()
    for agent in state.characters:
        equip_starter_loadout(agent.loadout, agent.role)
    ensure_mission_templates(state)
    eligible=[(i,m) for i,m in enumerate(state.mission_templates) if mission_id is None or m.id==mission_id]
    if not eligible:raise ValueError('Requested mission is absent from the actual daily board')
    index,mission=min(eligible,key=lambda pair:(pair[1].risk_level,pair[1].objective_type not in {'data_theft','data_with_detour'},pair[1].id))
    state.selected_mission_index=index
    return state,mission


def main(argv=None):
    import arcade
    from game.character import Character
    from game.gamestate import GameState
    from game.mission_templates import MissionTemplate
    from game.ui.music_window import MusicTransitionMixin
    from game.ui.screens.management_screen import ManagementView
    from game.ui.screens.world_map_view import MissionWorldMapView
    from game.ui.screens.mission_briefing_view import MissionBriefingView
    from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView
    from game.ui.screens.battle_debrief_view import BattleDebriefView
    from game.ui.screens.agent_promotion_view import AgentPromotionView
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('work/unified-experience'))
    parser.add_argument("--outcomes", nargs="+", choices=["victory","defeat","retreat"], default=["victory","defeat","retreat"])
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--interrupt-after-resolution", action="store_true")
    parser.add_argument("--interrupt-phase", choices=["player","enemy"])
    parser.add_argument("--keep-source-alive", action="store_true")
    parser.add_argument("--crash-recovery", action="store_true")
    parser.add_argument("--resume-debrief", action="store_true")
    parser.add_argument("--real-mission", action="store_true", help="Play the authored objective to victory instead of forcing an outcome")
    parser.add_argument("--window-hold-seconds", type=float, default=0.0, help="Keep the native combat window idle for manual lifecycle QA")
    parser.add_argument("--resize-check", action="store_true", help="Resize the tactical window from inside Godot")
    parser.add_argument("--overlay-check", action="store_true", help="Check the Win32 client rectangles after handoff")
    parser.add_argument("--godot-verbose", action="store_true", help="Log Godot lifetime diagnostics")
    parser.add_argument("--native-audio", action="store_true", help="Use the host audio driver instead of Dummy")
    args=parser.parse_args(argv);output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    if args.resize_check and not args.real_mission:
        parser.error("--resize-check requires --real-mission")
    if args.overlay_check and sys.platform != "win32":
        parser.error("--overlay-check requires Windows")
    if args.overlay_check and (args.width <= 160 or args.height <= 90):
        parser.error("--overlay-check requires width > 160 and height > 90")
    if args.real_mission and args.interrupt_phase and args.outcomes != ["victory"]:
        parser.error("real mission interruption requires --outcomes victory")
    if args.real_mission and any(outcome not in {"victory", "defeat", "retreat"} for outcome in args.outcomes):
        parser.error("--real-mission supports victory, defeat, and retreat")
    root=Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
    previous=Path.cwd();real_popen=subprocess.Popen
    class Window(MusicTransitionMixin,arcade.Window):pass
    window=Window(args.width,args.height,'CyberCity unified experience — Linux validation',visible=True)
    results=[]
    def frame(path=None):
        window.dispatch_events();window.switch_to()
        view=window.current_view
        if hasattr(view,'on_update'):view.on_update(.016)
        view.on_draw()
        if path:arcade.get_image().save(path)
        window.flip()
    try:
        for outcome in args.outcomes:
            case=output/outcome;case.mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='cybercity-unified-') as tmp:
                sandbox=Path(tmp);_link_directory(sandbox/'assets',root/'assets');_link_directory(sandbox/'godot',root/'godot');os.chdir(sandbox)
                mission=MissionTemplate(id='unified_'+outcome,title='Unified '+outcome,objective_text='Protocol validation',target_faction='Corp 37',district='Chrome',district_pressure={},starting_enemy_count=3,risk_level=2,objective_type='hack')
                names = ['Vera', 'Rook', 'Oracle', 'Mantis'] if args.real_mission else ['Vera']
                state=GameState(characters=[Character(name) for name in names],selected_agent_names=names,mission_templates=[mission])
                state.mission_board_generated_day=state.calendar.current_day;state.mission_board_version=2
                hq=ManagementView(state);hq.setup();window.show_view(hq);frame(case/'01-headquarters.png')
                hq._open_mission_map();assert isinstance(window.current_view,MissionWorldMapView);frame(case/'02-world-map.png')
                window.current_view._launch_selected_mission();assert isinstance(window.current_view,MissionBriefingView);frame(case/'03-briefing.png')
                confirm=case/'confirm.request';confirm.unlink(missing_ok=True)
                log=case/'godot.log'
                with log.open('w') as stream:
                    def launch(command,*a,**kw):
                        command=list(command)
                        driver='res://tests/unified_real_mission_flow.gd' if args.real_mission else 'res://tests/unified_return_flow.gd'
                        # The production command may already carry Arcade's window size.
                        # Override that option in place so Godot receives exactly one size.
                        if '--resolution' in command:
                            index = command.index('--resolution')
                            command[index + 1] = f'{args.width}x{args.height}'
                        else:
                            command[1:1] = ['--resolution', f'{args.width}x{args.height}']
                        command[1:1] = ['--script', driver]
                        if not args.native_audio:
                            command[1:1] = ['--audio-driver', 'Dummy']
                        command+=['--qa-confirm',str(confirm),'--qa-captures',str(case)]
                        if not args.real_mission: command += ['--qa-outcome',outcome]
                        else: command += ['--qa-real-outcome',outcome]
                        if args.window_hold_seconds > 0: command += ['--qa-window-hold-seconds',str(args.window_hold_seconds)]
                        if args.resize_check: command += ['--qa-resize-check']
                        if args.godot_verbose: command.insert(1, '--verbose')
                        if args.interrupt_phase: command += ['--qa-interrupt-phase',args.interrupt_phase]
                        return real_popen(command,*a,stdout=stream,stderr=subprocess.STDOUT,**kw)
                    launch_started=time.monotonic()
                    with patch('game.combat.godot_bridge.subprocess.Popen',side_effect=launch):
                        window.current_view.on_key_press(arcade.key.ENTER,0)
                    bridge=window.current_view;assert isinstance(bridge,GodotCombatHandoffView) and bridge.launch_result.launched
                    process=bridge.launch_result.process
                    try:
                        if args.interrupt_phase:
                            deadline=time.monotonic()+50
                            while 'UNIFIED_TACTICAL_SNAPSHOT_WAITING' not in log.read_text():
                                frame(); assert process.poll() is None,log.read_text()
                                assert time.monotonic()<deadline,log.read_text()
                                time.sleep(.03)
                            source_process=process;source_session=bridge.launch_result.session_id
                            from game.combat.checkpoints import load_combat_checkpoint
                            checkpoint=state.combat_sessions[source_session]['checkpoints']['before']
                            state,_=load_combat_checkpoint(checkpoint)
                            if not args.keep_source_alive: source_process.kill();source_process.wait(timeout=5)
                            # Emulate a new Python host: it has no child handle to clean up.
                            from dataclasses import replace
                            bridge.launch_result=replace(bridge.launch_result,process=None,process_pid=None)
                            from game.ui.screens.combat_recovery import show_combat_recovery
                            assert show_combat_recovery(window,state)
                            bridge=window.current_view
                            frame(case/'04-resume-offered.png')
                            with patch('game.combat.godot_bridge.subprocess.Popen',side_effect=launch):
                                bridge.on_key_press(arcade.key.S,0)
                            assert bridge.launch_result.launched,bridge._status
                            assert bridge.launch_result.session_id!=source_session
                            process=bridge.launch_result.process
                            deadline=time.monotonic()+10
                            while source_process.poll() is None:
                                frame();assert time.monotonic()<deadline,'old Godot did not accept supersession'
                                time.sleep(.03)
                            if args.keep_source_alive: assert source_process.returncode==0
                        deadline=launch_started+50+args.window_hold_seconds;first_frame_at=None;ready_at=None
                        ready_marker='UNIFIED_REAL_MISSION_READY' if args.real_mission else 'TACTICAL COMBAT UI READY'
                        while 'UNIFIED_NATIVE_RESULTS_WAITING' not in log.read_text():
                            frame();assert not bridge._launch_failed,bridge._status
                            assert process.poll() is None,log.read_text()
                            log_text=log.read_text()
                            if first_frame_at is None and 'UNIFIED_FIRST_FRAME' in log_text:first_frame_at=time.monotonic()
                            if ready_at is None and ready_marker in log_text:ready_at=time.monotonic()
                            assert time.monotonic()<deadline,log.read_text()
                            time.sleep(.03)
                        result_ready_at=time.monotonic()
                        log_text=log.read_text()
                        if first_frame_at is None and 'UNIFIED_FIRST_FRAME' in log_text:first_frame_at=result_ready_at
                        if ready_at is None and ready_marker in log_text:ready_at=result_ready_at
                        from PIL import Image
                        result_capture = case / ('godot-real-results.png' if args.real_mission else 'godot-results.png')
                        actual_viewport = Image.open(result_capture).size
                        assert actual_viewport[0] > 0 and actual_viewport[1] > 0
                        assert actual_viewport == (args.width, args.height), actual_viewport
                        if args.resize_check:
                            assert "UNIFIED_INTERNAL_RESIZE_PASSED" in log.read_text()
                        from game.combat.session_protocol import read_session_status
                        session=state.combat_sessions[bridge.launch_result.session_id]['session']
                        assert read_session_status(session['status_path'],session['session_id'],mission.id)['ready']
                        assert 'UNIFIED_AUDIO_OWNERSHIP_READY' in log.read_text()
                        first_frame_seconds=(first_frame_at-launch_started) if first_frame_at is not None else None
                        readiness_seconds=(ready_at-launch_started) if ready_at is not None else None
                        mission_play_seconds=(result_ready_at-ready_at) if ready_at is not None else None
                        if args.real_mission: assert 'UNIFIED_REAL_MISSION_COMPLETED' in log.read_text()
                        if args.interrupt_phase: assert 'UNIFIED_TACTICAL_STATE_RESUMED' in log.read_text()
                        before=state.available_funds
                        for _ in range(12):frame();time.sleep(.08)
                        assert window.current_view is bridge and process.poll() is None
                        if args.overlay_check:
                            import ctypes
                            from ctypes import wintypes
                            from game.combat.win32_embed import get_window_screen_rect
                            assert bridge._overlaid and bridge._arcade_hwnd and bridge._godot_hwnd
                            owner_rect = get_window_screen_rect(bridge._arcade_hwnd)
                            tactical_rect = get_window_screen_rect(bridge._godot_hwnd)
                            assert owner_rect == tactical_rect and min(owner_rect[2:]) > 0, (owner_rect, tactical_rect)
                            print(f"WIN32_OVERLAY_CLIENTS_MATCH {tactical_rect}", flush=True)
                            get_dpi = ctypes.windll.user32.GetDpiForWindow
                            get_dpi.argtypes = [wintypes.HWND]
                            get_dpi.restype = wintypes.UINT
                            dpi = (get_dpi(bridge._arcade_hwnd), get_dpi(bridge._godot_hwnd))
                            assert min(dpi) > 0
                            print(f"WIN32_OVERLAY_DPI arcade={dpi[0]} godot={dpi[1]}", flush=True)
                            for width, height in ((args.width - 160, args.height - 90), (args.width, args.height)):
                                window.set_size(width, height)
                                deadline = time.monotonic() + 5
                                while True:
                                    frame()
                                    owner_rect = get_window_screen_rect(bridge._arcade_hwnd)
                                    tactical_rect = get_window_screen_rect(bridge._godot_hwnd)
                                    if owner_rect == tactical_rect and owner_rect[2:] == (width, height):
                                        break
                                    assert time.monotonic() < deadline, (owner_rect, tactical_rect, width, height)
                                    time.sleep(.03)
                                print(f"WIN32_OVERLAY_FOLLOWS_ARCADE {tactical_rect}", flush=True)
                        assert state.available_funds==before and not Path(bridge.launch_result.result_path).exists()
                        if args.interrupt_after_resolution: bridge._write_pending_ack=lambda:None
                        if args.crash_recovery:
                            process.kill(); process.wait(timeout=5)
                            frame()
                            assert bridge._launch_failed
                            frame(case/'04-crash-recovery.png')
                        else:
                            confirm.write_text('USER CONFIRMATION IN QA\n')
                        deadline=time.monotonic()+30
                        while isinstance(window.current_view,GodotCombatHandoffView):
                            frame();assert not bridge._launch_failed,bridge._status
                            if args.interrupt_after_resolution and bridge._result_applied:
                                from game.combat.checkpoints import load_combat_checkpoint
                                from game.ui.screens.combat_recovery import show_combat_recovery
                                from dataclasses import replace
                                checkpoint=state.combat_sessions[bridge.launch_result.session_id]['checkpoints']['after']
                                assert process.poll() is None and not Path(state.combat_sessions[bridge.launch_result.session_id]['session']['ack_path']).exists()
                                bridge.launch_result=replace(bridge.launch_result,process=None,process_pid=None)
                                bridge._pending_return=None
                                state,_=load_combat_checkpoint(checkpoint)
                                assert show_combat_recovery(window,state)
                                assert state.combat_sessions[bridge.launch_result.session_id]['status']=='applied'

                            assert time.monotonic()<deadline,log.read_text()
                            time.sleep(.02)
                        assert isinstance(window.current_view,BattleDebriefView)
                        frame(case/'05-debrief.png')
                        if not args.crash_recovery: assert process.wait(timeout=5)==0
                        if args.resume_debrief:
                            from game.combat.checkpoints import load_combat_checkpoint
                            from game.ui.screens.combat_recovery import show_combat_recovery
                            checkpoint=state.combat_sessions[bridge.launch_result.session_id]['checkpoints']['after']
                            state, sid=load_combat_checkpoint(checkpoint)
                            assert show_combat_recovery(window,state)
                            assert isinstance(window.current_view,BattleDebriefView)
                            frame(case/'05-recovered-debrief.png')
                        actual=state.combat_sessions[bridge.launch_result.session_id]['confirmed_result']
                        (case/'confirmed-result.json').write_text(json.dumps(actual,indent=2)+'\n')
                        after=state.available_funds;bridge.on_update(.1);assert state.available_funds==after
                        window.current_view._go_to_management()
                        promoted=isinstance(window.current_view,AgentPromotionView)
                        if promoted:
                            frame(case/'06-promotions.png')
                            while isinstance(window.current_view,AgentPromotionView):window.current_view._advance()
                        assert isinstance(window.current_view,ManagementView)
                        frame(case/'07-headquarters-return.png')
                        assert promoted==(outcome=='victory')
                        save=case/'campaign.json';state.save(str(save));loaded=GameState.load(str(save))
                        from game.combat.godot_resolution import resolve_godot_result
                        assert resolve_godot_result(loaded,mission,actual,bridge.launch_result.session_id) is None
                        assert loaded.available_funds==after
                        assert state.latest_mission_debrief and state.latest_agent_aftermath is not None
                        results.append(dict(outcome=outcome,native_godot=True,real_mission=args.real_mission,first_frame_seconds=round(first_frame_seconds,3) if first_frame_seconds is not None else None,readiness_seconds=round(readiness_seconds,3) if readiness_seconds is not None else None,mission_play_seconds=round(mission_play_seconds,3) if mission_play_seconds is not None else None,results_waited_for_confirmation=True,debrief_before_promotions=True,promotions=promoted,reward_replay_blocked=True,save_reload_verified=True,return_ack_recovered=args.interrupt_after_resolution,tactical_resume_phase=args.interrupt_phase,source_process_superseded=args.keep_source_alive,requested_viewport=[args.width,args.height],actual_viewport=list(actual_viewport),readiness_verified=ready_at is not None,audio_ownership_verified=True,crash_recovery=args.crash_recovery,debrief_recovery=args.resume_debrief,native_windows_run=sys.platform=='win32',windows_graphics_verified=False))
                    finally:
                        if process.poll() is None:process.terminate();process.wait(timeout=5)
                        os.chdir(root)
    finally:
        os.chdir(previous);window.close()
    (output/'native-report.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'status':'PASS','platform':sys.platform,'native_windows_run':sys.platform=='win32','windows_graphics_verified':False,'cases':results}))


if __name__=='__main__':main()
