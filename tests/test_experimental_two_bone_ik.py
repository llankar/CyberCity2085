import importlib.util
from pathlib import Path
import numpy as np
import pytest

spec=importlib.util.spec_from_file_location('two_bone_ik',Path(__file__).parents[1]/'experiments/2d_to_3d/two_bone_ik.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


@pytest.mark.parametrize('target', [[.1,.4,.1], [.2,.3,-.1], [-.3,.2,.1]])
def test_preserves_both_segment_lengths(target):
    shoulder = np.array([.04,0,0])
    elbow = module.elbow_target(shoulder,target,[0,0,-1],.28,.245)
    assert np.linalg.norm(elbow-shoulder) == pytest.approx(.28)
    assert np.linalg.norm(elbow-target) == pytest.approx(.245)


def test_pole_changes_bend_side_without_stretch():
    first = module.elbow_target([0,0,0],[0,.4,0],[0,0,-1],.28,.245)
    second = module.elbow_target([0,0,0],[0,.4,0],[0,0,1],.28,.245)
    assert first[2] == pytest.approx(-second[2])
    assert first[1] == pytest.approx(second[1])


@pytest.mark.parametrize('target,pole,upper,lower', [([0,.6,0],[0,0,1],.28,.245), ([0,0,0],[0,0,1],.28,.245), ([0,.4,0],[0,1,0],.28,.245), ([0,.4,0],[0,0,1],0,.245)])
def test_rejects_unreachable_or_ambiguous_input(target,pole,upper,lower):
    with pytest.raises(ValueError): module.elbow_target([0,0,0],target,pole,upper,lower)


def test_reachable_target_preserves_lengths_and_bend_side():
    s=np.array([0.,0.,0.]);e=np.array([.3,.4,0.]);w=np.array([.6,0.,0.]);t=np.array([.55,.1,.1])
    middle,end=module.solve(s,e,w,t)
    assert np.allclose(end,t)
    assert np.linalg.norm(middle-s)==pytest.approx(.5)
    assert np.linalg.norm(end-middle)==pytest.approx(.5)
    assert middle[1]>0


def test_unreachable_target_clamps_without_stretch():
    middle,end=module.solve([0,0,0],[.3,.4,0],[.6,0,0],[4,0,0])
    assert np.linalg.norm(middle)==pytest.approx(.5)
    assert np.linalg.norm(end-middle)==pytest.approx(.5)
    assert .99<end[0]<1


def test_straight_limb_has_finite_fallback_pole():
    middle,end=module.solve([0,0,0],[1,0,0],[2,0,0],[1,0,0])
    assert np.isfinite(middle).all() and np.isfinite(end).all()
    assert np.linalg.norm(middle)==pytest.approx(1)


def test_invalid_landmarks_rejected():
    with pytest.raises(ValueError):module.solve([0,0,0],[0,0,0],[1,0,0],[1,1,0])
    with pytest.raises(ValueError):module.solve([0,0,0],[1,0,0],[2,0,0],[float('nan'),0,0])
