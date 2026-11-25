import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('rook_material_regions',Path(__file__).parents[1]/'experiments/2d_to_3d/rook_material_regions.py')
regions=importlib.util.module_from_spec(spec)
spec.loader.exec_module(regions)


def test_dark_scalp_selected_but_bright_forehead_and_front_eyebrows_retained():
    assert regions.region((0,0,1.76),(.15,.08,.04))==1
    assert regions.region((0,-.1,1.72),(.7,.4,.3))==0
    assert regions.region((0,-.14,1.66),(.1,.04,.02))==0


def test_jacket_preserves_shirt_hardware_and_lower_body():
    assert regions.region((-.3,-.05,1.3),(.15,.14,.13))==2
    assert regions.region((0,-.14,1.3),(.15,.14,.13))==0
    assert regions.region((.2,-.05,1.3),(1.,.25,.02))==0
    assert regions.region((-.2,0,.2),(.15,.14,.13))==0


@pytest.mark.parametrize('point,color',[((0,0),(.1,.1,.1)),((0,0,float('nan')),(.1,.1,.1)),((0,0,1.7),(2.,0,0))])
def test_invalid_inputs_rejected(point,color):
    with pytest.raises(ValueError):regions.region(point,color)
