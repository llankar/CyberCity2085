"""Finite segment/triangle crossings; parallel and coplanar cases are unresolved."""
import numpy as np


def segment_hit(start,end,a,b,c):
    start,end,a,b,c=[np.asarray(v,dtype=float) for v in (start,end,a,b,c)]
    direction=end-start;edge1=b-a;edge2=c-a
    p=np.cross(direction,edge2);det=float(edge1@p)
    if abs(det)<1e-12:return None
    inverse=1/det;tvec=start-a;u=float(tvec@p)*inverse
    if u<0 or u>1:return None
    q=np.cross(tvec,edge1);v=float(direction@q)*inverse
    if v<0 or u+v>1:return None
    t=float(edge2@q)*inverse
    return start+t*direction if 0<=t<=1 else None
