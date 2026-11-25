"""Conservative sole-only shin influence redistribution; no geometry modification."""
import math

def redistribute(weights, foot_groups, shin_groups, retained_shin=.7):
    if not 0<=retained_shin<=1:raise ValueError('Shin retention must lie in [0,1]')
    if any(not math.isfinite(value) or value<0 for value in weights.values()):raise ValueError('Finite nonnegative skin weights required')
    foot=sum(weights.get(key,0.) for key in foot_groups)
    if foot<=0:raise ValueError('Existing foot/toe influence required')
    moved=sum(weights.get(key,0.)*(1-retained_shin) for key in shin_groups)
    result=dict(weights)
    for key in shin_groups:
        if key in result:result[key]*=retained_shin
    for key in foot_groups:
        if key in result:result[key]+=moved*weights[key]/foot
    assert abs(sum(result.values())-sum(weights.values()))<1e-10
    return result
