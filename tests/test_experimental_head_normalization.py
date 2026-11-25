import importlib.util
from pathlib import Path
import numpy as np
import pytest

spec=importlib.util.spec_from_file_location('head_normalization',Path(__file__).parents[1]/'experiments/2d_to_3d/head_normalization.py')
head=importlib.util.module_from_spec(spec);spec.loader.exec_module(head)


def test_uniform_scan_scale_centers_xy_grounds_z_and_preserves_aspect():
    low=np.array([-2.,-1.,.1]);high=np.array([4.,3.,8.1])
    matrix=head.normalization(low,high)
    a=(matrix@np.r_[low,1])[:3];b=(matrix@np.r_[high,1])[:3]
    assert np.allclose((a+b)[:2]/2,0)
    assert abs(a[2])<1e-12 and abs(b[2]-.45)<1e-12
    assert np.allclose((b-a)/(high-low),.45/8)
    assert np.linalg.det(matrix[:3,:3])>0


@pytest.mark.parametrize('low,high,height',[([0,0,0],[1,1,0],.45),([0,0,0],[1,1,1],0),([0,0,float('nan')],[1,1,1],.45)])
def test_invalid_scan_bounds_rejected(low,high,height):
    with pytest.raises(ValueError):head.normalization(low,high,height)
