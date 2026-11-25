"""Conservative prototype material regions; final masks require artistic review."""
import math


def region(point,color):
    if len(point)!=3 or len(color)!=3 or not all(math.isfinite(float(v)) for v in (*point,*color)):
        raise ValueError('Finite XYZ/RGB triples required')
    if any(not 0<=v<=1 for v in color):raise ValueError('Expected normalized color')
    x,y,z=point
    hair=(z>1.685 or (z>1.61 and y>.025)) and max(color)<.38
    jacket=(1.10<z<1.535) and (abs(x)<.23 or x<-.16) and not(abs(x)<.066 and y<0) and max(color)<.44 and max(color)-min(color)<.16
    return 1 if hair else (2 if jacket else 0)
