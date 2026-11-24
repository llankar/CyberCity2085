"""Verify a self-contained one-piece PBR GLB and its externally saved bake maps."""
import json
import struct
import sys
from pathlib import Path
from PIL import Image

folder=Path(sys.argv[1]).resolve()
if folder.drive.upper()!='E:': raise ValueError('Use E:')
payload=(folder/'security_shell_pbr.glb').read_bytes()
magic,version,length=struct.unpack_from('<III',payload)
assert magic==0x46546C67 and version==2 and length==len(payload)
size,kind=struct.unpack_from('<II',payload,12)
assert kind==0x4E4F534A
data=json.loads(payload[20:20+size])
assert len(data['meshes'])==1 and len(data['scenes'])==1
assert len(data['images'])==3 and all('bufferView' in i for i in data['images'])
assert not data.get('skins') and not data.get('animations')
for material in data['materials']:
    pbr=material['pbrMetallicRoughness']
    assert 'baseColorTexture' in pbr and 'metallicRoughnessTexture' in pbr
    assert 'normalTexture' in material
maps={}
for name in ['BaseColor','Roughness','Metallic','Normal']:
    image=Image.open(folder/f'{name}.png')
    assert image.size==(512,512)
    maps[name]={'size':list(image.size),'channel_extrema':image.convert('RGB').getextrema()}
report={'glb_bytes':len(payload),'meshes':1,'scenes':1,'embedded_images':3,
        'connected_maps':['baseColor','metallicRoughness','normal'],'bake_maps':maps,
        'source_fidelity':'NOT VERIFIED','whole_robot':'NOT EXPORTED'}
(folder/'pbr_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('CHARGE_PBR_PIECE_VERIFIED bytes=',len(payload),'embedded_images=3')
