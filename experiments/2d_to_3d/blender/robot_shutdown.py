"""Staged mechanical knee buckle, backward topple and settled shutdown."""
import math


def shutdown_pose(time_s):
    if not math.isfinite(time_s):raise ValueError('Finite shutdown time required')
    def ease(start,end):
        p=max(0.,min(1.,(time_s-start)/(end-start)))
        return p*p*(3-2*p)
    return {'buckle':ease(0,.4),'fall_angle':math.pi/2*ease(.3,1.25),
            'head_tilt':.2*ease(0,.4),'settled':time_s>=1.25}
