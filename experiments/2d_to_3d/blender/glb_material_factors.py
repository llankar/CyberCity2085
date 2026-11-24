"""Apply explicit standard glTF color factors while preserving binary chunks."""
import json
import struct


def apply_material_factors(path, factors):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from('<III', data)
    assert magic == 0x46546C67 and version == 2 and length == len(data)
    size, kind = struct.unpack_from('<II', data, 12)
    assert kind == 0x4E4F534A
    document = json.loads(data[20:20 + size])
    changed = []
    for material in document.get('materials', []):
        for pattern, factor in factors.items():
            if pattern in material.get('name', ''):
                assert len(factor) == 4 and all(0 <= x <= 1 for x in factor)
                material.setdefault('pbrMetallicRoughness', {})['baseColorFactor'] = factor
                changed.append(material['name'])
    if not changed:
        raise ValueError('No matching exported materials')
    encoded = json.dumps(document, separators=(',', ':')).encode('utf-8')
    encoded += b' ' * (-len(encoded) % 4)
    tail = data[20 + size:]
    result = struct.pack('<III', magic, version, 20 + len(encoded) + len(tail))
    result += struct.pack('<II', len(encoded), kind) + encoded + tail
    path.write_bytes(result)
    return changed
