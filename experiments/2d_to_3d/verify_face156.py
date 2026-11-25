"""Verify face material study has exactly one declared change; not artistic approval."""
import copy
import hashlib
import json
from pathlib import Path
from glb_document import Glb


def verify_change(source, candidate):
    assert bytes(source.bin) == bytes(candidate.bin), 'Geometry/image/animation buffer changed'
    expected = copy.deepcopy(source.doc)
    materials = [m for m in expected['materials'] if m.get('name') == 'Body']
    assert len(materials) == 1 and 'normalTexture' in materials[0]
    materials[0]['normalTexture']['scale'] = .35
    if 'buffers' in expected:
        # Glb.save canonicalizes declared buffer length to the existing padded BIN.
        assert len(expected['buffers']) == 1
        expected['buffers'][0]['byteLength'] = len(source.bin)
    assert expected == candidate.doc, 'Undeclared document/material change'


def main():
    root = Path('E:/CyberCity2085-3d-lab/generated/phase2')
    folder = root / 'face_review156'
    source_path = root / 'amjviz_wardrobe150/human_actions.glb'
    candidate_path = folder / 'human_face035.glb'
    verify_change(Glb(source_path), Glb(candidate_path))
    captures = {}
    for name in ('source_front', 'normal_off', 'metal_off', 'candidate_front', 'candidate_side', 'candidate_back'):
        path = folder / (name + '.png')
        assert path.stat().st_size > 1000
        captures[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    report = {'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
              'candidate_sha256': hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
              'sole_change': 'Body.normalTexture.scale=0.35', 'binary_payload_exact': True,
              'captures_sha256': captures, 'artistic_acceptance': 'NOT VERIFIED'}
    (folder / 'verification.json').write_text(json.dumps(report, indent=2))
    print('FACE_MATERIAL156_VERIFIED sole_document_change exact_binary_payload six_captures')

if __name__ == '__main__': main()
