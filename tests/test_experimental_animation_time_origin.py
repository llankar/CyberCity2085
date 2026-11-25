import importlib.util,struct,sys
from pathlib import Path
import pytest

folder=Path(__file__).parents[1]/'experiments/2d_to_3d'
def module(name):
    spec=importlib.util.spec_from_file_location(name,folder/(name+'.py'))
    loaded=importlib.util.module_from_spec(spec);spec.loader.exec_module(loaded);return loaded
Glb=module('glb_document').Glb
normalize=module('animation_time_origin').normalize_origins

def empty():
    g=Glb.__new__(Glb);g.bin=bytearray();g.doc={'buffers':[{'byteLength':0}], 'bufferViews':[],'accessors':[]}
    return g

def test_shared_input_is_copied_per_clip_and_pose_payload_unchanged():
    g=empty();shared=g.add_floats([1,2],2);earlier=g.add_floats([0,1],2)
    pose=g.add_floats([10,20],2);before=bytes(g.bin)
    g.doc['animations']=[{'name':'A','samplers':[{'input':shared,'output':pose}]},
                         {'name':'B','samplers':[{'input':shared,'output':pose},{'input':earlier,'output':pose}]}]
    report=normalize(g)
    a,b=g.doc['animations']
    assert struct.unpack('<2f',g.values(a['samplers'][0]['input']))==(0,1)
    assert struct.unpack('<2f',g.values(b['samplers'][0]['input']))==(1,2)
    assert bytes(g.bin[:len(before)])==before
    assert g.values(pose)==struct.pack('<2f',10,20)
    assert report['A']['duration_s']==1 and report['B']['duration_s']==2

@pytest.mark.parametrize('values',[[1,1],[float('nan'),2]])
def test_invalid_times_rejected(values):
    g=empty();i=g.add_floats(values,2);g.doc['animations']=[{'samplers':[{'input':i}]}]
    with pytest.raises(ValueError):normalize(g)
