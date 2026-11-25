import importlib.util
from pathlib import Path
import numpy as np
import pytest

spec=importlib.util.spec_from_file_location('finger_ik',Path(__file__).parents[1]/'experiments/2d_to_3d/finger_ik.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('distance',[.045,.06,.09,.104])
def test_exact_target_without_stretch_or_excess_bend(distance):
    lengths=np.array([.041,.033,.030])
    target=np.array([0,distance,0])
    directions=module.segment_directions(lengths,target,[1,0,0])
    np.testing.assert_allclose(np.linalg.norm(directions,axis=1),1,atol=1e-10)
    np.testing.assert_allclose((directions*lengths[:,None]).sum(axis=0),target,atol=1e-8)
    angles=np.degrees(np.arccos(np.clip((directions[:-1]*directions[1:]).sum(axis=1),-1,1)))
    assert angles[0] <= 95+1e-6 and angles[1] <= 75+1e-6


@pytest.mark.parametrize('target,normal',[([0,.01,0],[1,0,0]),([0,.2,0],[1,0,0]),([0,.06,0],[0,1,0]),([0,float('nan'),0],[1,0,0])])
def test_rejects_impossible_or_ambiguous_fit(target,normal):
    with pytest.raises(ValueError):module.segment_directions([.041,.033,.03],target,normal)
