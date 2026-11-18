"""Transport ownership tests; these do not substitute for listening to audio."""
import json
from unittest.mock import Mock,patch
import pytest
from test_unified_mission_resolution import scenario
from game.combat.audio_transfer import release_music_to_godot
from game.audio.sound_manager import SoundManager


def test_ready_transfer_pauses_before_publication_and_refreshes_bookmark(tmp_path):
    state, _, session, _ = scenario(tmp_path)
    music = Mock(); music.music_position_for.return_value = 42.5
    def publish(path, payload):
        music.pause_music.assert_called_once_with(external=True)
        assert payload['audio']['start_position'] == 42.5
        assert payload['session_id'] == session['session_id']
        assert payload['mission_id'] == session['mission_id']
        assert payload['event'] == 'audio_released'
    with patch('game.combat.audio_transfer.SoundManager.get',return_value=music),patch('game.combat.audio_transfer.atomic_json',side_effect=publish):
        release_music_to_godot(state.combat_sessions[session['session_id']])
    music.release_external_music.assert_not_called()


def test_failed_audio_release_returns_music_ownership(tmp_path):
    state, _, session, _ = scenario(tmp_path)
    music = Mock(); music.music_position_for.return_value = 9
    with patch('game.combat.audio_transfer.SoundManager.get',return_value=music),patch('game.combat.audio_transfer.atomic_json',side_effect=OSError('disk full')):
        with pytest.raises(OSError):release_music_to_godot(state.combat_sessions[session['session_id']])
    music.release_external_music.assert_called_once()


def test_legacy_session_does_not_silence_music():
    with patch('game.combat.audio_transfer.SoundManager.get') as music:
        release_music_to_godot({'session':{}})
    music.assert_not_called()


def test_release_respects_view_transition_before_resuming():
    music=SoundManager();music._enabled=True;music._music_player=Mock();music._music_player.playing=False
    music._external_music=True;music._view_transition_depth=1
    music.release_external_music()
    music._music_player.play.assert_not_called()
    music.end_view_transition()
    music._music_player.play.assert_called_once()


def test_tactical_recovery_uses_recorded_position_without_advancing_offline_time(tmp_path):
    state, _, session, _ = scenario(tmp_path)
    from pathlib import Path
    path=Path(session['audio_path']).with_name('handoff.json')
    payload=json.loads(path.read_text())
    payload['resume_snapshot']={'music_playback':{'path':payload['audio']['battle_music_path'],'position':31.5,'captured_at':1}}
    path.write_text(json.dumps(payload))
    music=Mock();music.music_position_for.return_value=0
    with patch('game.combat.audio_transfer.SoundManager.get',return_value=music):
        release_music_to_godot(state.combat_sessions[session['session_id']])
    assert json.loads(Path(session['audio_path']).read_text())['audio']['start_position']==31.5
