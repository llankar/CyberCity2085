import importlib.util
from pathlib import Path
from datetime import datetime,timezone
import pytest

spec=importlib.util.spec_from_file_location('verify_benchmark_window',Path(__file__).parents[1]/'experiments/2d_to_3d/verify_benchmark_window.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    benchmark={'begin_utc_unix_s':100.,'end_utc_unix_s':105.,'seconds':5.,'rendered_frames':300,'rendered_frames_per_s':60.,'frame_post_draw_interval_p95_ms':17.}
    window={'samples':[{'utc':datetime.fromtimestamp(t,timezone.utc).isoformat(),'global_used_mib':2000+t,'godot_process_ids':[42] if 100<=t<=105 else []} for t in (99,101,102,103,106)]}
    return benchmark,window


def test_uses_only_live_samples_inside_actual_render_interval():
    benchmark,window=fixture()
    result=module.summarize(benchmark,window)
    assert result['overlapping_gpu_samples']==3
    assert result['observed_global_gpu_min_mib']==2101
    assert result['observed_global_gpu_max_mib']==2103


@pytest.mark.parametrize('defect',['outside','no_process','out_of_order','wrong_rate','wrong_duration','nan'])
def test_rejects_false_or_insufficient_benchmark_evidence(defect):
    benchmark,window=fixture()
    if defect=='outside': benchmark.update(begin_utc_unix_s=200,end_utc_unix_s=205)
    if defect=='no_process':
        for sample in window['samples']:sample['godot_process_ids']=[]
    if defect=='out_of_order':window['samples'].reverse()
    if defect=='wrong_rate':benchmark['rendered_frames_per_s']=300
    if defect=='wrong_duration':benchmark['seconds']=.5
    if defect=='nan':benchmark['rendered_frames_per_s']=float('nan')
    with pytest.raises(ValueError):module.summarize(benchmark,window)
