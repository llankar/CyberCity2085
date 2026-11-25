import importlib.util
from pathlib import Path
import numpy as np
import pytest

spec=importlib.util.spec_from_file_location('neck_boundary_fit',Path(__file__).parents[1]/'experiments/2d_to_3d/neck_boundary_fit.py')
neck=importlib.util.module_from_spec(spec);spec.loader.exec_module(neck)


def test_boundary_requires_one_closed_loop_not_disconnected_or_branching_geometry():
    assert set(neck.closed_loop([(0,1),(1,2),(2,0)]))=={0,1,2}
    with pytest.raises(ValueError):neck.closed_loop([(0,1),(1,2)])
    with pytest.raises(ValueError):neck.closed_loop([(0,1),(1,2),(2,0),(3,4),(4,5),(5,3)])


def test_harmonic_extension_keeps_face_and_cross_section_exact():
    points=np.array([[0,0,1.55],[0,0,1.57],[0,0,1.65],[1,0,1.7]])
    result,drop=neck.fit_boundary(points,[(0,1),(1,2)],[0],1.43,protected=[2],radius=.06)
    assert result[:,:2]==pytest.approx(points[:,:2])
    assert result[0,2]==pytest.approx(1.43)
    assert drop[0]<drop[1]<drop[2]==0
    assert np.array_equal(result[2:],points[2:])


def test_protected_boundary_conflict_and_upward_target_are_rejected():
    points=[[0,0,1.5],[0,0,1.6]]
    with pytest.raises(ValueError):neck.fit_boundary(points,[(0,1)],[0],1.4,protected=[0])
    with pytest.raises(ValueError):neck.fit_boundary(points,[(0,1)],[0],1.7)


def test_neck_root_anchors_to_torso_without_inventing_bones():
    assert neck.neck_weights(1.43)=={'Spine02':1.,'neck':0.,'Head':0.}
    assert neck.neck_weights(1.6)=={'Spine02':0.,'neck':0.,'Head':1.}
    for height in np.linspace(1.42,1.61,100):
        weights=neck.neck_weights(height)
        assert sum(weights.values())==pytest.approx(1)
        assert min(weights.values())>=0
