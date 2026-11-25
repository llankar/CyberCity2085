"""World-space mechanical foot targets; no humanoid retargeting dependency."""
import math


def gait(time_s, side=0, period=1.2, stride=.36, duty=.6, lift=.10):
    if period <= 0 or stride <= 0 or not 0 < duty < 1 or lift < 0:
        raise ValueError('Invalid gait dimensions')
    phase = (time_s / period + side * .5) % 1
    travel = -stride / duty * time_s / period
    if phase < duty:
        relative = -stride / 2 + stride * phase / duty
        height = 0.
    else:
        p = (phase - duty) / (1 - duty)
        tangent = (1 - duty) * stride / duty
        relative = ((2*p**3-3*p*p+1)*stride/2
                    + (p**3-2*p*p+p)*tangent
                    - (-2*p**3+3*p*p)*stride/2
                    + (p**3-p*p)*tangent)
        height = lift * math.sin(math.pi*p)**2
    return travel, relative, height, phase < duty
