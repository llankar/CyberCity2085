import importlib.util
from pathlib import Path
import numpy as np

spec=importlib.util.spec_from_file_location('triangle_contact',Path(__file__).parents[1]/'experiments/2d_to_3d/triangle_contact.py')
contact=importlib.util.module_from_spec(spec);spec.loader.exec_module(contact)
tri=((0,0,0),(1,0,0),(0,1,0))


def test_finite_segment_reports_actual_triangle_crossing():
    assert np.allclose(contact.segment_hit((.2,.2,1),(.2,.2,-1),*tri),(.2,.2,0))


def test_ray_beyond_segment_or_outside_triangle_is_not_counted():
    assert contact.segment_hit((.2,.2,1),(.2,.2,.1),*tri) is None
    assert contact.segment_hit((2,2,1),(2,2,-1),*tri) is None


def test_parallel_and_coplanar_segments_are_explicitly_unresolved():
    assert contact.segment_hit((0,0,1),(1,0,1),*tri) is None
    assert contact.segment_hit((.1,.1,0),(.2,.1,0),*tri) is None
