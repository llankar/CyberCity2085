import importlib.util
import json
from pathlib import Path
import struct
import pytest

spec = importlib.util.spec_from_file_location('compact_glb', Path(__file__).parents[1] / 'experiments/2d_to_3d/compact_glb.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture(extension=None):
    doc = {'asset': {'version': '2.0'}, 'buffers': [{'byteLength': 12}],
           'bufferViews': [{'buffer': 0, 'byteLength': 3, 'byteOffset': 0},
                           {'buffer': 0, 'byteLength': 3, 'byteOffset': 4},
                           {'buffer': 0, 'byteLength': 4, 'byteOffset': 8, 'target': 34962}],
           'images': [{'bufferView': 0, 'mimeType': 'image/png'}, {'bufferView': 1, 'mimeType': 'image/png'}]}
    if extension:
        doc['extensionsUsed'] = [extension]
    js = json.dumps(doc).encode(); js += b' ' * (-len(js) % 4)
    binary = b'abc\0abc\0mesh'
    return struct.pack('<4sII', b'glTF', 2, 28 + len(js) + len(binary)) + struct.pack('<II', len(js), 0x4e4f534a) + js + struct.pack('<II', len(binary), 0x004e4942) + binary


def test_duplicate_images_alias_exact_bytes_and_geometry_stays_intact():
    output, report = mod.compact(fixture())
    doc, binary = mod.unpack(output)
    assert report['duplicate_views'] == 1
    assert doc['bufferViews'][0]['byteOffset'] == doc['bufferViews'][1]['byteOffset'] == 0
    assert doc['bufferViews'][2]['byteOffset'] % 4 == 0
    assert binary[doc['bufferViews'][2]['byteOffset']:][:4] == b'mesh'
    assert doc['images'][1]['bufferView'] == 1


def test_compaction_is_idempotent():
    once, _ = mod.compact(fixture('KHR_materials_clearcoat'))
    twice, _ = mod.compact(once)
    assert once == twice


def test_unknown_offset_extensions_are_rejected():
    with pytest.raises(ValueError, match='Extension'):
        mod.compact(fixture('EXT_meshopt_compression'))


def test_truncated_glb_is_rejected():
    with pytest.raises(ValueError, match='header'):
        mod.compact(fixture()[:-1])
