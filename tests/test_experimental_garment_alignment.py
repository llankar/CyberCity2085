import importlib.util
from pathlib import Path
import numpy as np
import pytest
spec=importlib.util.spec_from_file_location('garment_alignment',Path(__file__).parents[1]/'experiments/2d_to_3d/garment_alignment.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('target',[(0,2,0),(-2,0,0),(2,0,0),(1,2,3)])
def test_alignment_preserves_measured_endpoints_and_has_no_shear(target):
    a=np.array([.2,.3,.4]);b=a+[1,0,0];c=np.array([3.,-2.,1.]);d=c+target
    matrix=np.array(module.segment_transform(a,b,c,d));linear=matrix[:3,:3]
    np.testing.assert_allclose(matrix@[*a,1],[*c,1],atol=1e-12)
    np.testing.assert_allclose(matrix@[*b,1],[*d,1],atol=1e-12)
    np.testing.assert_allclose(linear.T@linear,np.eye(3)*np.dot(target,target),atol=1e-12)
    assert np.linalg.det(linear)>0

@pytest.mark.parametrize('bad',[(0,0,0),(float('nan'),0,1),(1,2)])
def test_bad_joint_measurements_rejected(bad):
    with pytest.raises(ValueError):module.segment_transform((0,0,0),(1,0,0),(0,0,0),bad)
