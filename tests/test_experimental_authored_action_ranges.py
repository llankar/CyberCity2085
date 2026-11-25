import importlib.util
from pathlib import Path
import pytest
p=Path(__file__).parents[1]/'experiments/2d_to_3d/authored_action_ranges.py'
s=importlib.util.spec_from_file_location('authored_action_ranges',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def test_real_run_fps_not_silently_replaced_by_walk_fps():
 r=m.source_action_ranges('walk:0:70:60\nrun:0:90:120\npose:0:0:60')
 assert (r['run']['last']-r['run']['first'])/r['run']['fps']==.75
 assert r['walk']['fps']==60 and r['pose']['last']==0

def test_optional_loop_and_negative_preroll_preserved():
 r=m.source_action_ranges('# authored\nwalk:-10:70:60:1\nattack:0:16:60:0')
 assert r['walk']['first']==-10 and r['walk']['loop'] and not r['attack']['loop']

@pytest.mark.parametrize('text',['walk:0:70:0','walk:0:70:nan','walk:70:0:60','walk:0:1:60\nwalk:0:1:60','walk:0:1:60:maybe'])
def test_invalid_export_contract_rejected(text):
 with pytest.raises(ValueError):m.source_action_ranges(text)
