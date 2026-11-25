import importlib.util,math
from pathlib import Path
import pytest
p=Path(__file__).parents[1]/'experiments/2d_to_3d/vehicle_motion.py'
s=importlib.util.spec_from_file_location('vehicle_motion',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def test_rotors_counterrotate_without_frame_aliasing():
    a=m.vehicle_motion('Rotor_Spin',1/30,1)[0];b=m.vehicle_motion('Rotor_Spin',1/30,-1)[0]
    assert a==-b and abs(a)>0
    assert abs(a/(math.tau/10)-round(a/(math.tau/10)))>.1
    assert m.vehicle_motion('Rotor_Spin',2,1)[0]==4*math.tau

@pytest.mark.parametrize('side',[-1,1])
def test_gear_retract_extend_are_continuous_opposites(side):
    assert m.vehicle_motion('Gear_Retract',0,side)[1]==0
    assert m.vehicle_motion('Gear_Extend',1,side)[1]==0
    for t in [0,.25,.5,.75,1]:
        assert math.isclose(m.vehicle_motion('Gear_Retract',t,side)[1],m.vehicle_motion('Gear_Extend',1-t,side)[1])

@pytest.mark.parametrize('clip,time,side',[('bad',0,1),('Rotor_Spin',math.nan,1),('Gear_Retract',0,0)])
def test_invalid_controls_rejected(clip,time,side):
    with pytest.raises(ValueError):m.vehicle_motion(clip,time,side)
