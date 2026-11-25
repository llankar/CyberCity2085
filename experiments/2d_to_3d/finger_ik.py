"""Bounded planar three-segment finger fit; limits are rig-design parameters."""
import numpy as np


def segment_directions(lengths, target, normal, limits_degrees=(95,75)):
    lengths = np.asarray(lengths,dtype=float)
    target = np.asarray(target,dtype=float)
    normal = np.asarray(normal,dtype=float)
    limits = np.radians(limits_degrees)
    if lengths.shape != (3,) or target.shape != (3,) or normal.shape != (3,) or limits.shape != (2,):
        raise ValueError('Three lengths, target, plane normal and two bend limits required')
    if not all(np.isfinite(v).all() for v in (lengths,target,normal,limits)) or min(lengths) <= 0 or min(limits) <= 0 or sum(limits) >= np.pi:
        raise ValueError('Invalid lengths or bend bounds')
    distance = np.linalg.norm(target)
    if distance <= 1e-8:
        raise ValueError('Degenerate finger target')
    def resultant(factor):
        angles = np.array([0,limits[0]*factor,sum(limits)*factor])
        return np.array([np.dot(lengths,np.cos(angles)),np.dot(lengths,np.sin(angles))])
    if not np.linalg.norm(resultant(1))-1e-7 <= distance <= sum(lengths)+1e-7:
        raise ValueError('Target requires stretching or exceeds bend limits')
    low,high = 0.,1.
    for _ in range(48):
        middle = (low+high)/2
        if np.linalg.norm(resultant(middle)) > distance: low=middle
        else: high=middle
    factor = (low+high)/2
    result = resultant(factor)
    phase = np.arctan2(result[1],result[0])
    axis = target/distance
    normal = normal-axis*np.dot(normal,axis)
    if np.linalg.norm(normal) < 1e-8:
        raise ValueError('Ambiguous finger bending plane')
    normal /= np.linalg.norm(normal)
    tangent = np.cross(normal,axis)
    angles = np.array([0,limits[0]*factor,sum(limits)*factor])-phase
    return np.array([axis*np.cos(angle)+tangent*np.sin(angle) for angle in angles])
