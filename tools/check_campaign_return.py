"""Native Linux integration evidence; forced outcomes test plumbing, not Windows embedding."""
from __future__ import annotations
import argparse,json,os,subprocess,sys,tempfile,time
from contextlib import chdir
from pathlib import Path
from unittest.mock import patch
from tools.check_unified_return import _link_directory


def campaign_scenario(mission_id=None, *, state=None):
    """Use the real daily board and normal equipped recruits, with no stat overrides."""
    from game.gamestate import GameState
    from game.recruitment import recruit_agent
    from game.mission_system import ensure_mission_templates
    if state is None:
        roster=[]
        for role in ['samurai','sniper','psi','samurai','sniper']:
            recruit_agent(roster,role)
        state=GameState(characters=roster,selected_agent_names=[c.name for c in roster])
    ensure_mission_templates(state)
    eligible=[(i,m) for i,m in enumerate(state.mission_templates) if mission_id is None or m.id==mission_id]
    if not eligible:raise ValueError('Requested mission is absent from the actual daily board')
    index,mission=min(eligible,key=lambda pair:(pair[1].risk_level,pair[1].objective_type not in {'data_theft','data_with_detour'},pair[1].id))
    state.selected_mission_index=index
    return state,mission


def main():
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
    from game.ui.screens.campaign_ending_view import CampaignEndingView
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('work/unified-experience'))
    parser.add_argument("--outcomes", nargs="+", choices=["victory","defeat","retreat"])
    parser.add_argument("--campaign-play", action="store_true")
    parser.add_argument("--objective-first", action="store_true", help="Compare a pilot that advances toward the objective before attacking")
    parser.add_argument("--mission-id")
    parser.add_argument("--campaign-save", type=Path, help="Resume a campaign saved by a previous run")
    parser.add_argument("--hospital", action="store_true", help="Treat injured agents using campaign downtime before deployment")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--interrupt-after-resolution", action="store_true")
    parser.add_argument("--interrupt-phase", choices=["player","enemy"])
    parser.add_argument("--keep-source-alive", action="store_true")
    parser.add_argument("--crash-recovery", action="store_true")
    parser.add_argument("--resume-debrief", action="store_true")
    args=parser.parse_args()
    if args.campaign_save and not args.campaign_play:
        parser.error("--campaign-save requires --campaign-play")
    if args.hospital and not args.campaign_save:
        parser.error("--hospital requires --campaign-save")
    campaign_save = args.campaign_save.resolve(strict=True) if args.campaign_save else None
    args.outcomes=args.outcomes or (['victory'] if args.campaign_play else ['victory','defeat','retreat'])
    if args.campaign_play and ('retreat' in args.outcomes or args.interrupt_phase):
        parser.error('Natural playthrough has no fabricated retreat or forced interruption fixture')
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[1];previous=Path.cwd();real_popen=subprocess.Popen
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
            with tempfile.TemporaryDirectory(prefix='cybercity-unified-') as tmp, chdir(tmp):
                sandbox=Path(tmp)
                _link_directory(sandbox/'assets', root/'assets')
                _link_directory(sandbox/'godot', root/'godot')
                if args.campaign_play:
                    loaded_state = GameState.load(str(campaign_save)) if campaign_save else None
                    if args.hospital:
                        from game.character import is_deployable
                        from game.management.downtime import DOWNTIME_ACTIVITIES, apply_activity

                        activity = next(item for item in DOWNTIME_ACTIVITIES if item.key == "hospital")
                        print(apply_activity(loaded_state, activity, loaded_state.characters), flush=True)
                        loaded_state.selected_agent_names = [
                            agent.name for agent in loaded_state.characters if is_deployable(agent)
                        ]
                    state,mission=campaign_scenario(
                        args.mission_id, state=loaded_state
                    )
                    (case/'mission-input.json').write_text(json.dumps(mission.to_dict(),indent=2))
                    (case/'roster-input.json').write_text(json.dumps([c.to_dict() for c in state.characters],indent=2))
                else:
                    mission=MissionTemplate(id='unified_'+outcome,title='Unified '+outcome,objective_text='Protocol validation',target_faction='Corp 37',district='Chrome',district_pressure={},starting_enemy_count=3,risk_level=2,objective_type='hack')
                    state=GameState(characters=[Character('Vera')],selected_agent_names=['Vera'],mission_templates=[mission])
                    state.mission_board_generated_day=state.calendar.current_day;state.mission_board_version=2
                starting_levels = {agent.name: agent.stats.level for agent in state.characters}
                hq=ManagementView(state);hq.setup();window.show_view(hq);frame(case/'01-headquarters.png')
                hq._open_mission_map();assert isinstance(window.current_view,MissionWorldMapView);frame(case/'02-world-map.png')
                window.current_view._launch_selected_mission();assert isinstance(window.current_view,MissionBriefingView);frame(case/'03-briefing.png')
                confirm=case/'confirm.request';confirm.unlink(missing_ok=True)
                log=case/'godot.log'
                with log.open('w') as stream:
                    def launch(command,*a,**kw):
                        command=list(command)
                        if "--resolution" in command:
                            index = command.index("--resolution")
                            del command[index:index + 2]
                        command[1:1]=['--resolution',f'{args.width}x{args.height}','--audio-driver','Dummy','--script',('res://tests/campaign_playthrough.gd' if args.campaign_play else 'res://tests/unified_return_flow.gd')]
                        command+=['--qa-confirm',str(confirm),'--qa-captures',str(case),'--qa-outcome',outcome]
                        if args.campaign_play and args.objective_first:
                            command += ["--qa-objective-first", "1"]
                        if args.interrupt_phase: command += ['--qa-interrupt-phase',args.interrupt_phase]
                        return real_popen(command,*a,stdout=stream,stderr=subprocess.STDOUT,**kw)
                    launch_started=time.monotonic()
                    with patch('game.combat.godot_bridge.subprocess.Popen',side_effect=launch):
                        window.current_view.on_key_press(arcade.key.ENTER,0)
                    bridge=window.current_view;assert isinstance(bridge,GodotCombatHandoffView) and bridge.launch_result.launched
                    launch_return_seconds=time.monotonic()-launch_started
                    ready_seconds=None
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
                        deadline=time.monotonic()+(180 if args.campaign_play else 50)
                        while 'UNIFIED_NATIVE_RESULTS_WAITING' not in log.read_text():
                            frame();assert not bridge._launch_failed,bridge._status
                            if getattr(bridge,'_session_ready',False) and ready_seconds is None:ready_seconds=time.monotonic()-launch_started
                            assert process.poll() is None,log.read_text()
                            assert time.monotonic()<deadline,log.read_text()
                            time.sleep(.03)
                        from PIL import Image
                        assert Image.open(case/'godot-results.png').size == (args.width,args.height)
                        from game.combat.session_protocol import read_session_status
                        session=state.combat_sessions[bridge.launch_result.session_id]['session']
                        assert read_session_status(session['status_path'],session['session_id'],mission.id)['ready']
                        assert 'UNIFIED_AUDIO_OWNERSHIP_READY' in log.read_text()
                        if args.interrupt_phase: assert 'UNIFIED_TACTICAL_STATE_RESUMED' in log.read_text()
                        before=state.available_funds
                        for _ in range(12):frame();time.sleep(.08)
                        assert window.current_view is bridge and process.poll() is None
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
                        assert actual['outcome']==outcome,actual
                        if args.campaign_play:
                            playthrough=json.loads((case/'playthrough.json').read_text())
                            assert playthrough['outcome_forced'] is False and playthrough['mission_id']==mission.id
                        (case/'confirmed-result.json').write_text(json.dumps(actual,indent=2)+'\n')
                        after=state.available_funds;bridge.on_update(.1);assert state.available_funds==after
                        window.current_view._go_to_management()
                        promoted=isinstance(window.current_view,AgentPromotionView)
                        if promoted:
                            frame(case/'06-promotions.png')
                            while isinstance(window.current_view,AgentPromotionView):window.current_view._advance()
                        ending = state.campaign.ending
                        assert isinstance(window.current_view, CampaignEndingView if ending else ManagementView)
                        frame(case/('07-ending.png' if ending else '07-headquarters-return.png'))
                        if args.campaign_play:
                            assert promoted == any(
                                agent.stats.level > starting_levels.get(agent.name, agent.stats.level)
                                for agent in state.characters
                            )
                        else:
                            assert promoted == (outcome == 'victory')
                        save=case/'campaign.json';state.save(str(save));loaded=GameState.load(str(save))
                        from game.combat.godot_resolution import resolve_godot_result
                        assert resolve_godot_result(loaded,mission,actual,bridge.launch_result.session_id) is None
                        assert loaded.available_funds==after
                        assert state.latest_mission_debrief and state.latest_agent_aftermath is not None
                        results.append(dict(outcome=outcome,outcome_forced=not args.campaign_play,mission_id=mission.id,launch_return_seconds=launch_return_seconds,ready_seconds=ready_seconds,native_godot=True,results_waited_for_confirmation=True,debrief_before_promotions=True,promotions=promoted,reward_replay_blocked=True,save_reload_verified=True,return_ack_recovered=args.interrupt_after_resolution,tactical_resume_phase=args.interrupt_phase,source_process_superseded=args.keep_source_alive,viewport=[args.width,args.height],readiness_verified=True,audio_ownership_verified=True,crash_recovery=args.crash_recovery,debrief_recovery=args.resume_debrief,windows_graphics_verified=False))
                    finally:
                        if process.poll() is None:process.terminate();process.wait(timeout=5)
    finally:
        os.chdir(previous);window.close()
    (output/'native-report.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'status':'PASS','platform':sys.platform,'windows_graphics_verified':False,'cases':results}))


if __name__=='__main__':main()
