"""Fit an evaluated rigid surface and quantify any unrepresented deformation."""
import numpy as np
from mathutils import Matrix


def fit_surface(baseline, current):
    first=np.asarray(baseline,dtype=np.float64)
    second=np.asarray(current,dtype=np.float64)
    if first.shape!=second.shape or first.ndim!=2 or first.shape[1]!=3 or len(first)<3:
        raise ValueError('Stable matching vertex topology required')
    if not np.isfinite(first).all() or not np.isfinite(second).all():
        raise ValueError('Non-finite surface coordinates')
    a=first.mean(axis=0); b=second.mean(axis=0)
    u,_,vt=np.linalg.svd((first-a).T @ (second-b))
    rotation=vt.T @ u.T
    if np.linalg.det(rotation)<0:
        vt[-1]*=-1; rotation=vt.T @ u.T
    translation=b-rotation @ a
    error=float(np.linalg.norm(first @ rotation.T+translation-second,axis=1).max())
    matrix=np.eye(4); matrix[:3,:3]=rotation; matrix[:3,3]=translation
    return Matrix(matrix.tolist()),error
