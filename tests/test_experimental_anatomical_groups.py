import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('anatomical_groups',Path(__file__).parents[1]/'experiments/2d_to_3d/anatomical_groups.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def test_mouth_included_by_ancestry_and_arms_excluded():
    parents={'torso':None,'neck':'torso','head':'neck','mouth_l':'head','jaw':'head','lips':'jaw','arm':'torso'}
    original=parents.copy()
    assert module.descendants(parents,'neck')=={'neck','head','mouth_l','jaw','lips'}
    assert parents==original

def test_names_do_not_imply_anatomy():
    assert module.descendants({'a':None,'b':'a','c':'b','fake_head':'a'},'b')=={'b','c'}

@pytest.mark.parametrize('parents,root',[({'a':None},'missing'),({'a':'b'},'a'),({'a':'a'},'a'),({'a':'b','b':'a'},'a')])
def test_invalid_hierarchy_fails(parents,root):
    with pytest.raises(ValueError):module.descendants(parents,root)
