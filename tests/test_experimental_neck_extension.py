import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('neck_extension',Path(__file__).parents[1]/'experiments/2d_to_3d/neck_extension.py')
neck=importlib.util.module_from_spec(spec);spec.loader.exec_module(neck)


def test_upper_facial_anatomy_stays_exact_and_extension_is_bounded():
    assert neck.extended_height(1.6)==1.6
    assert neck.extended_height(1.535)==1.535
    assert neck.extended_height(1.4884845)==pytest.approx(1.4434845)
    for z in (1.49,1.5,1.51,1.52):assert 0<=z-neck.extended_height(z)<=.045


def test_neck_extension_is_monotonic_and_cannot_reverse_vertical_vertex_order():
    values=[neck.extended_height(1.48+i*.001) for i in range(100)]
    assert all(b>a for a,b in zip(values,values[1:]))


def test_invalid_neck_bands_fail():
    with pytest.raises(ValueError):neck.extended_height(float('nan'))
    with pytest.raises(ValueError):neck.extended_height(1.5,bottom=2,top=1)
