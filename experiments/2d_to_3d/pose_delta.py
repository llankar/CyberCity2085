"""Local additive pose arithmetic; quaternion order is w,x,y,z.

Independent numeric implementation, not copied engine code. Translation uses a
local additive offset; rotation applies the base-to-weapon delta after body pose.
"""
import numpy as np


def unit_quaternion(value):
    value=np.asarray(value,dtype=float)
    if value.shape!=(4,) or not np.isfinite(value).all() or abs(np.linalg.norm(value)-1)>1e-5:
        raise ValueError('Unit quaternion required')
    return value


def multiply(a,b):
    w,x,y,z=a;v,i,j,k=b
    return np.array([w*v-x*i-y*j-z*k,w*i+x*v+y*k-z*j,w*j-x*k+y*v+z*i,w*k+x*j-y*i+z*v])


def additive_pose(body_position,body_rotation,base_position,base_rotation,target_position,target_rotation):
    positions=[np.asarray(p,dtype=float) for p in [body_position,base_position,target_position]]
    if any(p.shape!=(3,) or not np.isfinite(p).all() for p in positions):
        raise ValueError('Finite local translations required')
    body,base,target=map(unit_quaternion,[body_rotation,base_rotation,target_rotation])
    inverse=base*np.array([1,-1,-1,-1])
    rotation=multiply(body,multiply(inverse,target))
    rotation/=np.linalg.norm(rotation)
    return positions[0]+positions[2]-positions[1],rotation
