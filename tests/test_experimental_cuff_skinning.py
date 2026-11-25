import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('cuff_skinning',Path(__file__).parents[1]/'experiments/2d_to_3d/cuff_skinning.py')
cuff=importlib.util.module_from_spec(spec);spec.loader.exec_module(cuff)


def test_palm_preserved_and_forearm_influence_bounded_monotonic():
    weights=[cuff.influence(i/1000) for i in range(-20,81)]
    assert weights==sorted(weights) and min(weights)==0 and max(weights)==1
    assert cuff.influence(0)==0 and cuff.influence(.05)==1
    assert cuff.influence(1e-7)<1e-8
    assert 1-cuff.influence(.05-1e-7)<1e-8


@pytest.mark.parametrize('distance,span',[(float('nan'),.05),(0,0),(0,-1),(0,float('inf'))])
def test_invalid_skinning_parameters_rejected(distance,span):
    with pytest.raises(ValueError):cuff.influence(distance,span)
