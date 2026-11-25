import importlib.util
from pathlib import Path
import numpy as np
import pytest
spec=importlib.util.spec_from_file_location('aim_geometry',Path(__file__).parents[1]/'experiments/2d_to_3d/aim_geometry.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('direction',[[1,2,3],[-1,-2,3],[0,1,-1],[0,1,0]])
def test_levels_direction_without_changing_heading(direction):
    q=module.horizontal_aim_correction(direction);v=np.array(direction,dtype=float);v/=np.linalg.norm(v)
    # Independent vector/quaternion rotation expression.
    rotated=v+2*np.cross(q[1:],np.cross(q[1:],v)+q[0]*v)
    expected=np.array([direction[0],direction[1],0.]);expected/=np.linalg.norm(expected)
    assert np.allclose(rotated,expected,atol=1e-12)
    assert np.linalg.norm(q)==pytest.approx(1)

@pytest.mark.parametrize('direction',[[0,0,0],[0,0,1],[float('nan'),1,0],[1,2]])
def test_no_guessed_heading_for_invalid_or_vertical_aim(direction):
    with pytest.raises(ValueError):module.horizontal_aim_correction(direction)
