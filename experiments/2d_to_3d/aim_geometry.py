"""Shortest world-space correction that levels aim without changing its yaw."""
import numpy as np

def horizontal_aim_correction(direction):
    direction=np.asarray(direction,dtype=float)
    if direction.shape!=(3,) or not np.isfinite(direction).all() or np.linalg.norm(direction)<1e-8:
        raise ValueError('Finite nonzero aim direction required')
    forward=direction/np.linalg.norm(direction)
    horizontal=forward.copy();horizontal[2]=0
    if np.linalg.norm(horizontal)<1e-8:raise ValueError('Vertical aim has no horizontal heading')
    horizontal/=np.linalg.norm(horizontal)
    quaternion=np.r_[1+forward@horizontal,np.cross(forward,horizontal)]
    return quaternion/np.linalg.norm(quaternion)
