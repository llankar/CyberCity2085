"""Inspect free author archive and extract only licensed runtime animation inputs."""
import json
import struct
import zipfile
from pathlib import Path

archive_path=Path('E:/CyberCity2085-3d-lab/downloads/quaternius_universal_animation_standard.zip')
root=Path('E:/CyberCity2085-3d-lab/sources/quaternius_ual_standard').resolve()
root.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(archive_path) as archive:
    for entry in archive.infolist():
        relative=Path(*Path(entry.filename).parts[1:])
        if not relative.parts or entry.is_dir(): continue
        if relative.name not in {'License.txt','README.txt','UAL1_Standard.glb','UAL1_Standard_RM.glb'}: continue
        target=(root/relative).resolve()
        if not target.is_relative_to(root): raise ValueError('Archive path escaped external workspace')
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(archive.read(entry))
license_text=(root/'License.txt').read_text(encoding='utf-8-sig')
print('AUTHOR_PACKAGE_LICENSE',license_text)
source=root/'Unreal-Godot/UAL1_Standard.glb'
payload=source.read_bytes()
magic,version,length=struct.unpack_from('<III',payload)
assert (magic,version,length)==(0x46546C67,2,len(payload))
size,kind=struct.unpack_from('<II',payload,12)
assert kind==0x4E4F534A
data=json.loads(payload[20:20+size])
report={'source':str(source),'bytes':len(payload),'meshes':len(data.get('meshes',[])),
        'skins':[len(skin['joints']) for skin in data.get('skins',[])],
        'animations':[animation['name'] for animation in data.get('animations',[])],
        'license_text':license_text,'credit':'Quaternius','license_source':'https://quaternius.com/packs/universalanimationlibrary.html'}
(root/'inventory.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('AUTHOR_ANIMATION_INVENTORY',json.dumps({k:v for k,v in report.items() if k!='license_text'}))
