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


def test_arcade_missing_new_file_stays_silent_without_legacy_fallback(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    play = Mock()
    monkeypatch.setitem(sys.modules, "arcade", SimpleNamespace(
        play_sound=play, load_sound=lambda path: Path(path).name
    ))
    sound = SoundManager()
    sound.play("sfx_fire")
    play.assert_not_called()


def test_combat_clicks_and_generic_movement_only_use_recorded_samples(tmp_path):
    root = tmp_path / "overhaul"
    for relative in ("ui/ui_click_01.wav", "movement/step_concrete_01.wav"):
        make_pcm(root / relative)
    assert [path.name for path in preview_sfx_paths("sfx_ui_click", root=root)] == ["ui_click_01.wav"]
    assert [path.name for path in preview_sfx_paths("sfx_ui_confirm", root=root)] == ["ui_click_01.wav"]
    assert [path.name for path in preview_sfx_paths("sfx_move", root=root)] == ["step_concrete_01.wav"]
    assert preview_sfx_paths("sfx_turn_player", root=root) == ()
    assert preview_sfx_paths("sfx_turn_enemy", root=root) == ()


def test_ambience_is_optional_separate_from_music(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert preview_city_ambience_path() is None
    make_pcm(Path("assets/audio/overhaul/ambience/ambience_city_cc0_01.wav"))
    assert preview_city_ambience_path() is not None


def test_static_godot_audio_contract_uses_only_new_bank():
    root = Path(__file__).resolve().parents[1]
    gd = (root / "godot/combat_missions_ui/scripts/audio_manager.gd").read_text()
    bridge = (root / "game/combat/godot_bridge.py").read_text()
    assert 'AudioStreamWAV.load_from_file(path)' in gd
    assert '"fire_laser"' in gd
    assert '"laboratory"' in gd and '"city_rain"' in gd
    assert 'Neon Street Warfare.mp3' in gd and "Intro 2.mp3" in gd
    assert "sfx_fire.wav" not in gd and "music_battle.wav" not in gd
    assert '"move": ["step_concrete_01.wav"]' in gd
    assert '"ui_click": ["ui_click_01.wav"]' in gd
    assert '"turn_player":            _play_music(_battle_music)' in gd
    assert '"ambience_profile"' in bridge


def test_system_turn_commands_do_not_emit_click_audio():
    root = Path(__file__).resolve().parents[1]
    hud = (root / "godot/combat_missions_ui/scripts/hud_controller.gd").read_text()
    handler = hud.split("func _on_action_pressed(action: String) -> void:", 1)[1].split("func ", 1)[0]
    assert "if action not in _SYSTEM_ACTIONS:" in handler
    assert 'CombatSignals.audio_event.emit("ui_click")' in handler


def test_zero_ap_auto_advance_is_silent():
    root = Path(__file__).resolve().parents[1]
    combat = (root / "godot/combat_missions_ui/scripts/combat_mission_ui.gd").read_text()
    handler = combat.split("func _auto_advance_unit() -> void:", 1)[1].split("func ", 1)[0]
    assert 'audio_event.emit("ui_click")' not in handler


def test_no_audio_catalog_claims_unmaterialized_candidates_are_installed():
    root = Path(__file__).resolve().parents[1]
    import json
    data = json.loads((root / "docs/audio/cc0_ccby_sources.json").read_text())
    assert all(x["distribution_status"] == "not_yet_converted" for x in data["kenney_curated"])


def test_robot_moves_use_robot_specific_cue_in_both_godot_views():
    root = Path(__file__).resolve().parents[1]
    for script in ("unit_visual.gd", "unit_token.gd"):
        text = (root / "godot/combat_missions_ui/scripts" / script).read_text()
        assert 'unit_data.get("role", "")' in text
        assert 'CombatSignals.audio_event.emit("move_robot")' in text
        assert 'CombatSignals.audio_event.emit("move")' in text


def test_freesound_staging_is_distinct_from_committed_wavs():
    root = Path(__file__).resolve().parents[1]
    import json
    data = json.loads((root / "docs/audio/cc0_ccby_sources.json").read_text())
    received = [
        entry for entry in data["sources"]
        if entry.get("received_original_sha256")
    ]
    assert len(received) == 4
    for entry in received:
        assert len(entry["received_original_sha256"]) == 64
        assert len(entry["prepared_output_sha256"]) == 64
        assert entry["prepared_output_format"]["sample_rate_hz"] == 48000
        assert entry["license"] in ("CC0-1.0", "CC-BY-4.0")
