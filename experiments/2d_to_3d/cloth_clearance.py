"""Smooth fit corrections over an authored mesh without replacing its topology."""
import numpy as np


def smooth_fit_offsets(points, edges, offsets, iterations=30, strength=.65):
    points=np.asarray(points,dtype=float);offsets=np.asarray(offsets,dtype=float)
    edges=np.asarray(edges,dtype=int)
    if points.ndim!=2 or points.shape[1]!=3 or offsets.shape!=points.shape or not np.isfinite(points).all() or not np.isfinite(offsets).all():
        raise ValueError('Finite matching Nx3 geometry/offset arrays required')
    if edges.ndim!=2 or edges.shape[1]!=2 or edges.size and (edges.min()<0 or edges.max()>=len(points)):
        raise ValueError('Invalid mesh edges')
    if not isinstance(iterations,int) or not 0<=iterations<=1000 or not 0<=strength<=1:
        raise ValueError('Invalid bounded smoothing parameters')
    result=offsets.copy();degree=np.zeros(len(points))
    if not edges.size:return result
    for side in (0,1):np.add.at(degree,edges[:,side],1)
    active=degree>0
    for _ in range(iterations):
        average=np.zeros_like(result)
        np.add.at(average,edges[:,0],result[edges[:,1]])
        np.add.at(average,edges[:,1],result[edges[:,0]])
        average[active]/=degree[active,None]
        result[active]=(1-strength)*result[active]+strength*average[active]
    return result
