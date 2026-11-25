import copy
import importlib.util
import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

folder = Path(__file__).parents[1] / 'experiments/2d_to_3d'
sys.path.insert(0, str(folder))
spec = importlib.util.spec_from_file_location('texture_budget', folder / 'texture_budget.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_color_filter_uses_linear_light():
    image = Image.fromarray(np.array([[[0, 0, 0], [255, 255, 255]]], dtype='uint8'))
    pixel = np.asarray(module.resize(image, (1, 1), 'color'))[0, 0, 0]
    assert 185 <= pixel <= 190  # sRGB midpoint is ~188, not128.


def test_normal_filter_renormalizes_and_retains_alpha():
    image = Image.fromarray(np.array([[[255, 128, 128, 64], [128, 128, 255, 192]]], dtype='uint8'))
    pixel = np.asarray(module.resize(image, (1, 1), 'normal'))[0, 0]
    vector = pixel[:3].astype(float) / 255 * 2 - 1
    assert abs(np.linalg.norm(vector) - 1) < .01
    assert 125 <= pixel[3] <= 130


def test_budget_preserves_source_and_animation_bytes(tmp_path):
    stream = io.BytesIO(); Image.new('RGB', (32, 16), 'red').save(stream, 'WEBP', lossless=True)
    raw = stream.getvalue()
    source = module.Glb.__new__(module.Glb)
    source.bin = bytearray(raw)
    source.doc = {'buffers': [{'byteLength': len(raw)}], 'bufferViews': [{'buffer': 0, 'byteOffset': 0, 'byteLength': len(raw)}],
                  'accessors': [], 'images': [{'bufferView': 0, 'mimeType': 'image/webp'}],
                  'textures': [{'extensions': {'EXT_texture_webp': {'source': 0}}}],
                  'materials': [{'pbrMetallicRoughness': {'baseColorTexture': {'index': 0}}}]}
    source.add_floats([1, 2, 3], 1, 'VEC3')
    old_doc, old_bytes = copy.deepcopy(source.doc), bytes(source.bin)
    target, report = module.budget(source, 16)
    assert source.doc == old_doc and bytes(source.bin) == old_bytes
    assert target.values(0) == source.values(0)
    path = tmp_path / 'variant.glb'; target.save(path)
    loaded = module.Glb(path)
    assert loaded.values(0) == source.values(0)
    assert report[0]['after'] == (16, 8)
    assert loaded.doc['textures'] == source.doc['textures']
    source.doc['materials'][0]['normalTexture'] = {'index': 0}
    with pytest.raises(ValueError, match='incompatible'): module.budget(source, 16)
