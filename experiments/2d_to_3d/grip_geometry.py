"""Measured grip frames; rejects degenerate landmarks rather than guessing axes."""
import numpy as np


def circle_center(points):
    points=np.asarray(points,dtype=float)
    if points.shape!=(3,3) or not np.isfinite(points).all(): raise ValueError('Three finite landmarks required')
    a,b=points[1]-points[0],points[2]-points[0]
    normal=np.cross(a,b); square=float(normal@normal)
    if square<1e-16: raise ValueError('Finger landmarks are collinear')
    return points[0]+((a@a)*np.cross(b,normal)+(b@b)*np.cross(normal,a))/(2*square)


def grip_frame(centers,forearm,wrist):
    centers=np.asarray(centers,dtype=float)
    if centers.shape!=(3,3): raise ValueError('Middle/ring/pinky centers required')
    up=centers[0]-centers[2]
    if np.linalg.norm(up)<1e-5: raise ValueError('Grip axis collapsed')
    forward=np.asarray(wrist,dtype=float)-np.asarray(forearm,dtype=float)
    if np.linalg.norm(forward)<1e-5: raise ValueError('Forearm axis collapsed')
    forward/=np.linalg.norm(forward)
    # Aim follows the measured forearm. Finger curl centers are an up hint;
    # their oblique alignment must not tilt the barrel away from the arm.
    up-=forward*(forward@up)
    if np.linalg.norm(up)<1e-5: raise ValueError('Forward axis parallel to grip')
    up/=np.linalg.norm(up)
    right=np.cross(-forward,up); right/=np.linalg.norm(right)
    up=np.cross(right,-forward)
    basis=np.column_stack((right,-forward,up))
    if not np.allclose(basis.T@basis,np.eye(3),atol=1e-8) or np.linalg.det(basis)<.999999:
        raise ValueError('Invalid grip frame')
    return centers.mean(axis=0),basis
