"""Conservative endpoint lifts for sampled inter-key clearance deficits."""
import math


def endpoint_lifts(deficits):
    if not deficits or any(not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in deficits):
        raise ValueError('Expected nonnegative finite interval deficits')
    result=[0.]*(len(deficits)+1)
    for index,value in enumerate(deficits):
        result[index]=max(result[index],value)
        result[index+1]=max(result[index+1],value)
    return result
