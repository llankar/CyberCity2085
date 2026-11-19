"""Soundtrack routing and silent decoder checks; no desktop input or audio."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import subprocess
import sys

import pytest

from game.audio.music_catalog import MUSIC_TRACKS, battle_music_key, music_path
from game.audio.sound_manager import SoundManager


@pytest.mark.parametrize("mission,expected", [
    (None, "music_battle"),
    (SimpleNamespace(id="sm_act5_citadel"), "music_finale"),
    (SimpleNamespace(id="sm_act5_seven_minutes", objective_type="sabotage"), "music_finale_climax"),
    (SimpleNamespace(objective_type="data_with_detour"), "music_hacking"),
    (SimpleNamespace(objective_type="sabotage"), "music_hacking"),
    (SimpleNamespace(title="Highway Convoy Pursuit"), "music_chase"),
    (SimpleNamespace(title="Street Ambush"), "music_battle"),
])
def test_mission_soundtrack_follows_stakes_and_theme(mission, expected):
    assert battle_music_key(mission) == expected


def test_every_new_mp3_has_a_route_and_exists():
    files = {path.name for path in Path("assets/audio/music").glob("*.mp3")}
    assert files
    assert files <= set(MUSIC_TRACKS.values())
    assert all(music_path(key).is_file() for key in MUSIC_TRACKS)


def test_missing_mp3_uses_original_wav(tmp_path):
    from game.audio import music_catalog
    fallback = tmp_path / "music_battle.wav"
    fallback.touch()
    with patch.object(music_catalog, "MUSIC_DIR", tmp_path):
        assert music_catalog.music_path("music_finale") == fallback


def test_same_track_is_not_restarted_and_disabled_audio_stays_silent():
    with patch("arcade.play_sound", return_value=SimpleNamespace(volume=1.0), create=True) as play, patch("arcade.stop_sound", create=True):
        manager = SoundManager()
        manager._loaded = True
        manager._music = {"music_battle": object()}
        manager.play_music("music_battle")
        manager.play_music("music_battle")
        assert play.call_count == 1
        manager.configure(enabled=False)
        assert manager._music_player.volume == 0
        manager.stop_music()
        manager.play_music("music_battle")
        assert play.call_count == 1


def test_music_decodes_only_the_selected_track_with_loop_support():
    with patch("arcade.load_sound", return_value=object(), create=True) as load, patch("arcade.play_sound", return_value=object(), create=True), patch("arcade.stop_sound", create=True):
        manager = SoundManager()
        manager._loaded = True
        manager._music_paths = {"music_title": music_path("music_title")}
        manager.play_music("music_title")
        load.assert_called_once_with(str(music_path("music_title")), streaming=False)
        assert list(manager._music) == ["music_title"]


def test_godot_loads_and_loops_all_mp3s_with_dummy_audio(tmp_path):
    from game.combat.godot_bridge import find_godot_executable
    executable = find_godot_executable()
    if not executable:
        pytest.skip("Godot not installed")
    source = Path("godot/combat_missions_ui/scripts")
    (tmp_path / "audio_manager.gd").write_text((source / "audio_manager.gd").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "combat_signals.gd").write_text((source / "combat_signals.gd").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "project.godot").write_text('config_version=5\n[autoload]\nCombatSignals="*res://combat_signals.gd"\n', encoding="utf-8")
    tracks = sorted({str(path.resolve()).replace("\\", "/") for path in Path("assets/audio/music").glob("*.mp3")})
    smoke = '''extends SceneTree
func _initialize():
    call_deferred("check_audio")
func check_audio():
    var manager = load("res://audio_manager.gd").new()
    root.add_child(manager)
    for path in TRACKS:
        manager.configure_soundtrack({"battle_music_path": path, "music_volume": 0.0})
        var stream = manager._music_player.stream
        if not stream is AudioStreamMP3 or not stream.loop or stream.get_length() <= 0:
            push_error("MP3 decode/loop failed: " + path)
            quit(1)
            return
    manager.configure_soundtrack({"enabled": false})
    if manager._music_player.playing:
        quit(2)
        return
    print("MP3_SOUNDTRACK_OK")
    quit(0)
'''.replace("TRACKS", json.dumps(tracks))
    (tmp_path / "smoke.gd").write_text(smoke, encoding="utf-8")
    result = subprocess.run([executable, "--headless", "--audio-driver", "Dummy", "--path", str(tmp_path), "--script", "res://smoke.gd"], capture_output=True, text=True, timeout=40)
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SCRIPT ERROR" not in output, output
    assert "MP3_SOUNDTRACK_OK" in output, output


def test_arcade_backend_decodes_all_mp3s_without_playing_them():
    script = '''import pyglet
pyglet.options['audio'] = ('silent',)
from pathlib import Path
for path in Path('assets/audio/music').glob('*.mp3'):
    source = pyglet.media.load(str(path), streaming=True)
    assert source.audio_format is not None and source.duration > 0, str(path)
print('ARCADE_MP3_OK')
'''
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ARCADE_MP3_OK" in result.stdout
