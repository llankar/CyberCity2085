import importlib.util
from pathlib import Path
import math
import pytest
p=Path(__file__).parents[1]/'experiments/2d_to_3d/blender/robot_shutdown.py'
spec=importlib.util.spec_from_file_location('robot_shutdown',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_shutdown_buckles_before_fall_and_remains_settled():
    assert m.shutdown_pose(-1)==m.shutdown_pose(0)
    assert m.shutdown_pose(.2)['buckle']>0 and m.shutdown_pose(.2)['fall_angle']==0
    assert m.shutdown_pose(1.25)==m.shutdown_pose(10)
    assert m.shutdown_pose(2)['fall_angle']==math.pi/2
    assert m.shutdown_pose(2)['settled']

def test_angles_and_buckle_monotonic_and_bounded():
    samples=[m.shutdown_pose(i/100) for i in range(201)]
    for key,maximum in [('buckle',1),('fall_angle',math.pi/2),('head_tilt',.2)]:
        values=[s[key] for s in samples]
        assert min(values)>=0 and max(values)<=maximum
        assert all(a<=b for a,b in zip(values,values[1:]))

@pytest.mark.parametrize('time_s',[0,.3,.4,1.25])
def test_shutdown_stage_velocity_has_no_jump(time_s):
    h=1e-7
    for k in ['buckle','fall_angle','head_tilt']:
        left=(m.shutdown_pose(time_s)[k]-m.shutdown_pose(time_s-h)[k])/h
        right=(m.shutdown_pose(time_s+h)[k]-m.shutdown_pose(time_s)[k])/h
        assert abs(left-right)<1e-4

@pytest.mark.parametrize('bad',[math.nan,math.inf])
def test_nonfinite_time_rejected(bad):
    with pytest.raises(ValueError):m.shutdown_pose(bad)
