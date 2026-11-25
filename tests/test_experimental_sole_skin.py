import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('sole162',Path(__file__).parents[1]/'experiments/2d_to_3d/sole_skin_weights162.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def test_preserves_total_and_other_influences():
    old={'foot':.65,'toe':.1,'shin':.2,'other':.05}
    new=module.redistribute(old,{'foot','toe'},{'shin'})
    assert sum(new.values())==pytest.approx(sum(old.values()))
    assert new['shin']==pytest.approx(.14) and new['other']==old['other']
    assert new['foot']/new['toe']==pytest.approx(old['foot']/old['toe'])

def test_requires_existing_foot_influence():
    with pytest.raises(ValueError):module.redistribute({'shin':1},{'foot'},{'shin'})

@pytest.mark.parametrize('value',[-.1,float('nan'),float('inf')])
def test_invalid_weights_rejected(value):
    with pytest.raises(ValueError):module.redistribute({'foot':1,'shin':value},{'foot'},{'shin'})
