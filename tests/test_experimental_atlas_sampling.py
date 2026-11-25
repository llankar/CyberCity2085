import importlib.util
from pathlib import Path
import pytest
p=Path(__file__).parents[1]/'experiments/2d_to_3d/atlas_sampling.py'
spec=importlib.util.spec_from_file_location('atlas_sampling',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_imported_strip_offset_preserves_real_start_end_and_time():
    frames=m.atlas_sample_frames(1,37)
    assert frames==[1,13,25,37]
    assert [(f-1)/30 for f in frames]==[0,.4,.8,1.2]
    assert m.atlas_sample_frames(0,36)==[f-1 for f in frames]

def test_loop_avoids_duplicate_endpoint_without_changing_rate():
    assert m.atlas_sample_frames(1,61,loop=True)==[1,16,31,46]


def test_ten_fire_samples_include_recoil_peak_and_preserve_duration():
    frames=m.atlas_sample_frames(0,18,count=10)
    assert frames==list(range(0,19,2))
    assert 8 in frames
    assert (len(frames)-1)/(9/.75)==18/24

@pytest.mark.parametrize('first,last,count',[(1,1,4),(2,1,4),(0,float('inf'),4),(0,1,1)])
def test_invalid_clip_intervals_rejected(first,last,count):
    with pytest.raises(ValueError):m.atlas_sample_frames(first,last,count=count)
