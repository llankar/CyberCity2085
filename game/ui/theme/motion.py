"""Shared motion timings and easing curves for command UI animations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MotionDurations:
    room_transition_seconds: float = 0.28
    selection_transition_seconds: float = 0.28
    micro_animation_seconds: float = 0.14


@dataclass(frozen=True)
class MotionEasings:
    room_transition: str = "smoothstep"
    selection_transition: str = "smoothstep"
    micro_interaction: str = "ease_out_quad"


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def ease_smoothstep(progress: float) -> float:
    t = clamp01(progress)
    return t * t * (3.0 - 2.0 * t)


def ease_out_quad(progress: float) -> float:
    t = clamp01(progress)
    return 1.0 - (1.0 - t) * (1.0 - t)


def pulse_from_elapsed(elapsed_seconds: float, cycle_seconds: float = 1.8) -> float:
    """Return a light 0..1 pulse for subtle hover/focus/click accents."""
    if cycle_seconds <= 0:
        return 0.0
    phase = (elapsed_seconds % cycle_seconds) / cycle_seconds
    return ease_out_quad(phase if phase <= 0.5 else 1.0 - phase)


durations = MotionDurations()
easings = MotionEasings()
