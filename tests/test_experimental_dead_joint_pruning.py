import importlib.util,struct
from pathlib import Path
import pytest

folder=Path(__file__).parents[1]/'experiments/2d_to_3d'
def load(name):
    spec=importlib.util.spec_from_file_location(name,folder/(name+'.py'))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
Glb=load('glb_document').Glb
module=load('prune_dead_joints')

def fixture():
    g=Glb.__new__(Glb);g.bin=bytearray();g.doc={'buffers':[{'byteLength':0}],'accessors':[],'bufferViews':[]}
    ji=module.append_accessor(g,{'componentType':5123,'count':1,'type':'VEC4'},struct.pack('<4H',1,0,0,0))
    wi=g.add_floats([1,0,0,0],1,'VEC4');ib=g.add_floats(list(range(48)),3,'MAT4')
    time=g.add_floats([0,1],2);value=g.add_floats([0,0,0,1,0,0],2,'VEC3')
    g.doc.update(nodes=[{'children':[1,3,4]},{'name':'unused'},{'name':'weighted'},
                        {'name':'required_ancestor','children':[2]},{'mesh':0,'skin':0}],
                 scenes=[{'nodes':[0]}],skins=[{'joints':[1,2,3],'skeleton':0,'inverseBindMatrices':ib}],
                 meshes=[{'primitives':[{'attributes':{'JOINTS_0':ji,'WEIGHTS_0':wi}}]}],
                 animations=[{'name':'move','samplers':[{'input':time,'output':value}],
                              'channels':[{'sampler':0,'target':{'node':1,'path':'translation'}},
                                          {'sampler':0,'target':{'node':3,'path':'translation'}}]}])
    return g

def test_unweighted_ancestor_animation_and_exact_inverse_binds_are_retained():
    g=fixture();poses=g.values(g.doc['animations'][0]['samplers'][0]['output'])
    report=module.prune(g)
    assert report['output_skin_joints']==2 and report['removed_animation_channels']==1
    assert [n.get('name') for n in g.doc['nodes']]==[None,'weighted','required_ancestor',None]
    assert g.doc['nodes'][2]['children']==[1]
    assert g.doc['animations'][0]['channels'][0]['target']['node']==2
    assert g.values(g.doc['animations'][0]['samplers'][0]['output'])==poses
    assert struct.unpack('<32f',g.values(g.doc['skins'][0]['inverseBindMatrices']))==tuple(range(16,48))
    assert struct.unpack('<4H',g.values(g.doc['meshes'][0]['primitives'][0]['attributes']['JOINTS_0']))==(0,0,0,0)

def test_shared_joint_accessor_with_different_weight_masks_is_not_aliased():
    g=fixture();a=g.doc['meshes'][0]['primitives'][0]['attributes']
    other=g.add_floats([0,1,0,0],1,'VEC4')
    g.doc['meshes'][0]['primitives'].append({'attributes':{'JOINTS_0':a['JOINTS_0'],'WEIGHTS_0':other}})
    module.prune(g)
    first,second=[p['attributes'] for p in g.doc['meshes'][0]['primitives']]
    assert first['JOINTS_0']!=second['JOINTS_0']
    assert struct.unpack('<4H',g.values(first['JOINTS_0']))[0]==1
    assert struct.unpack('<4H',g.values(second['JOINTS_0']))[1]==0

def test_unknown_additional_skin_is_rejected():
    g=fixture();g.doc['skins'].append(g.doc['skins'][0].copy())
    with pytest.raises(ValueError):module.prune(g)
