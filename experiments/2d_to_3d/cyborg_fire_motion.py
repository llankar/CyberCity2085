"""Single-shot timing in source24fps frames; no gameplay damage simulation."""
import math


def smooth(value):
    value=max(0.,min(1.,value))
    return value*value*(3-2*value)


def sample(frame):
    if not isinstance(frame,(int,float)) or not math.isfinite(frame) or not 0<=frame<=18:
        raise ValueError('Expected a finite frame in0..18')
    raise_amount=smooth(frame/6) if frame<=6 else (1. if frame<=12 else 1-smooth((frame-12)/6))
    recoil=smooth((frame-6)/2) if frame<=8 else 1-smooth((frame-8)/4)
    return {'raise':raise_amount,'recoil':recoil,'pitch_rad':-math.radians(4)*recoil,'slide_back_m':.02*recoil}
