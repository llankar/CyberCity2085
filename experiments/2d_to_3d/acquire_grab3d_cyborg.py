"""Bounded acquisition of one publicly CC0 licensed rigged comparison asset."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen
from acquire_diesel_candidate import checked_glb

ROOT = Path('E:/CyberCity2085-3d-lab/sources/grab3d_cyborg')
PAGE = 'https://grab3d.com/models/characters/cyborg/'
MODEL = 'https://grab3d.com/dl/cyborg-rigged/cyborg-rigged.glb'


def fetch(url, limit):
    with urlopen(url, timeout=60) as response:
        payload = response.read(limit + 1)
    if len(payload) > limit:
        raise ValueError('Asset exceeds reviewed size limit')
    return payload


def main():
    ROOT.mkdir(exist_ok=True)
    page = fetch(PAGE, 2_000_000)
    license_text = fetch('https://grab3d.com/dl/cyborg/LICENSE.txt', 20_000)
    manifest = fetch('https://grab3d.com/dl/cyborg/manifest.json', 50_000)
    if b'CC0 1.0 Universal' not in license_text or b'AI-assisted' not in license_text:
        raise ValueError('Reviewed grant/origin changed; stop and reassess')
    if json.loads(manifest)['extras']['license'] != 'CC0-1.0':
        raise ValueError('Unexpected source license')
    data = fetch(MODEL, 32_000_000)
    digest = checked_glb(data)
    for name, payload in [('publisher.html', page), ('LICENSE.txt', license_text),
                          ('manifest.json', manifest), ('cyborg-rigged.glb', data)]:
        (ROOT / name).write_bytes(payload)
    (ROOT/'provenance.json').write_text(json.dumps({
        'publisher': PAGE, 'download': MODEL, 'sha256': digest, 'bytes': len(data),
        'license': 'CC0-1.0', 'origin': 'AI-assisted Meshy base; publisher Blender cleanup',
        'scope': 'One experimental candidate; source claims do not prove topology or art quality'}, indent=2), encoding='utf8')
    print('GRAB3D_CYBORG_ACQUIRED', len(data), digest)


if __name__ == '__main__':
    main()
