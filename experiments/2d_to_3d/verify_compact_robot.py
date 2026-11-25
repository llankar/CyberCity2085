"""Verify five actual native renderer samples against the original robot GLB."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops
from compact_glb import compact

root = Path('E:/CyberCity2085-3d-lab/generated/phase2')
folder = root / 'security_compact134'
original = root / 'security_bundle01/robot_actions.glb'
candidate = folder / 'robot_actions.glb'
expected, report = compact(original.read_bytes())
assert candidate.read_bytes() == expected, 'Not the verified lossless derivative'
proofs = []
for clip in ('Idle', 'Walk', 'Melee', 'Hit', 'Death'):
    pictures = []
    hashes = {}
    for variant in ('source', 'compact'):
        log_bytes = (folder / f'{variant}_{clip}.log').read_bytes()
        log = log_bytes.decode('utf-16' if log_bytes.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig')
        assert f'CYBERCITY_IMPORTED_CLIP_SAMPLED {clip}' in log
        assert 'CYBERCITY_CAPTURE_RESULT 0' in log
        model = original if variant == 'source' else candidate
        assert f'CYBERCITY_GODOT_GLTF_OK {model.as_posix()}' in log
        path = folder / f'{variant}_{clip}.png'
        pictures.append(Image.open(path).convert('RGB'))
        hashes[variant] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert pictures[0].size == pictures[1].size
    difference = ImageChops.difference(*pictures)
    assert difference.getbbox() is None, f'Pixel mismatch: {clip}'
    proofs.append({'clip': clip, 'fraction': .5, 'pixels_exact': True, 'capture_sha256': hashes})
report.update(source_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
              output_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(), native_samples=proofs,
              limitations=['Five midpoint renders, not a new exhaustive motion proof',
                           'No VRAM or FPS improvement measured', 'No artistic acceptance inferred'])
(folder / 'native_compaction_validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('COMPACT_ROBOT_NATIVE_PIXELS_EXACT clips=5')
