"""Focused Arcade/Godot audio integration contract checks.

Runtime tests use a fake Arcade module and actual temporary WAV files;
no GPU or real sound card is required. Godot checks remain static until its
binary can be run in the CI environment.
"""
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import wave
from unittest.mock import Mock

from game.audio.sound_manager import SoundManager
from game.audio.overhaul_assets import preview_sfx_paths, preview_city_ambience_path


def make_pcm(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(48000)
        wf.writeframes(b"\\0" * 9600)


def test_arcade_only_loads_existing_cc0_wavs_and_cycles_variants(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p1 = Path("assets/audio/overhaul/weapons/fire_laser_cc0_01.wav")
    p2 = Path("assets/audio/overhaul/weapons/fire_laser_cc0_02.wav")
    make_pcm(p1)
    make_pcm(p2)
    play = Mock()
    load = Mock(side_effect=lambda path: Path(path).name)
    monkeypatch.setitem(sys.modules, "arcade", SimpleNamespace(play_sound=play, load_sound=load))
    sound = SoundManager()
    sound.play("sfx_fire_laser")
    sound.play("sfx_fire_laser")
    sound.play("sfx_fire_laser")
    assert [call.args[0] for call in play.call_args_list] == [
        "fire_laser_cc0_01.wav", "fire_laser_cc0_02.wav", "fire_laser_cc0_01.wav"
    ]
    assert all("music" not in str(call.args) for call in play.call_args_list)


def test_arcade_missing_cc0_file_uses_original_generic_wav(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_pcm(Path("assets/audio/sfx/sfx_fire.wav"))
    play = Mock()
    monkeypatch.setitem(sys.modules, "arcade", SimpleNamespace(
        play_sound=play, load_sound=lambda path: Path(path).name
    ))
    sound = SoundManager()
    sound.play("sfx_fire")
    play.assert_called_once()
    assert play.call_args.args[0] == "sfx_fire.wav"


def test_ambience_is_optional_separate_from_music(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert preview_city_ambience_path() is None
    make_pcm(Path("assets/audio/overhaul/ambience/ambience_city_cc0_01.wav"))
    assert preview_city_ambience_path() is not None


def test_static_godot_audio_contract_preserves_existing_tracks():
    root = Path(__file__).resolve().parents[1]
    gd = (root / "godot/combat_missions_ui/scripts/audio_manager.gd").read_text()
    bridge = (root / "game/combat/godot_bridge.py").read_text()
    assert 'AudioStreamWAV.load_from_file(path)' in gd
    assert '"fire_laser"' in gd
    assert '"laboratory"' in gd and '"city_rain"' in gd
    assert 'music_battle.wav' in gd and "music_debrief.wav" in gd
    assert '"ambience_profile"' in bridge


def test_no_audio_catalog_claims_unmaterialized_candidates_are_installed():
    root = Path(__file__).resolve().parents[1]
    import json
    data = json.loads((root / "docs/audio/cc0_ccby_sources.json").read_text())
    assert all(x["distribution_status"] == "not_yet_converted" for x in data["kenney_curated"])
