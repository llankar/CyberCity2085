"""Correlate actual native render intervals with timestamped GPU-wide samples."""
from datetime import datetime
import hashlib
import json
import math
import argparse
from pathlib import Path


def summarize(benchmark,window):
    begin,end,seconds = [float(benchmark[key]) for key in ('begin_utc_unix_s','end_utc_unix_s','seconds')]
    frames = benchmark['rendered_frames']
    fps = float(benchmark['rendered_frames_per_s'])
    if not all(math.isfinite(value) for value in (begin,end,seconds,fps)) or not 5 <= seconds < 6 or end <= begin:
        raise ValueError('Invalid native render interval')
    if abs(end-begin-seconds) > .1 or type(frames) is not int or frames <= 0 or abs(fps-frames/seconds) > .0001:
        raise ValueError('Frame count, wall interval and rate disagree')
    selected = []
    previous = -math.inf
    for sample in window['samples']:
        date = datetime.fromisoformat(sample['utc'].replace('Z','+00:00'))
        if date.tzinfo is None:
            raise ValueError('GPU timestamps need a timezone')
        timestamp = date.timestamp()
        if timestamp <= previous or sample['global_used_mib'] < 0:
            raise ValueError('Invalid GPU sample chronology or memory')
        previous = timestamp
        if begin <= timestamp <= end and sample['godot_process_ids']:
            selected.append(sample)
    if len(selected) < 3:
        raise ValueError('Insufficient live-Godot GPU samples inside render interval')
    return {'overlapping_gpu_samples':len(selected),
            'observed_global_gpu_min_mib':min(s['global_used_mib'] for s in selected),
            'observed_global_gpu_max_mib':max(s['global_used_mib'] for s in selected),
            'godot_process_ids':sorted({pid for s in selected for pid in s['godot_process_ids']}),
            'rendered_frames_per_s':fps,'frame_post_draw_interval_p95_ms':benchmark['frame_post_draw_interval_p95_ms'],
            'scope':'Timestamp-correlated GPU-wide observations, not exclusive process allocation, guaranteed peak, GPU execution timing or artistic acceptance'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--folder',default='tactical_facades01')
    parser.add_argument('--batch',type=int,default=117)
    args=parser.parse_args()
    root = Path('E:/CyberCity2085-3d-lab/generated/phase2')
    folder = (root/args.folder).resolve()
    assert folder.is_relative_to(root.resolve()) and args.batch>0
    benchmark_path=folder/f'benchmark{args.batch}.json'
    gpu_path=folder/f'gpu{args.batch}.json'
    benchmark = json.loads(benchmark_path.read_text())
    window = json.loads(gpu_path.read_text(encoding='utf-8-sig'))
    for path_key,hash_key in [('human','human_glb_sha256'),('robot','robot_glb_sha256')]:
        path = Path(benchmark[path_key])
        assert path.resolve().is_relative_to(root.resolve())
        assert hashlib.sha256(path.read_bytes()).hexdigest() == benchmark[hash_key]
    assert hashlib.sha256((root/'tactical_facades01/facades.glb').read_bytes()).hexdigest() == benchmark['facade_glb_sha256']
    if 'vehicle' in benchmark:
        vehicle = Path(benchmark['vehicle']).resolve()
        assert vehicle.is_relative_to(root.resolve())
        assert hashlib.sha256(vehicle.read_bytes()).hexdigest() == benchmark['vehicle_glb_sha256']
    assert benchmark['logical_viewport_size'] == [1920.,1080.]
    assert benchmark['render_texture_size'] == [1920.,1080.]
    result = summarize(benchmark,window)
    result['source_benchmark_sha256'] = hashlib.sha256(benchmark_path.read_bytes()).hexdigest()
    result['source_gpu_window_sha256'] = hashlib.sha256(gpu_path.read_bytes()).hexdigest()
    (folder/f'verified_benchmark{args.batch}.json').write_text(json.dumps(result,indent=2))
    print('NATIVE_BENCHMARK_GPU_WINDOW_VERIFIED',json.dumps(result))


if __name__ == '__main__':main()
