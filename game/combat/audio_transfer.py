"""Single-owner music handoff, delayed until Godot's first ready frame."""
import json
from pathlib import Path
from game.audio import SoundManager
from .session_protocol import atomic_json


def release_music_to_godot(record):
    session = record['session']
    if not session.get('audio_path'):
        return  # Backward-compatible session without a music ownership channel.
    handoff = Path(session['audio_path']).with_name('handoff.json')
    settings = json.loads(handoff.read_text(encoding='utf-8'))['audio']
    music = SoundManager.get()
    path = settings.get('battle_music_path')
    settings['start_position'] = music.music_position_for(path) if path else 0.0
    music.pause_music(external=True)
    try:
        atomic_json(session['audio_path'], dict(protocol_version=2,
            session_id=session['session_id'], mission_id=session['mission_id'],
            event='audio_released', audio=settings))
    except (OSError, ValueError, TypeError):
        music.release_external_music()
        raise
