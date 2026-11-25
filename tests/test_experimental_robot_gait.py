import importlib.util
from pathlib import Path
import pytest

path = Path(__file__).resolve().parents[1]/'experiments/2d_to_3d/blender/robot_gait.py'
spec = importlib.util.spec_from_file_location('robot_gait', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('side,start,end', [(0,.02,.70),(1,.62,1.30)])
def test_world_stance_foot_does_not_slide(side,start,end):
    # Side R has stance from .6 to 1.32 seconds in this cycle.
    positions=[]
    for i in range(21):
        travel,relative,height,stance=module.gait(start+(end-start)*i/20,side)
        assert stance and height==0
        positions.append(travel+relative)
    assert max(positions)-min(positions)<1e-12


def test_swing_clears_ground_and_lands_without_velocity_jump():
    assert module.gait(.96)[2]==pytest.approx(.1)
    for t in [.72,1.2]:
        eps=1e-6
        before=module.gait(t-eps); after=module.gait(t+eps)
        assert abs((sum(after[:2])-sum(before[:2]))/(2*eps))<1e-4
        assert before[2]<1e-10 and after[2]<1e-10


def test_forward_distance_and_invalid_parameters():
    assert module.gait(1.2)[0]==pytest.approx(-.6)
    with pytest.raises(ValueError): module.gait(0,duty=1)
