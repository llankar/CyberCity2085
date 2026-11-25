"""Bounded mechanical hit recoil, returning to planted neutral stance."""
import math


def recoil_amount(time_s):
    if not math.isfinite(time_s):raise ValueError('Finite action time required')
    if time_s<=0 or time_s>=.8:return 0.
    p=time_s/.2 if time_s<=.2 else (.8-time_s)/.6
    return p*p*(3-2*p)
