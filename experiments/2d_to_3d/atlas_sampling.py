"""Frame sampling uses scene strip time rather than assuming action starts at zero."""
import math


def atlas_sample_frames(first,last,loop=False,count=4):
    if not all(math.isfinite(t) for t in (first,last)) or last<=first or not isinstance(count,int) or count<2:
        raise ValueError('Finite increasing clip range and at least two samples required')
    denominator=count if loop else count-1
    return [first+(last-first)*index/denominator for index in range(count)]
