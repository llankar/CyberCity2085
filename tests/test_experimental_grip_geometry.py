import importlib.util
from pathlib import Path
import numpy as np
import pytest

source=Path(__file__).resolve().parents[1]/'experiments/2d_to_3d/grip_geometry.py'
spec=importlib.util.spec_from_file_location('grip_geometry',source)
grip=importlib.util.module_from_spec(spec); spec.loader.exec_module(grip)


def test_circle_center_is_rigid_transform_equivariant():
    points=np.array([[1,0,0],[0,1,0],[-1,0,0.]])
    rotation=np.array([[0,0,1],[1,0,0],[0,1,0.]])
    offset=np.array([3,-4,7.])
    assert np.allclose(grip.circle_center(points@rotation.T+offset),offset)


def test_collinear_fingers_refuse_fit():
    with pytest.raises(ValueError,match='collinear'): grip.circle_center([[0,0,0],[1,0,0],[2,0,0]])


def test_frame_preserves_grip_axis_and_weapon_forward():
    center,basis=grip.grip_frame([[0,0,.03],[0,0,0],[0,0,-.03]],[0,1,0],[0,0,0])
    assert np.allclose(center,0)
    assert np.allclose(basis@[0,-1,0],[0,-1,0])
    assert np.allclose(basis@[0,0,1],[0,0,1])
    assert np.linalg.det(basis)==pytest.approx(1)


def test_parallel_forearm_axis_refuses_fit():
    with pytest.raises(ValueError,match='parallel'):
        grip.grip_frame([[0,0,.03],[0,0,0],[0,0,-.03]],[0,0,-1],[0,0,0])


def test_oblique_finger_curl_does_not_redirect_barrel():
    _,basis=grip.grip_frame([[0,.02,.03],[0,0,0],[0,-.02,-.03]],[0,1,0],[0,0,0])
    assert np.allclose(basis@[0,-1,0],[0,-1,0])
