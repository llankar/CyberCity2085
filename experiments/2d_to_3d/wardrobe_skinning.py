"""Barycentric transfer of existing skin weights, without any skeleton invention."""
import numpy as np


def surface_weights(point, triangle, weights, limit=4):
    points=np.asarray(triangle,dtype=float);point=np.asarray(point,dtype=float)
    if points.shape!=(3,3) or point.shape!=(3,) or not np.isfinite(points).all() or not np.isfinite(point).all():
        raise ValueError('Finite triangle and point required')
    if len(weights)!=3 or limit<1:raise ValueError('Three source weight maps and a positive limit required')
    a,b,c=points;v0=b-a;v1=c-a;v2=point-a
    d00=v0@v0;d01=v0@v1;d11=v1@v1;d20=v2@v0;d21=v2@v1
    denominator=d00*d11-d01*d01
    if denominator<=1e-12*max(d00*d11,1e-300):raise ValueError('Degenerate source triangle')
    second=(d11*d20-d01*d21)/denominator;third=(d00*d21-d01*d20)/denominator
    bary=np.array([1-second-third,second,third])
    if bary.min() < -1e-4 or bary.max()>1.0001:raise ValueError('Projected point lies outside source triangle')
    bary=np.clip(bary,0,1)
    influences={}
    for values,amount in zip(weights,bary):
        for name,value in values.items():
            if not isinstance(name,str) or not np.isfinite(value) or value<0:raise ValueError('Invalid source bone weight')
            if value>0:influences[name]=influences.get(name,0)+float(amount)*value
    influences={name:value for name,value in influences.items() if value>1e-12}
    ranked=sorted(influences.items(),key=lambda item:item[1],reverse=True)
    total=sum(influences.values());retained=sum(value for _,value in ranked[:limit])
    if retained<=0:raise ValueError('No source skin weights at projected point')
    return {name:value/retained for name,value in ranked[:limit]},retained/total
