"""Slowed mechanical inspection motion, not a flight dynamics model."""
import math


def vehicle_motion(clip,time_s,side):
    if side not in (-1,1) or not math.isfinite(time_s):raise ValueError('Valid side and finite time required')
    if clip=='Rotor_Spin':return side*math.tau*2*max(0.,min(2.,time_s)),0.
    if clip not in {'Gear_Retract','Gear_Extend'}:raise ValueError('Unknown vehicle action')
    phase=max(0.,min(1.,time_s));blend=phase*phase*(3-2*phase)
    folded=blend if clip=='Gear_Retract' else 1-blend
    return 0.,side*math.pi/2*folded
