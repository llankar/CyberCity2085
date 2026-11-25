import importlib.util
from pathlib import Path
import pytest

path=Path(__file__).resolve().parents[1]/'experiments/2d_to_3d/blender/robot_strike.py'
spec=importlib.util.spec_from_file_location('robot_strike',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_attack_has_windup_forward_reach_and_recovery():
    windup=module.strike_offset(.32); contact=module.strike_offset(.5)
    assert windup[1]>0 and windup[2]>.3
    assert contact[1]<-.4 and contact[2]>.4
    assert module.strike_offset(0)==module.strike_offset(1)==(0,0,0)
    assert module.strike_offset(.55)==contact


@pytest.mark.parametrize('time_s',[0,.32,.5,.6,1])
def test_stage_boundaries_do_not_instantly_change_hand_velocity(time_s):
    epsilon=1e-7
    first=module.strike_offset(time_s-epsilon)
    second=module.strike_offset(time_s+epsilon)
    assert max(abs(a-b)/(2*epsilon) for a,b in zip(first,second))<1e-4


def test_nonloop_clip_holds_neutral_outside_its_time_interval():
    assert module.strike_offset(-4)==module.strike_offset(3)==(0,0,0)
