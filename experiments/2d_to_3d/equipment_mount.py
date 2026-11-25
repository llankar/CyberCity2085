"""Front-facing rigid equipment mount clearance, in meters and Blender -Y facing."""
import math


def front_offset(support_y,rear_y,clearance=.004):
    support_y=tuple(support_y)
    if not support_y or not all(math.isfinite(v) for v in (*support_y,rear_y,clearance)) or clearance<=0:
        raise ValueError('Finite torso support points and positive clearance required')
    shift=min(support_y)-clearance-rear_y
    if abs(shift)>=.15:
        raise ValueError('Source units or equipment placement mismatch')
    return shift
