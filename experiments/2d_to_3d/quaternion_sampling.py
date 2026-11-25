"""Shortest-arc unit quaternion sampling, wxyz, independent of Blender."""
import numpy as np


def slerp(first, second, fraction):
    values = [np.asarray(value, dtype=float) for value in (first, second)]
    if any(value.shape != (4,) or not np.isfinite(value).all() or
           abs(np.linalg.norm(value) - 1) > 1e-5 for value in values):
        raise ValueError('Finite unit quaternions required')
    if not np.isfinite(fraction) or not 0 <= fraction <= 1:
        raise ValueError('Fraction must lie within the segment')
    first, second = values
    dot = float(first @ second)
    if dot < 0:
        second = -second
        dot = -dot
    if dot > .999999:
        result = first * (1 - fraction) + second * fraction
    else:
        angle = np.arccos(np.clip(dot, -1, 1))
        result = (first * np.sin((1 - fraction) * angle) +
                  second * np.sin(fraction * angle)) / np.sin(angle)
    return result / np.linalg.norm(result)
