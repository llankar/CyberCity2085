import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('skin_normal_strength',Path(__file__).parents[1]/'experiments/2d_to_3d/skin_normal_strength.py')
skin=importlib.util.module_from_spec(spec);spec.loader.exec_module(skin)


def test_calibration_keeps_normal_image_and_other_materials_and_source_exact():
    source={'materials':[{'name':'sm004_head','normalTexture':{'index':3}},
                         {'name':'armor','normalTexture':{'index':4}}],'meshes':[{'name':'same'}]}
    result=skin.set_skin_strength(source,.35)
    assert result['materials'][0]['normalTexture']=={'index':3,'scale':.35}
    assert result['materials'][1]==source['materials'][1]
    assert result['meshes']==source['meshes']
    assert 'scale' not in source['materials'][0]['normalTexture']


def test_zero_or_invalid_values_cannot_silently_disable_detail():
    for value in (0,-1,float('nan'),float('inf'),2):
        with pytest.raises(ValueError):skin.set_skin_strength({'materials':[]},value)


def test_missing_source_texture_fails_instead_of_inventing_detail():
    with pytest.raises(ValueError):skin.set_skin_strength({'materials':[{'name':'sm004_head'}]},.35)
