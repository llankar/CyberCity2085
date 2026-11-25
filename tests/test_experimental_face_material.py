import copy
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest
folder=Path(__file__).parents[1]/'experiments/2d_to_3d'
sys.path.insert(0,str(folder))
spec=importlib.util.spec_from_file_location('face156',folder/'verify_face156.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def pair():
    source=SimpleNamespace(bin=b'protected geometry and images',doc={'materials':[{'name':'Body','normalTexture':{'index':4}},{'name':'Other'}]})
    candidate=copy.deepcopy(source);candidate.doc['materials'][0]['normalTexture']['scale']=.35
    return source,candidate

def test_declared_material_change():module.verify_change(*pair())

def test_unrelated_material_change_rejected():
    source,candidate=pair();candidate.doc['materials'][1]['doubleSided']=True
    with pytest.raises(AssertionError,match='Undeclared'):module.verify_change(source,candidate)

def test_changed_geometry_or_texture_rejected():
    source,candidate=pair();candidate.bin=b'altered'
    with pytest.raises(AssertionError,match='buffer changed'):module.verify_change(source,candidate)
