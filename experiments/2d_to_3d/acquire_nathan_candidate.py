"""Acquire one original-resolution, explicitly CC BY game-evaluation candidate."""
import hashlib
import json
from pathlib import Path
import requests
from acquire_rocketbox_candidate import blob_hash, verified_payload, destination_for

UID='143a2b1ea5eb4385ae90a73657aca3bc'
REPOSITORY='mehulkapadia5/open-theft-auto'
COMMIT='b37e7f3070501dd90353c250e9ad90dffdf4c8b2'
PREFIX='assets/characters/nathan/'
ROOT=Path('E:/CyberCity2085-3d-lab/sources/renderpeople_nathan')
FILES=[
    {'path':PREFIX+'license.txt','size':776,'git_blob':'37ef84c1ef511b23f6d2fc87fd9afbe0fe56f6bd'},
    {'path':PREFIX+'scene.gltf','size':138654,'git_blob':'7ef5936b9acbcd7713e904fb5a334aef27248cca'},
    {'path':PREFIX+'scene.bin','size':1086168,'git_blob':'14e404245f0c0852ea1d4881762d4d12fb315ff9'},
    {'path':PREFIX+'textures/rp_nathan_animated_003_mat_baseColor.jpeg','size':18827746,'git_blob':'47e4ac9133177596c46906ed947935373d4212b6'},
]


def validate_primary(metadata):
    if (metadata.get('uid')!=UID or metadata.get('user',{}).get('username')!='renderpeople'
            or metadata.get('license',{}).get('slug')!='by'
            or metadata.get('license',{}).get('url','').replace('http:','https:')!='https://creativecommons.org/licenses/by/4.0/'):
        raise ValueError('Original author/model/CC BY4 grant not verified')


def validate_scene(document):
    extras=document.get('asset',{}).get('extras',{})
    if (not extras.get('source','').endswith(UID) or not extras.get('license','').startswith('CC-BY-4.0')
            or not extras.get('author','').startswith('Renderpeople ')):
        raise ValueError('Replica source attribution does not match reviewed model')
    if ({image.get('uri') for image in document.get('images',[])}!={'textures/rp_nathan_animated_003_mat_baseColor.jpeg'}
            or {buffer.get('uri') for buffer in document.get('buffers',[])}!={'scene.bin'}):
        raise ValueError('Unreviewed external scene resource')


def acquire():
    ROOT.mkdir(exist_ok=True)
    primary=requests.get('https://api.sketchfab.com/v3/models/'+UID,timeout=30)
    primary.raise_for_status();metadata=primary.json();validate_primary(metadata)
    assert sum(item['size'] for item in FILES)<24_000_000
    report=[]
    for item in FILES:
        destination=destination_for(ROOT,item['path'],PREFIX)
        destination.parent.mkdir(parents=True,exist_ok=True)
        url=f"https://raw.githubusercontent.com/{REPOSITORY}/{COMMIT}/{item['path']}"
        data=destination.read_bytes() if destination.exists() else b''
        if len(data)!=item['size'] or blob_hash(data)!=item['git_blob']:
            chunks=[];size=0
            with requests.get(url,stream=True,timeout=60) as response:
                response.raise_for_status()
                for chunk in response.iter_content(65536):
                    size+=len(chunk)
                    if size>item['size']:raise ValueError('Candidate exceeded reviewed file size')
                    chunks.append(chunk)
            data=verified_payload(b''.join(chunks),item)
            destination.write_bytes(data)
        report.append({'path':str(destination.relative_to(ROOT)),'bytes':len(data),
                       'git_blob':item['git_blob'],'sha256':hashlib.sha256(data).hexdigest(),'url':url})
        print('NATHAN_SOURCE_FILE_VERIFIED',destination.name,len(data),flush=True)
    document=json.loads((ROOT/'scene.gltf').read_text())
    validate_scene(document)
    notice=(ROOT/'license.txt').read_text()
    assert UID in notice and 'Commercial use is allowed' in notice
    (ROOT/'primary_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
    (ROOT/'acquisition.json').write_text(json.dumps({'uid':UID,'repository':REPOSITORY,
        'commit':COMMIT,'files':report,'bytes':sum(item['size'] for item in FILES),
        'license':'CC-BY-4.0','source_author':'Renderpeople',
        'scope':'Traditional DCC/game evaluation only; no AI training or generative model use',
        'limitations':['Public replica has 8K baseColor only; no normal/roughness map completeness claimed',
                       'Replica file hashes verified; original author/grant verified separately',
                       'Character is a candidate, not accepted Rook art']},indent=2),encoding='utf8')
    print('NATHAN_LICENSED_CANDIDATE_ACQUIRED',sum(item['size'] for item in FILES),flush=True)


if __name__=='__main__':acquire()
