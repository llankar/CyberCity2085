import importlib.util
from pathlib import Path
import math
import pytest

spec=importlib.util.spec_from_file_location('cyborg_fire_motion',Path(__file__).parents[1]/'experiments/2d_to_3d/cyborg_fire_motion.py')
motion=importlib.util.module_from_spec(spec)
spec.loader.exec_module(motion)


def test_returns_to_exact_start_without_slide_displacement():
    assert motion.sample(0)==motion.sample(18)=={'raise':0.,'recoil':0.,'pitch_rad':0.,'slide_back_m':0.}


def test_single_peak_and_slide_travel():
    samples=[motion.sample(i/4) for i in range(73)]
    assert [i for i,value in enumerate(samples) if value['recoil']==1]==[32]
    assert motion.sample(8)['slide_back_m']==.02
    assert motion.sample(8)['pitch_rad']==-math.radians(4)
    assert all(0<=v['raise']<=1 and 0<=v['recoil']<=1 for v in samples)


@pytest.mark.parametrize('value',[-1,19,float('nan'),float('inf'),'8'])
def test_rejects_invalid_sampling(value):
    with pytest.raises(ValueError):motion.sample(value)
