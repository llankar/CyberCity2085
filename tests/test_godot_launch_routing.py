"""Visual-2 save migration and explicit launch failure behavior."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
import pytest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from game.character import Character
from game.gamestate import GameState


def test_handoff_copy_never_exposes_engine_or_runtime_names():
    from game.ui.screens.godot_combat_handoff_view import _player_launch_status
    for launched in (True, False):
        status = _player_launch_status(SimpleNamespace(
            launched=launched,
            message="Mission sent to the application Godot runtime.",
        ))
        assert "godot" not in status.lower()
        assert "runtime" not in status.lower()
        assert "arcade" not in status.lower()
    panel = Path("game/ui/components/utilities/handoff.py").read_text(encoding="utf-8")
    draw = panel.split("    def draw(self, v):", 1)[1]
    assert "CHOISIR GODOT" not in draw and "COMBAT ARCADE" not in draw
    assert "MODE DE SECOURS" not in draw and "FALLBACK MODE" not in draw
    view = Path("game/ui/screens/godot_combat_handoff_view.py").read_text(encoding="utf-8")
    assert "arcade.key.F and self._launch_failed" not in view
    assert "def _fallback_to_arcade_battle" not in view


def test_ready_tactical_window_is_raised_without_waiting_for_an_arcade_click():
    view = Path("game/ui/screens/godot_combat_handoff_view.py").read_text(encoding="utf-8")
    win32 = Path("game/combat/win32_embed.py").read_text(encoding="utf-8")
    overlay = view.split("    def _try_overlay(self)", 1)[1].split(
        "    def _cleanup_godot", 1
    )[0]
    show = win32.split("def show_window", 1)[1].split("def terminate_pid", 1)[0]
    assert "not is_foreground_window(self._arcade_hwnd)" not in overlay
    assert "show_window(hwnd)" in overlay
    assert "BringWindowToTop(hwnd)" in show
    assert "SetActiveWindow(hwnd)" in show
    assert "SetForegroundWindow(hwnd)" in show


def test_old_arcade_default_migrates_without_touching_campaign_progress(tmp_path):
    state = GameState(characters=[Character('Rook')],selected_agent_names=['Rook'])
    state.strategic_resources['credits'] = 123
    path = tmp_path/"campaign.json"
    state.save(str(path))
    payload = json.loads(path.read_text())
    payload.pop('combat_visual_version')
    payload['combat_mission_ui_engine'] = 'arcade'
    path.write_text(json.dumps(payload))
    restored = GameState.load(str(path))
    assert restored.combat_mission_ui_engine == 'godot'
    assert restored.characters[0].name == 'Rook'
    assert restored.selected_agent_names == ['Rook']
    assert restored.strategic_resources['credits'] == 123
    assert payload['combat_mission_ui_engine'] == 'arcade'  # Source save not modified in place.
    restored.save(str(path))
    assert json.loads(path.read_text())['combat_visual_version'] == 2


def test_current_explicit_arcade_preference_roundtrips(tmp_path):
    state = GameState(combat_mission_ui_engine='arcade')
    path = tmp_path/'current.json'
    state.save(str(path))
    assert GameState.load(str(path)).combat_mission_ui_engine == 'arcade'
    assert GameState().combat_mission_ui_engine == 'godot'


def test_missing_engine_in_old_save_selects_godot(tmp_path):
    path = tmp_path/"old.json"
    GameState().save(str(path))
    data = json.loads(path.read_text())
    data.pop('combat_visual_version')
    data.pop('combat_mission_ui_engine')
    path.write_text(json.dumps(data))
    assert GameState.load(str(path)).combat_mission_ui_engine == 'godot'


def test_retry_and_choose_executable_never_silently_start_arcade():
    from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView, arcade
    bridge = GodotCombatHandoffView.__new__(GodotCombatHandoffView)
    bridge.game_state = GameState()
    bridge.mission = Mock()
    bridge.window = Mock()
    bridge._launch_failed = True
    bridge._overlaid = False
    bridge._cleanup_godot = Mock()
    bridge._fallback_to_arcade_battle = Mock()
    result = SimpleNamespace(launched=True,message='Godot started',process=None,process_pid=None)
    with patch.object(arcade,"key",SimpleNamespace(R=82,S=83,G=71,F=70,ESCAPE=27)), \
         patch('game.combat.godot_bridge.launch_godot_combat_ui',return_value=result) as launch:
        bridge.on_key_press(82,0)
    launch.assert_called_once_with(bridge.game_state,bridge.mission)
    assert not bridge._launch_failed
    bridge._fallback_to_arcade_battle.assert_not_called()
    bridge._launch_failed = True
    with patch.object(arcade,"key",SimpleNamespace(R=82,S=83,G=71,F=70,ESCAPE=27)), \
         patch('game.ui.screens.settings_screen._browse_for_godot_executable',return_value='D:/Godot/godot.exe'), \
         patch('game.ui.screens.settings_screen._persist_godot_bin_path') as save, \
         patch.object(bridge,'_retry_godot') as retry:
        bridge.on_key_press(71,0)
    save.assert_called_once_with('D:/Godot/godot.exe')
    retry.assert_called_once()


@pytest.mark.skipif(sys.platform != 'linux' or not os.environ.get('DISPLAY') or not (shutil.which('godot') or shutil.which('godot4')),
                    reason='Native cross-process check requires Linux/X11 and Godot; Win32 overlay not exercised here')
def test_native_campaign_launch_and_godot_result_return():
    result = subprocess.run([sys.executable,'-m','tools.check_godot_launch_flow'],
        cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,timeout=100,
        env={**os.environ,'ALSOFT_DRIVERS':'null'})
    assert result.returncode == 0, result.stdout+result.stderr
    report = json.loads(result.stdout.strip().splitlines()[-1])
    assert report['native_godot'] and not report['fake_processes']
    assert len(report['checks']) == 4
