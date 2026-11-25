"""Frame sampling uses scene strip time rather than assuming action starts at zero."""
import math


def realtime_sample_count(duration,loop=False,static_pose=False,minimum_fps=24.):
    """Uniform exact-duration samples; preserve nonintegral source end times."""
    if not all(math.isfinite(v) and v>0 for v in (duration,minimum_fps)):
        raise ValueError('Positive finite duration and target rate required')
    if static_pose:return 2
    intervals=max(1,math.ceil(duration*minimum_fps-1e-8))
    return max(2,intervals+(0 if loop else 1))


def atlas_sample_frames(first,last,loop=False,count=4):
    if not all(math.isfinite(t) for t in (first,last)) or last<=first or not isinstance(count,int) or count<2:
        raise ValueError('Finite increasing clip range and at least two samples required')
    denominator=count if loop else count-1
    return [first+(last-first)*index/denominator for index in range(count)]
