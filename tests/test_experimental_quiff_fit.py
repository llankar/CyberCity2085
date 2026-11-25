import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('quiff_fit',Path(__file__).parents[1]/'experiments/2d_to_3d/quiff_fit.py')
hair=importlib.util.module_from_spec(spec);spec.loader.exec_module(hair)


def test_fit_preserves_front_and_height_and_moves_back_toward_scalp():
    for y in (-.08,0,.045):
        assert hair.fit_point((0,y,1.8))[1:]==(y,1.8)
    fitted=hair.fit_point((.08,.16,1.7))
    assert .045<fitted[1]<.16 and fitted[2]==1.7
    assert abs(fitted[0]+.0037)<abs(.08+.0037)


def test_fit_is_continuous_at_posterior_transition():
    left=hair.fit_point((0,.045-1e-8,1.7))
    right=hair.fit_point((0,.045+1e-8,1.7))
    assert abs(left[1]-right[1])<2e-8


@pytest.mark.parametrize('point',[(0,float('nan'),1.7),(0,1)])
def test_invalid_hair_coordinates_rejected(point):
    with pytest.raises(ValueError):hair.fit_point(point)
