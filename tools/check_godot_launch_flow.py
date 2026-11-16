"""Real Arcade -> native Godot -> Arcade checks, isolated from campaign files.

Run with a display: python -m tools.check_godot_launch_flow
The normal launch checks use the untouched game scene. The completion check
uses the existing Godot regression driver to perform actions and write its
actual mission result (no fabricated JSON, no fake child process).
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from unittest.mock import patch


def main():
    import arcade
    from game.character import Character
    from game.gamestate import GameState
    from game.mission_templates import MissionTemplate
    from game.persistence.save_system import SaveSystem
    from game.ui.screens.mission_briefing_view import MissionBriefingView
    from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView
    from game.ui.screens.management_screen import ManagementView
    from game.views import RPGView, BattleView
    root = Path(__file__).resolve().parents[1]
    original_cwd = Path.cwd()
    real_popen = subprocess.Popen
    checks = []
    from game.ui.music_window import MusicTransitionMixin
    class GameWindow(MusicTransitionMixin, arcade.Window):
        pass
    window = GameWindow(1280,720,'Godot launch integration',visible=False)
    try:
        with tempfile.TemporaryDirectory(prefix='cybercity-launch-') as directory:
            session = Path(directory)
            (session/'assets').symlink_to(root/'assets',target_is_directory=True)
            (session/'godot').symlink_to(root/'godot',target_is_directory=True)
            os.chdir(session)
            mission = MissionTemplate(id='launch_flow',title='Launch integration',objective_text='Hack terminal',
                target_faction='Corp 37',district='Chrome',district_pressure={},starting_enemy_count=3,
                risk_level=3,objective_type='hack')

            def campaign():
                state = GameState(characters=[Character('Rook')],selected_agent_names=['Rook'],mission_templates=[mission])
                # Reproduce a saved campaign carrying the former Arcade default.
                state.save(str(session/"old-save.json"))
                data = json.loads((session/"old-save.json").read_text())
                data.pop('combat_visual_version')
                data['combat_mission_ui_engine'] = 'arcade'
                (session/'old-save.json').write_text(json.dumps(data))
                restored, status = SaveSystem.load_game(session/'old-save.json')
                assert status.ok and restored.combat_mission_ui_engine == 'godot'
                restored.active_mission = mission
                return restored

            def start_and_check(entry, automated=False):
                state = campaign()
                before = state.available_funds
                log = session/f'{entry}-{automated}.log'
                with log.open('w') as stream:
                    def start(command, *args, **kwargs):
                        assert '--handoff' in command and '--path' in command
                        command = list(command)
                        command[1:1] = ['--audio-driver','Dummy']
                        if automated:
                            command[1:1] = ['--script','res://tests/visual_regression.gd']
                        return real_popen(command,*args,stdout=stream,stderr=subprocess.STDOUT,**kwargs)
                    with patch('game.combat.godot_bridge.subprocess.Popen',side_effect=start):
                        if entry == 'briefing':
                            view = MissionBriefingView(state,mission)
                            window.show_view(view)
                            view.on_key_press(arcade.key.ENTER,0)
                        else:
                            view = RPGView(state)
                            window.show_view(view)
                            view.setup()
                            view.launch_selected_mission()
                    bridge = window.current_view
                    assert isinstance(bridge,GodotCombatHandoffView), type(bridge)
                    assert bridge.launch_result.launched and not bridge._launch_failed
                    child = bridge.launch_result.process
                    if automated:
                        assert child.wait(timeout=45) == 0, log.read_text()
                        output = log.read_text()
                        assert 'VISUAL_REGRESSION:' in output and 'failures=0' in output, output
                        actual_result = json.loads((session/'runtime/godot_combat/mission_result.json').read_text())
                        bridge.on_update(0.3)
                        assert isinstance(window.current_view,ManagementView)
                        assert state.available_funds == before+actual_result['funds_earned']
                        funds = state.available_funds
                        bridge.on_update(0.3)
                        assert state.available_funds == funds
                        checks.append('real_godot_actions_result_rewards_and_management_return_once')
                    else:
                        deadline = time.monotonic()+25
                        while time.monotonic() < deadline:
                            window.dispatch_events()
                            bridge.on_update(0.1)
                            if 'TACTICAL COMBAT UI READY' in log.read_text(): break
                            if child.poll() is not None: raise AssertionError(log.read_text())
                            time.sleep(0.05)
                        output = log.read_text()
                        assert 'TACTICAL COMBAT UI READY' in output, output
                        assert 'OpenGL' in output, output
                        assert 'SCRIPT ERROR' not in output, output
                        assert window.current_view is bridge and not bridge._launch_failed
                        bridge.on_key_press(arcade.key.ESCAPE,0)
                        child.wait(timeout=10)
                        checks.append(entry+'_launches_real_native_godot_from_migrated_save')

            start_and_check('briefing')
            start_and_check('rpg')
            start_and_check('briefing',automated=True)
            # Missing executable: show the actual recovery screen, preserve state,
            # and only show the legacy deployment after the user's explicit F.
            state = campaign()
            before = state.available_funds
            with patch('game.combat.godot_bridge.find_godot_executable',return_value=str(session/'missing-godot.exe')):
                view = MissionBriefingView(state,mission)
                window.show_view(view)
                view.on_key_press(arcade.key.ENTER,0)
            bridge = window.current_view
            assert isinstance(bridge,GodotCombatHandoffView) and bridge._launch_failed
            bridge.on_draw()
            bridge.on_update(1.0)
            assert window.current_view is bridge and state.available_funds == before
            bridge.on_key_press(arcade.key.F,0)
            assert isinstance(window.current_view,BattleView)
            checks.append('missing_executable_visible_error_then_explicit_legacy_choice')
            print(json.dumps({'checks':checks,'native_godot':True,'fake_processes':False,'isolated_campaign':True}))
    finally:
        view = window.current_view
        if isinstance(view,GodotCombatHandoffView): view._cleanup_godot()
        window.close()
        os.chdir(original_cwd)

if __name__ == '__main__':
    main()
