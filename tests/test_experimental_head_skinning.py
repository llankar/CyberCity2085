import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('head_skinning',Path(__file__).parents[1]/'experiments/2d_to_3d/head_skinning.py')
head=importlib.util.module_from_spec(spec);spec.loader.exec_module(head)


def test_neck_to_skull_transition_is_normalized_bounded_and_monotonic():
    previous=0
    for i in range(200):
        neck,skull=head.neck_skull_weights(1.4+i*.003)
        assert 0<=neck<=1 and previous<=skull<=1
        assert neck+skull==pytest.approx(1)
        previous=skull
    assert head.neck_skull_weights(1.48)==(1,0)
    assert head.neck_skull_weights(1.60)==(0,1)


@pytest.mark.parametrize('height',[float('nan'),float('inf')])
def test_nonfinite_rest_height_rejected(height):
    with pytest.raises(ValueError):head.neck_skull_weights(height)
