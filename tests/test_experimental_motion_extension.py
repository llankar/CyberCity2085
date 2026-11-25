import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest
folder=Path(__file__).parents[1]/'experiments/2d_to_3d'
sys.path.insert(0,str(folder))
spec=importlib.util.spec_from_file_location('motion159',folder/'verify_motion_extension159.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def test_motion_signature_detects_output_change():
    clip={'channels':[{'target':{'node':0,'path':'rotation'},'sampler':0}], 'samplers':[{'input':0,'output':1}]}
    original=SimpleNamespace(doc={'nodes':[{'name':'head'}]},values=lambda index:[b'times',b'original rotations'][index])
    changed=SimpleNamespace(doc=original.doc,values=lambda index:[b'times',b'changed rotations'][index])
    assert module.channels(original,clip)!=module.channels(changed,clip)

def test_duplicate_named_target_rejected():
    clip={'channels':[{'target':{'node':0,'path':'rotation'},'sampler':0}]*2,'samplers':[{'input':0,'output':1}]}
    model=SimpleNamespace(doc={'nodes':[{'name':'head'}]},values=lambda index:b'fixture')
    with pytest.raises(AssertionError):module.channels(model,clip)
