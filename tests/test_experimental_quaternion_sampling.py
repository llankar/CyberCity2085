import importlib.util
from pathlib import Path
import numpy as np
import pytest

spec = importlib.util.spec_from_file_location('quaternion_sampling', Path(__file__).parents[1] / 'experiments/2d_to_3d/quaternion_sampling.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('fraction', [0, .25, .5, .75, 1])
def test_constant_angular_speed(fraction):
    angle = np.radians(140)
    end = [np.cos(angle / 2), 0, np.sin(angle / 2), 0]
    expected = [np.cos(angle * fraction / 2), 0, np.sin(angle * fraction / 2), 0]
    np.testing.assert_allclose(module.slerp([1,0,0,0], end, fraction), expected, atol=1e-12)
    np.testing.assert_allclose(module.slerp([1,0,0,0], -np.array(end), fraction), expected, atol=1e-12)


def test_antipodes_are_same_orientation():
    np.testing.assert_allclose(module.slerp([1,0,0,0], [-1,0,0,0], .25), [1,0,0,0])


@pytest.mark.parametrize('first,second,fraction', [([0,0,0,0],[1,0,0,0],.5), ([1,0,0,0],[1,0,0],.5), ([1,0,0,0],[1,0,0,0],1.1), ([1,0,0,0],[1,0,0,0],float('nan'))])
def test_rejects_invalid_input(first, second, fraction):
    with pytest.raises(ValueError): module.slerp(first, second, fraction)
