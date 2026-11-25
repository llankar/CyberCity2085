"""Small posterior fit of real source hair; no face or skull deformation."""
import math


def fit_point(point):
    if len(point)!=3 or not all(math.isfinite(v) for v in point):
        raise ValueError('Finite XYZ required')
    x,y,z=point
    return ((x+.0037)*.95-.0037, .045+(y-.045)*.8 if y>.045 else y, z)
