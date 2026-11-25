"""Lossless experimental GLB buffer compaction; no mesh/material conversion."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct


def unpack(data):
    magic, version, length = struct.unpack_from('<4sII', data)
    if magic != b'glTF' or version != 2 or length != len(data):
        raise ValueError('Invalid GLB header')
    chunks = []
    cursor = 12
    while cursor < length:
        size, kind = struct.unpack_from('<II', data, cursor)
        cursor += 8
        if size % 4 or cursor + size > length:
            raise ValueError('Invalid chunk')
        chunks.append((kind, data[cursor:cursor + size]))
        cursor += size
    if [kind for kind, _ in chunks] != [0x4e4f534a, 0x004e4942]:
        raise ValueError('Only JSON + embedded BIN supported')
    return json.loads(chunks[0][1]), chunks[1][1]


def compact(data):
    original, binary = unpack(data)
    doc = copy.deepcopy(original)
    if len(doc.get('buffers', [])) != 1 or 'uri' in doc['buffers'][0]:
        raise ValueError('One embedded buffer required')
    if set(doc.get('extensionsUsed', [])) - {'KHR_materials_clearcoat'}:
        raise ValueError('Extension-specific binary offsets need a separate audit')
    packed = bytearray()
    offsets = {}
    duplicates = 0
    for view in doc.get('bufferViews', []):
        start = view.get('byteOffset', 0)
        size = view['byteLength']
        if view.get('buffer', 0) != 0 or start < 0 or size <= 0 or start + size > original['buffers'][0]['byteLength']:
            raise ValueError('Invalid buffer view')
        payload = binary[start:start + size]
        # Bytes are the key, not a hash: no possibility of hash-collision aliasing.
        if payload in offsets:
            duplicates += 1
        else:
            packed.extend(b'\0' * (-len(packed) % 4))
            offsets[payload] = len(packed)
            packed.extend(payload)
        view['byteOffset'] = offsets[payload]
    doc['buffers'][0]['byteLength'] = len(packed)
    encoded = json.dumps(doc, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    encoded += b' ' * (-len(encoded) % 4)
    packed.extend(b'\0' * (-len(packed) % 4))
    output = struct.pack('<4sII', b'glTF', 2, 28 + len(encoded) + len(packed))
    output += struct.pack('<II', len(encoded), 0x4e4f534a) + encoded
    output += struct.pack('<II', len(packed), 0x004e4942) + packed
    # Every referenced payload and every JSON property except offsets/length stays exact.
    result, result_bin = unpack(output)
    for before, after in zip(original.get('bufferViews', []), result.get('bufferViews', [])):
        a, b = before.get('byteOffset', 0), after['byteOffset']
        assert binary[a:a + before['byteLength']] == result_bin[b:b + after['byteLength']]
        after.pop('byteOffset')
        before.pop('byteOffset', None)
    result['buffers'][0]['byteLength'] = original['buffers'][0]['byteLength']
    assert original == result
    return output, {'duplicate_views': duplicates, 'source_bytes': len(data), 'output_bytes': len(output),
                    'saved_bytes': len(data) - len(output), 'payload_and_metadata_exact': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if any(p.resolve().drive.upper() != 'E:' for p in (args.source, args.output)) or args.source.resolve() == args.output.resolve():
        parser.error('Separate source/output on E: required')
    source = args.source.read_bytes()
    output, report = compact(source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)
    report.update(source_sha256=hashlib.sha256(source).hexdigest(), output_sha256=hashlib.sha256(output).hexdigest())
    args.output.with_suffix('.compaction.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))
