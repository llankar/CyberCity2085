import importlib.util
from pathlib import Path
import numpy as np
import pytest
spec=importlib.util.spec_from_file_location('cloth_clearance',Path(__file__).parents[1]/'experiments/2d_to_3d/cloth_clearance.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
points=np.array([[0.,0,0],[1,0,0],[2,0,0],[3,0,0]])
edges=[[0,1],[1,2]]

def test_uniform_translation_and_isolated_vertex_preserved():
    offsets=np.array([[1.,2,3]]*3+[[4,5,6]])
    np.testing.assert_allclose(m.smooth_fit_offsets(points,edges,offsets),offsets)

def test_correction_becomes_smooth_without_shrinking_original_surface():
    offsets=np.array([[0.,0,0],[0,0,1],[0,0,0],[0,0,0]])
    result=m.smooth_fit_offsets(points,edges,offsets)
    assert result[:3,2].max()-result[:3,2].min()<.001
    assert result[:3,2].min()>=0 and result[:3,2].max()<=1
    np.testing.assert_array_equal(offsets[1],[0,0,1])
    np.testing.assert_array_equal(result[:,:2],0)

def test_rigid_motion_equivariance():
    rotation=np.array([[0.,-1,0],[1,0,0],[0,0,1]])
    offsets=np.arange(12).reshape(4,3)/10
    actual=m.smooth_fit_offsets(points@rotation.T+3,edges,offsets@rotation.T)
    expected=m.smooth_fit_offsets(points,edges,offsets)@rotation.T
    np.testing.assert_allclose(actual,expected)

@pytest.mark.parametrize('bad',[[[0,4]], [[-1,0]], [[0,1,2]]])
def test_invalid_edges_rejected(bad):
    with pytest.raises(ValueError):m.smooth_fit_offsets(points,bad,np.zeros_like(points))
