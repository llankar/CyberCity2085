import copy,importlib.util
from pathlib import Path

folder=Path(__file__).parents[1]/'experiments/2d_to_3d'
def load(name):
    spec=importlib.util.spec_from_file_location(name,folder/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
Glb=load('glb_document').Glb
restore=load('game_materials').restore

def asset(materials,images):
    g=Glb.__new__(Glb);g.bin=bytearray();g.doc={'buffers':[{'byteLength':0}],'bufferViews':[],'accessors':[],
        'materials':materials,'images':[],'textures':[],'samplers':[]}
    for payload in images:
        g.doc['images'].append({'bufferView':len(g.doc['bufferViews']),'mimeType':'image/png'})
        g.doc['bufferViews'].append({'buffer':0,'byteOffset':len(g.bin),'byteLength':len(payload)});g.bin.extend(payload)
        g.doc['textures'].append({'source':len(g.doc['textures'])})
    return g

def test_nested_pbr_slots_are_remapped_and_unmatched_weapon_texture_is_preserved():
    target=asset([{'name':'Jacket','normalTexture':{'index':0}}, {'name':'Weapon','normalTexture':{'index':0}}],[b'weapon'])
    accessor=target.add_floats([1,2,3],1,'VEC3');geometry=target.values(accessor)
    source=asset([{'name':'Jacket','normalTexture':{'index':1},'extensions':{
        'KHR_materials_clearcoat':{'clearcoatTexture':{'index':0,'texCoord':1}}}}],[b'coat',b'normal'])
    old_doc=copy.deepcopy(source.doc);old_bin=bytes(source.bin)
    report=restore(target,source)
    assert target.values(accessor)==geometry and report['restored_materials']==['Jacket']
    assert target.doc['materials'][1]['normalTexture']['index']==0
    assert target.doc['materials'][0]['normalTexture']['index']==2
    assert target.doc['materials'][0]['extensions']['KHR_materials_clearcoat']['clearcoatTexture']=={'index':1,'texCoord':1}
    assert source.doc==old_doc and bytes(source.bin)==old_bin
    for image,payload in zip(target.doc['images'],[b'weapon',b'coat',b'normal']):
        view=target.doc['bufferViews'][image['bufferView']]
        assert target.bin[view['byteOffset']:view['byteOffset']+view['byteLength']]==payload

def test_webp_extension_image_reference_is_preserved_without_a_fallback_source():
    target=asset([{'name':'Jacket','normalTexture':{'index':0}}],[b'old'])
    source=asset([{'name':'Jacket','normalTexture':{'index':0}}],[b'webp'])
    source.doc['textures']=[{'extensions':{'EXT_texture_webp':{'source':0}}}]
    source.doc['extensionsUsed']=['EXT_texture_webp'];source.doc['extensionsRequired']=['EXT_texture_webp']
    restore(target,source)
    assert target.doc['textures']==[{'extensions':{'EXT_texture_webp':{'source':0}}}]
    assert target.doc['extensionsRequired']==['EXT_texture_webp']
