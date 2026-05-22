from game.gamestate import GameState
from game.ui.room_interaction import ROOM_TRANSITION_SECONDS
from game.ui.theme import motion_durations
from game.ui.theme.motion import ease_smoothstep, pulse_from_elapsed


def test_room_transition_uses_shared_motion_duration() -> None:
    assert ROOM_TRANSITION_SECONDS == motion_durations.room_transition_seconds


def test_shared_easing_and_micro_pulse_are_bounded() -> None:
    assert 0.0 <= ease_smoothstep(0.4) <= 1.0
    assert 0.0 <= pulse_from_elapsed(0.9) <= 1.0


def test_optional_audio_feedback_logs_only_when_enabled() -> None:
    gs = GameState()
    before = len(gs.event_log)
    gs.play_ui_audio_feedback("selection")
    assert len(gs.event_log) == before

    gs.ui_audio_feedback_enabled = True
    gs.play_ui_audio_feedback("selection")
    assert gs.event_log[-1] == "Audio cue: selection."
