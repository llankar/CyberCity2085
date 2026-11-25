import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('vehicle_paint',Path(__file__).parents[1]/'experiments/2d_to_3d/vehicle_paint.py')
paint=importlib.util.module_from_spec(spec);spec.loader.exec_module(paint)


def test_original_maps_are_deterministic_and_have_distinct_pbr_channels():
    a,b=paint.maps(128),paint.maps(128)
    assert set(a)=={'basecolor','roughness','metallic'}
    for key in a:
        assert a[key].tobytes()==b[key].tobytes()
        assert a[key].size==(128,128)
    assert a['basecolor'].mode=='RGB'
    assert a['metallic'].getextrema()==(20,240)
    assert a['roughness'].getextrema()==(100,145)


def test_small_texture_rejected_before_invalid_scratch_random_range():
    with pytest.raises(ValueError):paint.maps(8)
