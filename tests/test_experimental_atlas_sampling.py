import importlib.util
from pathlib import Path
import pytest
p=Path(__file__).parents[1]/'experiments/2d_to_3d/atlas_sampling.py'
spec=importlib.util.spec_from_file_location('atlas_sampling',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


@pytest.mark.parametrize('duration,loop,expected',[(23/24,True,23),(76/120,False,17),(1.,False,25),(2.4,False,59)])
def test_realtime_resampling_retains_exact_duration(duration,loop,expected):
    count=m.realtime_sample_count(duration,loop=loop)
    assert count==expected
    frames=m.atlas_sample_frames(5,5+duration*120,loop=loop,count=count)
    fps=(count if loop else count-1)/duration
    assert fps>=24-1e-8
    assert frames[0]==5
    assert frames[-1]<5+duration*120 if loop else frames[-1]==pytest.approx(5+duration*120)


def test_static_posture_is_not_invented_high_frequency_motion():
    assert m.realtime_sample_count(.00004,static_pose=True)==2


@pytest.mark.parametrize('duration,rate',[(0,24),(-1,24),(float('nan'),24),(1,0)])
def test_invalid_realtime_sampling_rejected(duration,rate):
    with pytest.raises(ValueError):m.realtime_sample_count(duration,minimum_fps=rate)

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


@pytest.mark.parametrize('last,loop,count',[(48,True,48),(24,True,24),(18,False,19),(24,False,25),(58,False,59)])
def test_full_cadence_action_sheets_preserve_native_keys_and_loop_endpoint(last,loop,count):
    frames=m.atlas_sample_frames(0,last,loop=loop,count=count)
    assert frames==list(range(last+(0 if loop else 1)))
    if not loop:assert frames[-1]==last
    else:assert frames[-1]<last
