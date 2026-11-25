"""Fetch one explicitly reviewed MIT candidate, pinned by Git commit/blob IDs."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import requests


def blob_hash(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def verified_payload(data, entry):
    if len(data) != entry['size'] or blob_hash(data) != entry['git_blob']:
        raise ValueError('Source payload size/hash mismatch: '+entry['path'])
    return data


def destination_for(root, source_path, prefix):
    path=PurePosixPath(source_path)
    if path.is_absolute() or '..' in path.parts or '\\' in source_path:
        raise ValueError('Unsafe source path')
    if source_path != 'LICENSE.md' and not source_path.startswith(prefix):
        raise ValueError('Source outside reviewed candidate')
    destination=(root/source_path.removeprefix(prefix)).resolve()
    if not destination.is_relative_to(root.resolve()):
        raise ValueError('Destination outside acquisition directory')
    return destination


def acquire():
    manifest=json.loads((Path(__file__).parent/'manifests/rocketbox_military03.json').read_text())
    assert manifest['license']=='MIT' and manifest['asset']=='Military_Male_03'
    root=Path('E:/CyberCity2085-3d-lab/sources/rocketbox/Military_Male_03').resolve()
    root.mkdir(parents=True,exist_ok=True)
    total=sum(file['size'] for file in manifest['files'])
    assert total<160_000_000,'Review larger acquisition before download'
    prefix='Assets/Avatars/Professions/Military_Male_03/'
    report=[]
    for file in manifest['files']:
        path=PurePosixPath(file['path'])
        relative=str(path).removeprefix(prefix)
        destination=destination_for(root,file['path'],prefix)
        destination.parent.mkdir(parents=True,exist_ok=True)
        url=f"https://raw.githubusercontent.com/{manifest['repository']}/{manifest['commit']}/{path}"
        data=destination.read_bytes() if destination.exists() else b''
        if len(data)!=file['size'] or blob_hash(data)!=file['git_blob']:
            with requests.get(url,stream=True,timeout=90) as response:
                response.raise_for_status()
                pieces=[]; received=0
                for piece in response.iter_content(1024*1024):
                    received+=len(piece)
                    if received>file['size']: raise ValueError('Download exceeded reviewed size')
                    pieces.append(piece)
            data=b''.join(pieces)
            verified_payload(data,file)
            destination.write_bytes(data)
        report.append({'file':str(destination.relative_to(root)),'bytes':len(data),'source':url,
                       'git_blob':file['git_blob'],'sha256':hashlib.sha256(data).hexdigest()})
        print('ROCKETBOX_FILE_VERIFIED',relative,len(data),flush=True)
    notice=(root/'LICENSE.md').read_text()
    assert 'MIT License' in notice and 'Copyright (c) 2020 Microsoft' in notice and 'distribute' in notice
    (root/'acquisition.json').write_text(json.dumps({'manifest':manifest,'files':report,'total_bytes':total},indent=2),encoding='utf-8')
    print('ROCKETBOX_CANDIDATE_ACQUIRED',len(report),total,flush=True)


if __name__=='__main__': acquire()
