"""Copy existing map references to E: without modifying production data."""
import hashlib
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[2]
output = Path('E:/CyberCity2085-3d-lab/sources/tactical_map')
output.mkdir(parents=True, exist_ok=True)
name = 'city_exterior_neon_market_alley'
manifest = {}
for suffix in ['.png', '.walls.json']:
    source = root / 'assets' / 'maps' / (name + suffix)
    target = output / source.name
    shutil.copy2(source, target)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert hashlib.sha256(target.read_bytes()).hexdigest() == digest
    manifest[source.name] = {'source': str(source), 'sha256': digest}
(output / 'provenance.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('TACTICAL_MAP_COPY_VERIFIED', len(manifest))
