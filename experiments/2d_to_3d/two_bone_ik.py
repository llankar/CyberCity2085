"""Analytical two-link placement, retaining lengths and the existing bend side."""
import numpy as np


def elbow_target(shoulder, target, pole, upper, lower):
    """Original strict API: ambiguous or unreachable targets remain errors."""
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


def solve(shoulder, elbow, wrist, target):
    shoulder, elbow, wrist, target = [np.asarray(p, dtype=float) for p in (shoulder, elbow, wrist, target)]
    if any(p.shape != (3,) or not np.isfinite(p).all() for p in (shoulder, elbow, wrist, target)):
        raise ValueError('Finite 3D landmarks required')
    upper, lower = np.linalg.norm(elbow-shoulder), np.linalg.norm(wrist-elbow)
    distance = np.linalg.norm(target-shoulder)
    if min(upper, lower, distance) < 1e-8: raise ValueError('Degenerate limb or target')
    direction = (target-shoulder)/distance
    reach = np.clip(distance, abs(upper-lower)+1e-6, upper+lower-1e-6)
    end = shoulder+direction*reach
    pole = elbow-shoulder-direction*np.dot(elbow-shoulder, direction)
    if np.linalg.norm(pole) < 1e-8:
        axis = np.eye(3)[np.argmin(abs(direction))]
        pole = axis-direction*np.dot(axis, direction)
    pole /= np.linalg.norm(pole)
    return elbow_target(shoulder,end,pole,upper,lower), end
