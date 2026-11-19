"""8K promotion must retain surveyed obstacle coordinates and source trace data."""
import hashlib
import json
from pathlib import Path

from PIL import Image

from game.battle_maps import build_battle_map_catalog
from game.map_geometry import load_map_geometry
from tools.maps.refresh_geometry_metadata import refresh_geometry_metadata


def test_metadata_refresh_preserves_all_collision_data_and_does_not_mutate_input(tmp_path):
    image = tmp_path / 'restored.png'
    Image.new('RGB', (160, 90)).save(image)
    original = {'image': 'original.png', 'image_size': [40, 22],
                'image_sha256': 'old', 'grid': [40, 28], 'reviewed': True,
                'walls': [{'id': 'wall', 'cells': [[3, 4]],
                           'outline_uv': [[.1, .2], [.3, .2], [.3, .4]],
                           'blocks_sight': False}]}
    saved = json.loads(json.dumps(original))
    result = refresh_geometry_metadata(original, image)
    assert original == saved
    assert result['walls'] == saved['walls']
    assert result['grid'] == saved['grid']
    assert result['image_size'] == [160, 90]
    assert result['image_sha256'] == hashlib.sha256(image.read_bytes()).hexdigest()
    result['walls'][0]['cells'].append([4, 4])
    assert original == saved


def test_all_8k_maps_preserve_survey_and_trace_fingerprints():
    manifest = json.loads(Path('assets/maps/restoration_8k.json').read_text())
    records = {r['name']: r for r in manifest['maps']}
    fallbacks = set(manifest['resample_only_maps'])
    assert len(fallbacks) == 5
    entries = build_battle_map_catalog()
    assert len(records) == len(entries) == 122
    assert set(records) == {entry.filename for entry in entries}
    for entry in entries:
        path = Path(entry.path)
        record = records[path.name]
        expected = 'resample_only_generation_rejected' if path.name in fallbacks else 'image_restoration_then_resample'
        assert record['restoration_method'] == expected
        geometry = load_map_geometry(path)
        assert geometry, path.name
        with Image.open(path) as image:
            assert image.size[0] == 7680, path.name
            assert list(image.size) == geometry['image_size'] == record['target_size']
        assert geometry['image_sha256'] == record['output_sha256']
        walls_hash = hashlib.sha256(json.dumps(geometry['walls'], sort_keys=True).encode()).hexdigest()
        assert walls_hash == record['geometry_sha256'], path.name
        trace = path.with_suffix('.wall-traces.json')
        # The manifest records LF bytes; Git can materialize these JSON files as CRLF.
        trace_bytes = trace.read_bytes().replace(b'\r\n', b'\n')
        assert hashlib.sha256(trace_bytes).hexdigest() == record['trace_sha256'], path.name
        source_w, source_h = record['source_size']
        assert abs(record['target_size'][1] - source_h * 7680 / source_w) <= .5
