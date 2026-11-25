"""Bounded neck-to-skull weights for the isolated head fit study."""
import math


def neck_skull_weights(height):
    if not math.isfinite(height):
        raise ValueError('Finite rest height required')
    skull=max(0.,min(1.,(height-1.49)/.065))
    return 1-skull,skull
