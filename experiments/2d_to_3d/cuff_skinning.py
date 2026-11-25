"""Smooth forearm influence for recovered authored cuff vertices."""
import math


def influence(distance,span=.05):
    if not math.isfinite(distance) or not math.isfinite(span) or span<=0:
        raise ValueError('Finite distance and positive span required')
    t=max(0.,min(1.,distance/span))
    return t*t*(3-2*t)
