"""Private GLB texture-budget variants; mesh, skin and motion bytes stay exact."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image
from glb_document import Glb


def image_roles(doc):
    roles = {}
    def visit(value, key=''):
        if isinstance(value, dict):
            if 'index' in value and 'texture' in key.lower():
                role = 'normal' if 'normal' in key.lower() else ('color' if key in ('baseColorTexture', 'emissiveTexture') else 'data')
                texture = doc['textures'][value['index']]
                ids = [texture['source']] if 'source' in texture else []
                if 'EXT_texture_webp' in texture.get('extensions', {}):
                    ids.append(texture['extensions']['EXT_texture_webp']['source'])
                for index in ids: roles.setdefault(index, set()).add(role)
            for name, child in value.items(): visit(child, name)
        elif isinstance(value, list):
            for child in value: visit(child, key)
    visit(doc.get('materials', []))
    if any(len(value) != 1 for value in roles.values()):
        raise ValueError('Shared image has incompatible semantic roles')
    return {i: next(iter(value)) for i, value in roles.items()}


def resize(image, size, role):
    """Filter color in linear light, packed data directly, normals as unit vectors."""
    rgba = np.asarray(image.convert('RGBA'), dtype=np.float32) / 255
    rgb, alpha = rgba[:, :, :3], rgba[:, :, 3:]
    if role == 'color':
        rgb = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4) * alpha
    elif role == 'normal': rgb = rgb * 2 - 1
    values = np.concatenate([rgb, alpha], axis=2)
    filtered = np.stack([np.asarray(Image.fromarray(values[:, :, c]).resize(size, Image.Resampling.LANCZOS)) for c in range(4)], axis=2)
    rgb, alpha = filtered[:, :, :3], np.clip(filtered[:, :, 3:], 0, 1)
    if role == 'color':
        rgb = np.clip(rgb / np.maximum(alpha, 1e-8), 0, 1)
        rgb = np.where(rgb <= .0031308, rgb * 12.92, 1.055 * rgb ** (1 / 2.4) - .055)
    elif role == 'normal':
        length = np.linalg.norm(rgb, axis=2, keepdims=True)
        rgb = np.where(length > 1e-8, rgb / np.maximum(length, 1e-8), np.array([0, 0, 1]))
        rgb = rgb * .5 + .5
    result = Image.fromarray(np.rint(np.clip(np.concatenate([rgb, alpha], axis=2), 0, 1) * 255).astype('uint8'))
    return result if 'A' in image.getbands() else result.convert('RGB')


def budget(source, maximum):
    if maximum < 16: raise ValueError('Texture limit too small')
    target = copy.deepcopy(source)
    roles = image_roles(source.doc)
    replacements, report = {}, []
    accessor_payloads = [source.values(i) for i in range(len(source.doc.get('accessors', [])))]
    for index, info in enumerate(source.doc.get('images', [])):
        if 'uri' in info: raise ValueError('Embedded images required')
        view_index = info['bufferView']; view = source.doc['bufferViews'][view_index]
        start = view.get('byteOffset', 0)
        raw = bytes(source.bin[start:start + view['byteLength']])
        image = Image.open(io.BytesIO(raw))
        before = image.size
        if max(before) > maximum:
            if index not in roles: raise ValueError('Unknown image role')
            ratio = maximum / max(before)
            after = tuple(max(1, round(v * ratio)) for v in before)
            result = resize(image, after, roles[index])
            output = io.BytesIO()
            # Retain WebP semantics for EXT_texture_webp sources; no lossy recompression.
            kind = 'WEBP' if info['mimeType'] == 'image/webp' else 'PNG'
            result.save(output, format=kind, lossless=True)
            replacements[view_index] = output.getvalue()
            target.doc['images'][index]['mimeType'] = 'image/webp' if kind == 'WEBP' else 'image/png'
        else: after = before
        report.append({'image': index, 'name': info.get('name'), 'role': roles.get(index), 'before': before, 'after': after})
    if any(a.get('bufferView') in replacements for a in source.doc.get('accessors', [])):
        raise ValueError('Image storage overlaps geometry accessor')
    packed = bytearray()
    for index, view in enumerate(target.doc['bufferViews']):
        old = source.doc['bufferViews'][index]; start = old.get('byteOffset', 0)
        payload = replacements.get(index, source.bin[start:start + old['byteLength']])
        packed.extend(b'\0' * (-len(packed) % 4))
        view['byteOffset'], view['byteLength'] = len(packed), len(payload)
        packed.extend(payload)
    target.bin = packed
    assert all(target.values(i) == value for i, value in enumerate(accessor_payloads))
    return target, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--maximum', type=int, default=1024)
    args = parser.parse_args()
    root = Path('E:/CyberCity2085-3d-lab/generated/phase2')
    source_path = root / 'amjviz_actions146/human_actions.glb'
    out = root / f'amjviz_budget147_{args.maximum}'; out.mkdir(exist_ok=True)
    target, images = budget(Glb(source_path), args.maximum)
    destination = out / 'human_actions.glb'; target.save(destination)
    report = {'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
              'variant_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
              'source_bytes': source_path.stat().st_size, 'variant_bytes': destination.stat().st_size,
              'maximum': args.maximum, 'images': images, 'accessor_bytes_exact': True,
              'scope': 'Texture-only private variant; native import and visual comparison still required'}
    (out / 'texture_budget.json').write_text(json.dumps(report, indent=2))
    (out / 'CREDITS.txt').write_bytes((root / 'amjviz_actions146/CREDITS_equipped.txt').read_bytes())
    print('TEXTURE_BUDGET_VARIANT_READY', destination)


if __name__ == '__main__': main()
