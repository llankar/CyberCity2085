"""Acquire a few authored scene props at1K, not a massive environment conversion."""
from pathlib import Path
import hashlib
import json
import urllib.request
import re
import zipfile

ROOT=Path('E:/CyberCity2085-3d-lab/sources/environment169')
HEADERS={'User-Agent':'CyberCity2085-ExperimentalStudy/1.0'}

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=60).read()

def main():
    ROOT.mkdir(exist_ok=True)
    for name in ['medical_box','modular_industrial_pipes_01','street_lamp_01','modular_electric_cables','old_military_compressor','rollershutter_door',
                 'modular_factory_facade','modular_urban_apartments_facade','modular_airduct_rectangular_01','modular_fire_escape']:
        meta=ROOT/(name+'.json')
        if not meta.exists():meta.write_bytes(get('https://api.polyhaven.com/files/'+name))
        data=json.loads(meta.read_text(encoding='utf8'))
        entry=data['gltf']['1k']['gltf']
        files={name+'_1k.gltf':entry,**entry['include']}
        size=sum(f.get('size',0) for f in files.values())
        assert size<80_000_000
        folder=ROOT/name;folder.mkdir(exist_ok=True)
        for relative,item in files.items():
            target=(folder/relative).resolve()
            assert target.is_relative_to(folder.resolve())
            target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():target.write_bytes(get(item['url']))
            assert hashlib.md5(target.read_bytes()).hexdigest()==item['md5']
        print('AUTHORED_PROP_READY',name,size,flush=True)
    for name in ['brick_wall_001','concrete_wall_001','blue_metal_plate']:
        meta=ROOT/(name+'.json')
        if not meta.exists():meta.write_bytes(get('https://api.polyhaven.com/files/'+name))
        data=json.loads(meta.read_text(encoding='utf8'))
        for key in ['diff','nor_gl','rough']:
            entry=data[{'diff':'Diffuse','rough':'Rough'}.get(key,key)]['1k']['jpg']
            target=ROOT/name/(key+'.jpg');target.parent.mkdir(exist_ok=True)
            if not target.exists():target.write_bytes(get(entry['url']))
            assert hashlib.md5(target.read_bytes()).hexdigest()==entry['md5']
        print('PBR_SURFACE_READY',name,flush=True)
    archive=ROOT/'kenney_industrial.zip'
    if not archive.exists():
        html=get('https://kenney.nl/assets/city-kit-industrial').decode('utf8')
        ident=re.search("data-download-id=['\"]([^'\"]+)",html).group(1)
        link=json.loads(get('https://kenney.nl/download-link/'+ident))['url']
        content=get(link);assert len(content)<30_000_000;archive.write_bytes(content)
    folder=ROOT/'kenney_industrial'
    with zipfile.ZipFile(archive) as package:
        for name in package.namelist():
            if not name.endswith(('.glb','.gltf','.bin','.png','.txt')):continue
            target=(folder/name).resolve();assert target.is_relative_to(folder.resolve())
            target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():target.write_bytes(package.read(name))
    print('AUTHORED_ROOF_KIT_READY',flush=True)

if __name__=='__main__':main()
