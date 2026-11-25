import importlib.util
from pathlib import Path
import numpy as np
import pytest

spec=importlib.util.spec_from_file_location('pose_delta',Path(__file__).parents[1]/'experiments/2d_to_3d/pose_delta.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_reference_pose_reaches_target():
    q=[.5,.5,.5,.5];target=[0,0,1,0]
    position,rotation=module.additive_pose([1,2,3],q,[1,2,3],q,[4,5,6],target)
    assert np.allclose(position,[4,5,6])
    assert abs(np.dot(rotation,target))==pytest.approx(1)


def test_identity_delta_preserves_body_and_inputs():
    body=np.array([0.,1.,0.,0.]);original=body.copy()
    position,rotation=module.additive_pose([7,8,9],body,[1,2,3],[1,0,0,0],[1,2,3],[1,0,0,0])
    assert np.allclose(position,[7,8,9]) and np.allclose(rotation,body)
    assert np.array_equal(original,body)


def test_rotation_order_is_not_commutative():
    h=2**-.5
    _,rotation=module.additive_pose([0,0,0],[h,h,0,0],[0,0,0],[1,0,0,0],[0,0,0],[h,0,h,0])
    assert np.allclose(rotation,[.5,.5,.5,.5])


@pytest.mark.parametrize('quaternion',[[0,0,0,0],[2,0,0,0],[float('nan'),0,0,0],[1,0,0]])
def test_invalid_quaternions_fail(quaternion):
    with pytest.raises(ValueError):module.additive_pose([0,0,0],quaternion,[0,0,0],[1,0,0,0],[0,0,0],[1,0,0,0])


def test_invalid_position_fails():
    with pytest.raises(ValueError):module.additive_pose([0,float('inf'),0],[1,0,0,0],[0,0,0],[1,0,0,0],[0,0,0],[1,0,0,0])
