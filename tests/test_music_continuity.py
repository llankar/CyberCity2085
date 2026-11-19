"""Physical soundtrack identity and transport across UI/backend boundaries."""
import json
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from game.audio.sound_manager import SoundManager
from game.ui.music_window import MusicTransitionMixin


class Player:
    def __init__(self):
        self.time = 0.0
        self.playing = True
        self.source = SimpleNamespace(duration=120.0)
        self.volume = .5
    def pause(self): self.playing = False
    def play(self): self.playing = True
    def seek(self, position): self.time = position


@pytest.fixture
def soundtrack(tmp_path, monkeypatch):
    # Keep soundtrack transport tests isolated from the production ambience bank.
    monkeypatch.chdir(tmp_path)
    paths = [tmp_path / 'shared.mp3', tmp_path / 'battle.mp3']
    for path in paths: path.write_bytes(b'fixture')
    players = []
    def play(*args, **kwargs):
        player = Player(); players.append(player); return player
    arcade = SimpleNamespace(load_sound=Mock(return_value=object()),play_sound=Mock(side_effect=play),stop_sound=Mock())
    monkeypatch.setitem(sys.modules,'arcade',arcade)
    manager = SoundManager()
    manager._loaded = True
    manager._music_paths = {'music_management': paths[0], 'music_briefing': paths[0], 'music_battle': paths[1]}
    monkeypatch.setattr(SoundManager,'_instance',manager)
    return manager, arcade, players, paths


def test_same_file_alias_resumes_original_player_without_decode_or_restart(soundtrack):
    manager, arcade, players, paths = soundtrack
    manager.play_music('music_management')
    players[0].time = 37.5
    manager.pause_music()
    manager.play_music('music_briefing')
    assert manager._music_player is players[0]
    assert players[0].playing and players[0].time == 37.5
    assert arcade.play_sound.call_count == arcade.load_sound.call_count == 1
    arcade.stop_sound.assert_not_called()


def test_different_tracks_have_independent_bookmarks_and_disabled_stays_silent(soundtrack):
    manager, arcade, players, paths = soundtrack
    manager.play_music('music_management')
    players[0].time = 37.5
    manager.play_music('music_battle')
    assert players[1].time == 0
    players[1].time = 19.0
    manager.play_music('music_briefing')
    assert players[2].time == 37.5
    assert manager.music_position_for(paths[1]) == 19.0
    manager.pause_music()
    manager.configure(enabled=False)
    manager.resume_music()
    manager.play_music('music_battle')
    assert not players[2].playing
    assert len(players) == 3


def test_view_transition_pauses_until_destination_is_ready(soundtrack):
    manager, arcade, players, paths = soundtrack
    manager.play_music('music_management')
    players[0].time = 12
    class Window:
        def show_view(self, view):
            assert not players[0].playing
            assert players[0].time == 12
            view()
            assert not manager._music_player.playing
    class TestWindow(MusicTransitionMixin, Window): pass
    TestWindow().show_view(lambda: manager.play_music('music_briefing'))
    assert players[0].playing and len(players)==1
    with pytest.raises(RuntimeError):
        TestWindow().show_view(lambda: (_ for _ in ()).throw(RuntimeError('view failed')))
    assert players[0].playing


def test_external_backend_owns_audio_until_next_music_context(soundtrack):
    manager, arcade, players, paths = soundtrack
    manager.play_music('music_management')
    players[0].time = 12
    manager.pause_music(external=True)
    manager.resume_music()  # finally block of window.show_view must not unpause Arcade.
    assert not players[0].playing
    manager.play_music('music_briefing')
    assert players[0].playing and players[0].time==12


def test_godot_result_restores_bookmark_before_returning_to_same_track(soundtrack, tmp_path):
    manager, arcade, players, paths = soundtrack
    manager.play_music('music_battle')
    players[0].time = 12
    manager.pause_music(external=True)
    from game.combat.godot_bridge import read_godot_combat_result
    path = tmp_path/'result.json'
    path.write_text(json.dumps({'outcome':'victory','music_playback':{'path':str(paths[1]),'position':41.5}}))
    assert read_godot_combat_result(path)['outcome']=='victory'
    assert not players[0].playing and players[0].time==41.5
    manager.play_music('music_battle')
    assert players[0].playing and players[0].time==41.5
    manager.remember_music_position(paths[1],float('nan'))
    assert players[0].time==41.5


def test_handoff_keeps_position_when_battle_uses_same_physical_track(soundtrack, monkeypatch):
    manager, arcade, players, paths = soundtrack
    manager.play_music('music_management')
    players[0].time = 37.5
    manager.begin_view_transition()
    from game.character import Character
    from game.gamestate import GameState
    from game.mission_templates import MissionTemplate
    from game.combat.godot_bridge import build_godot_combat_payload
    monkeypatch.setattr('game.audio.music_catalog.music_path',lambda key:paths[0])
    state = GameState(characters=[Character('Rook')],selected_agent_names=['Rook'])
    mission = MissionTemplate(id='continuity',title='Continuity',objective_text='Extract',target_faction='Corp 37',district='Chrome',district_pressure={},starting_enemy_count=2,risk_level=2,objective_type='extract')
    payload = build_godot_combat_payload(state,mission)
    assert payload['audio']['start_position']==37.5
    assert payload['audio']['battle_music_path']==str(paths[0].resolve())
    assert not players[0].playing and len(players)==1
    manager.end_view_transition()


def test_result_bookmark_accounts_for_child_playback_until_parent_reads_it(soundtrack, tmp_path, monkeypatch):
    manager, arcade, players, paths = soundtrack
    manager.play_music('music_battle')
    manager.pause_music(external=True)
    from game.combat.godot_bridge import read_godot_combat_result
    path = tmp_path/'result.json'
    path.write_text(json.dumps({'music_playback':{'path':str(paths[1]),'position':41.5,'captured_at':199.0}}))
    monkeypatch.setattr('time.time',lambda:200.0)
    read_godot_combat_result(path)
    assert players[0].time==42.5
    assert not players[0].playing
