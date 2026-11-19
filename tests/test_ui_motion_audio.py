from game.gamestate import GameState
from game.ui.room_interaction import ROOM_TRANSITION_SECONDS
from game.ui.theme import motion_durations
from game.ui.theme.motion import ease_smoothstep, pulse_from_elapsed


def test_room_transition_uses_shared_motion_duration() -> None:
    assert ROOM_TRANSITION_SECONDS == motion_durations.room_transition_seconds


def test_shared_easing_and_micro_pulse_are_bounded() -> None:
    assert 0.0 <= ease_smoothstep(0.4) <= 1.0
    assert 0.0 <= pulse_from_elapsed(0.9) <= 1.0


def test_optional_audio_feedback_does_not_raise() -> None:
    """play_ui_audio_feedback now delegates to SoundManager (no window = silent no-op)."""
    gs = GameState()
    before = len(gs.event_log)
    # Must not raise even when no Arcade window is available
    gs.play_ui_audio_feedback("selection")
    gs.play_ui_audio_feedback("ui_click")
    # Event log should not grow (audio no longer writes to event log)
    assert len(gs.event_log) == before
