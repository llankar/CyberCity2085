"""Invert measured screen projections into the existing E,SE,S,SW,W,NW,N,NE order."""
import math


def facing_lookup(projected_vectors,y_scale=2.):
    if len(projected_vectors)!=8 or not math.isfinite(y_scale) or y_scale<=0:
        raise ValueError('Eight projections and positive finite aspect required')
    lookup=[None]*8
    for orbit,delta in enumerate(projected_vectors):
        if len(delta)!=2 or not all(math.isfinite(v) for v in delta) or math.hypot(*delta)<1e-10:
            raise ValueError('Finite nonzero screen vector required')
        angle=math.atan2(delta[1]*y_scale,delta[0])
        facing=math.floor(angle/(math.tau/8)+.5)%8
        if lookup[facing] is not None:raise ValueError('Orbit views do not cover eight distinct facings')
        lookup[facing]=orbit
    return lookup
