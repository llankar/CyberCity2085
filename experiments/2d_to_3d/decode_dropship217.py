"""Convert embedded BasisU images to editable PNG, keeping mesh buffers intact."""
import json
from pathlib import Path
import struct
import subprocess

root = Path('E:/CyberCity2085-3d-lab/sources/dropship217')
data = (root/'dropship_uncompressed.glb').read_bytes()
length = struct.unpack_from('<I', data, 12)[0]
doc = json.loads(data[20:20+length])
offset = 20+length
binary = bytearray(data[offset+8:])
ktx = '/mnt/e/CyberCity2085-3d-lab/tools/ktx/KTX-Software-4.4.2-Linux-x86_64/bin/ktx'
for i, image in enumerate(doc.get('images', [])):
    if image.get('mimeType') != 'image/ktx2':
        continue
    view = doc['bufferViews'][image['bufferView']]
    start = view.get('byteOffset', 0)
    source = root/f'image_{i}.ktx2'
    target = root/f'image_{i}.png'
    source.write_bytes(binary[start:start+view['byteLength']])
    linux = lambda p: '/mnt/e/'+str(p).replace('\\','/').split(':/',1)[1]
    subprocess.run(['wsl.exe','-e',ktx,'extract','--transcode','rgba8',linux(source),linux(target)],check=True)
    png = target.read_bytes()
    binary.extend(b'\0'*(-len(binary)%4))
    image['bufferView'] = len(doc['bufferViews'])
    doc['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':len(png)})
    image['mimeType'] = 'image/png'
    binary.extend(png)
for texture in doc.get('textures', []):
    extension = texture.get('extensions',{}).pop('KHR_texture_basisu',None)
    if extension:
        texture['source'] = extension['source']
for key in ('extensionsUsed','extensionsRequired'):
    doc[key] = [e for e in doc.get(key,[]) if e != 'KHR_texture_basisu']
doc['buffers'][0]['byteLength'] = len(binary)
encoded = json.dumps(doc,separators=(',',':')).encode()
encoded += b' '*(-len(encoded)%4)
binary.extend(b'\0'*(-len(binary)%4))
output = struct.pack('<III',0x46546C67,2,28+len(encoded)+len(binary))
output += struct.pack('<II',len(encoded),0x4E4F534A)+encoded
output += struct.pack('<II',len(binary),0x004E4942)+binary
(root/'dropship_blender.glb').write_bytes(output)
print('Converted',len(doc.get('images',[])),'images;',len(output),'bytes')

