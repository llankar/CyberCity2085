import importlib.util
from pathlib import Path
import pytest
p=Path(__file__).parents[1]/'experiments/2d_to_3d/blender/robot_hit.py'
spec=importlib.util.spec_from_file_location('robot_hit',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_hit_has_brief_peak_and_complete_recovery():
    assert m.recoil_amount(.2)==1
    assert all(0<=m.recoil_amount(i/100)<=1 for i in range(81))
    assert m.recoil_amount(-1)==m.recoil_amount(0)==m.recoil_amount(.8)==m.recoil_amount(2)==0

@pytest.mark.parametrize('t',[0,.2,.8])
def test_recoil_velocity_continuous_at_stages(t):
    h=1e-7
    assert abs(m.recoil_amount(t+h)-m.recoil_amount(t-h))/(2*h)<1e-4

@pytest.mark.parametrize('t',[float('nan'),float('inf')])
def test_nonfinite_rejected(t):
    with pytest.raises(ValueError):m.recoil_amount(t)
