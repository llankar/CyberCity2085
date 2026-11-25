"""Verify actual current-human texture review evidence; never certify artistic quality."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path('E:/CyberCity2085-3d-lab/generated/phase2')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(root=ROOT):
    folder = root / 'texture_review155'
    variants = ('amjviz_wardrobe150', 'amjviz_budget154_1024')
    captures = []
    for variant in variants:
        for facing in ('front', 'side', 'back'):
            path = folder / f'{variant}_{facing}.png'
            with Image.open(path) as image:
                image.load()
                assert image.size == (1280, 720)
            captures.append({'file': path.name, 'sha256': digest(path), 'variant': variant, 'view': facing})
    source, budget = [json.loads((folder / f'{key}_benchmark.json').read_text()) for key in ('source', 'budget')]
    for result, variant in zip((source, budget), variants):
        assert result['human_glb_sha256'] == digest(root / variant / 'human_actions.glb')
        assert result['render_texture_size'] == [1280, 720]
        assert result['seconds'] >= 5 and result['rendered_frames'] > 0
    for key in ('robot_glb_sha256', 'facade_glb_sha256', 'max_draw_calls', 'godot_version'):
        assert source[key] == budget[key], key
    assert source['end_utc_unix_s'] < budget['begin_utc_unix_s'], 'Overlapping benchmark intervals'
    report = {'captures': captures, 'source': source, 'budget': budget,
              'engine_video_memory_reduction_bytes': source['engine_reported_video_bytes'] - budget['engine_reported_video_bytes'],
              'scope': 'Six real full-body native neutral captures; sequential five-second probes; no exclusive VRAM, long-run performance, face closeup or artistic acceptance'}
    (folder / 'review_evidence.json').write_text(json.dumps(report, indent=2))
    print('CURRENT_TEXTURE_REVIEW155_VERIFIED captures=6 sequential_probes=2')
    return report

if __name__ == '__main__':
    verify()
