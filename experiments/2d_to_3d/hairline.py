"""Measured undercut half-spaces; front quiff stays lower than nape/temples."""
import math


def cutoff(x,y):
    if not math.isfinite(x) or not math.isfinite(y):
        raise ValueError('Finite scalp XY required')
    return 1.685+.22*(y+.06)+.3*max(0.,abs(x)-.04)


def planes():
    return [((0,0,1.6982),(0,-.22,1)),((0,0,1.6862),(-.3,-.22,1)),((0,0,1.6862),(.3,-.22,1))]
