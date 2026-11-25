"""Acquire one bounded CC BY jacket from its public licensed redistributor."""
import hashlib
import json
from pathlib import Path
import requests

UID='1a5ef5dbcd304f3a984848cd26de890f'
ROOT=Path('E:/CyberCity2085-3d-lab/sources/trebejo_jacket')


def acquire():
    ROOT.mkdir(exist_ok=True)
    primary=requests.get('https://api.sketchfab.com/v3/models/'+UID,timeout=30)
    primary.raise_for_status(); original=primary.json()
    assert original['license']['slug']=='by' and original['license']['url'].replace('http:','https:')=='https://creativecommons.org/licenses/by/4.0/'
    response=requests.get('https://assets.keeno.dev/asset/'+UID,timeout=30)
    response.raise_for_status(); metadata=response.json()
    # The catalog is a public CC BY redistributor, not the authenticated
    # Sketchfab download endpoint. Verify original author/license separately.
    assert metadata['uid']==UID and metadata['license']=='CC-BY-4.0'
    assert metadata['mb']<2
    url=metadata['glb_url']
    assert url.startswith('https://pub-da56e9d607b24519a815698ff4e9020f.r2.dev/glb/')
    parts=[]; size=0
    with requests.get(url,stream=True,timeout=45) as payload:
        payload.raise_for_status()
        for piece in payload.iter_content(65536):
            size+=len(piece)
            if size>2_000_000: raise ValueError('Asset exceeded reviewed download limit')
            parts.append(piece)
    data=b''.join(parts); assert data[:4]==b'glTF'
    (ROOT/'jacket_source.glb').write_bytes(data)
    (ROOT/'primary_metadata.json').write_text(json.dumps(original,indent=2),encoding='utf-8')
    metadata.update({'acquired_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
        'download_source':url,'reviewed_original_license':'CC BY 4.0','model_modified':False})
    (ROOT/'provenance.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    (ROOT/'CREDITS.txt').write_text(metadata['attribution']+'\nOriginal license: https://creativecommons.org/licenses/by/4.0/\nOriginal work preserved; fitting and export studies will be separate derivatives.\n',encoding='utf-8')
    print('TREBEJO_LICENSED_JACKET_ACQUIRED',len(data),metadata['sha256'],flush=True)


if __name__=='__main__': acquire()
