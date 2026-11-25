"""Bounded extension of existing lower-neck vertices, preserving upper facial anatomy."""
import math


def extended_height(height, bottom=1.4884845, top=1.535, extension=.045):
    if not all(math.isfinite(v) for v in (height,bottom,top,extension)) or top<=bottom or extension<0:
        raise ValueError('Finite ordered neck band and nonnegative extension required')
    t=max(0.,min(1.,(top-height)/(top-bottom)))
    return height-extension*t*t*(3-2*t)
