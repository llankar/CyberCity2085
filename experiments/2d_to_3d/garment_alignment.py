"""Measured segment alignment for authored garment rest-pose adaptation."""
import numpy as np


def segment_transform(source_head, source_child, target_head, target_child):
    """Similarity transform: align endpoints without introducing shear/reflection."""
    a,b,c,d=(np.asarray(p,dtype=float) for p in (source_head,source_child,target_head,target_child))
    if any(p.shape!=(3,) or not np.isfinite(p).all() for p in (a,b,c,d)):
        raise ValueError('Expected finite 3D joint positions')
    x=b-a;y=d-c;lx=np.linalg.norm(x);ly=np.linalg.norm(y)
    if min(lx,ly)<1e-8:raise ValueError('Degenerate measured segment')
    x/=lx;y/=ly;dot=np.clip(x@y,-1.,1.)
    cross=np.cross(x,y)
    if dot < -1+1e-10:
        axis=np.eye(3)[np.argmin(np.abs(x))];axis=np.cross(x,axis);axis/=np.linalg.norm(axis)
        rotation=2*np.outer(axis,axis)-np.eye(3)
    else:
        skew=np.array([[0,-cross[2],cross[1]],[cross[2],0,-cross[0]],[-cross[1],cross[0],0]])
        rotation=np.eye(3)+skew+(skew@skew)/(1+dot)
    result=np.eye(4);result[:3,:3]=rotation*(ly/lx);result[:3,3]=c-result[:3,:3]@a
    return result.tolist()


def landmark_warp(points, source_landmarks, target_landmarks):
    """3D polyharmonic interpolation with affine tail, for measured rest fitting."""
    p,s,t=(np.asarray(a,dtype=float) for a in (points,source_landmarks,target_landmarks))
    if any(a.ndim!=2 or a.shape[1]!=3 or not np.isfinite(a).all() for a in (p,s,t)) or s.shape!=t.shape or len(s)<4:
        raise ValueError('Finite matching landmark sets and Nx3 points required')
    affine=np.column_stack([np.ones(len(s)),s])
    if np.linalg.matrix_rank(affine)<4:raise ValueError('Landmarks must span 3D')
    distances=np.linalg.norm(s[:,None]-s[None,:],axis=2)
    if np.any((distances+np.eye(len(s)))<1e-9):raise ValueError('Duplicate landmarks')
    system=np.block([[distances,affine],[affine.T,np.zeros((4,4))]])
    coefficients=np.linalg.solve(system,np.vstack([t,np.zeros((4,3))]))
    return np.column_stack([np.linalg.norm(p[:,None]-s[None,:],axis=2),np.ones(len(p)),p])@coefficients
