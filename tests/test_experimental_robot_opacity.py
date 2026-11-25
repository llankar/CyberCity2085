import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('robot_opacity',Path(__file__).parents[1]/'experiments/2d_to_3d/robot_opacity.py')
opacity=importlib.util.module_from_spec(spec);spec.loader.exec_module(opacity)


def data():
    return {'materials':[{'name':'hull','alphaMode':'BLEND','doubleSided':True},
                         {'name':'decal','alphaMode':'BLEND'}],'meshes':[{'name':'untouched'}]}, {'objects':[
        {'baked_materials':['hull'],'all_adapter_alpha_constant_one':True,'documented_opaque_visor_approximation':False},
        {'baked_materials':['decal'],'all_adapter_alpha_constant_one':False,'documented_opaque_visor_approximation':False}]}


def test_only_source_proven_alpha_is_changed_and_input_is_not_modified():
    doc,report=data();new,changed=opacity.restore(doc,report)
    assert changed==['hull']
    assert new['materials'][1]==doc['materials'][1]
    assert new['materials'][0]=={'name':'hull','alphaMode':'OPAQUE','doubleSided':True}
    assert new['meshes']==doc['meshes']
    assert doc['materials'][0]['alphaMode']=='BLEND'


def test_incompatible_source_mapping_fails_instead_of_guessing():
    doc,report=data();report['objects'][0]['baked_materials']=['missing']
    with pytest.raises(ValueError,match='mapping'):opacity.restore(doc,report)


def test_documented_visor_contract_is_distinct_from_unresolved_alpha():
    doc,report=data();report['objects'][1]['documented_opaque_visor_approximation']=True
    assert opacity.restore(doc,report)[1]==['hull','decal']
