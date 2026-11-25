import importlib.util
from pathlib import Path
import numpy as np
import pytest

spec=importlib.util.spec_from_file_location('garment_alignment',Path(__file__).parents[1]/'experiments/2d_to_3d/garment_alignment.py')
align=importlib.util.module_from_spec(spec);spec.loader.exec_module(align)


def test_longitudinal_fit_does_not_triple_garment_circumference():
    matrix=np.array(align.axial_segment_transform((0,0,0),(0,0,.1),(0,0,0),(0,0,.3),1.1))
    assert matrix@np.array([0,0,.1,1])==pytest.approx([0,0,.3,1])
    assert matrix@np.array([.05,0,0,1])==pytest.approx([.055,0,0,1])


def test_rotated_axis_preserves_both_joint_endpoints():
    matrix=np.array(align.axial_segment_transform((1,2,3),(1,2,4),(5,6,7),(7,6,7),.9))
    assert matrix@np.array([1,2,3,1])==pytest.approx([5,6,7,1])
    assert matrix@np.array([1,2,4,1])==pytest.approx([7,6,7,1])
    assert np.linalg.norm((matrix@np.array([2,2,3,1]))[:3]-[5,6,7])==pytest.approx(.9)


def test_invalid_circumference_is_not_silently_applied():
    for scale in (-1,0,float('nan')):
        with pytest.raises(ValueError):align.axial_segment_transform((0,0,0),(0,0,1),(0,0,0),(0,0,1),scale)
