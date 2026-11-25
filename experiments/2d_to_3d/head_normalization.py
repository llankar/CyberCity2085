"""Uniform scan-bust normalization; rejects collapsed or nonfinite bounds."""
import numpy as np


def normalization(low,high,height=.45):
    low=np.asarray(low,dtype=float);high=np.asarray(high,dtype=float)
    if low.shape!=(3,) or high.shape!=(3,) or not np.isfinite([*low,*high,height]).all() or height<=0 or np.any(high<=low):
        raise ValueError('Finite increasing XYZ bounds and positive height required')
    scale=height/(high[2]-low[2])
    result=np.eye(4)*scale;result[3,3]=1
    result[:3,3]=-np.array([(low[0]+high[0])/2,(low[1]+high[1])/2,low[2]])*scale
    return result
