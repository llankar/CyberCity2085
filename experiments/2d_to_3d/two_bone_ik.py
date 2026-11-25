"""Position-only two-segment IK. Never stretch a limb to reach a target."""
import numpy as np


def elbow_target(shoulder, target, pole, upper, lower):
    shoulder, target, pole = [np.asarray(p,dtype=float) for p in (shoulder,target,pole)]
    if any(p.shape != (3,) or not np.isfinite(p).all() for p in (shoulder,target,pole)):
        raise ValueError('Finite 3D landmarks required')
    if not np.isfinite([upper,lower]).all() or min(upper,lower) <= 0:
        raise ValueError('Positive limb lengths required')
    delta = target-shoulder
    distance = np.linalg.norm(delta)
    if not abs(upper-lower)+1e-8 < distance < upper+lower-1e-8:
        raise ValueError('Target outside nondegenerate limb reach')
    axis = delta/distance
    bend = pole-axis*np.dot(pole,axis)
    if np.linalg.norm(bend) < 1e-8:
        raise ValueError('Bend pole parallel to target direction')
    bend /= np.linalg.norm(bend)
    along = (upper*upper-lower*lower+distance*distance)/(2*distance)
    height = np.sqrt(max(0,upper*upper-along*along))
    return shoulder+axis*along+bend*height
