"""Acquire only CUDA12.8 compilation components on E:, without system install."""
from pathlib import Path
import gzip
import hashlib
import json
import urllib.request

ROOT=Path('E:/CyberCity2085-3d-lab')
BASE='https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/'
WANTED={'cuda-nvcc-12-8','cuda-crt-12-8','cuda-cudart-12-8','cuda-cudart-dev-12-8',
        'cuda-cccl-12-8','cuda-driver-dev-12-8'}

def main():
    folder=ROOT/'downloads/cuda168';folder.mkdir(parents=True,exist_ok=True)
    index=folder/'Packages.gz'
    if not index.exists(): urllib.request.urlretrieve(BASE+'Packages.gz',index)
    selected={}
    for block in gzip.decompress(index.read_bytes()).decode().split('\n\n'):
        fields=dict(line.split(': ',1) for line in block.splitlines() if ': ' in line and not line.startswith(' '))
        if fields.get('Package') in WANTED: selected[fields['Package']]=fields
    assert selected.keys()==WANTED
    total=sum(int(f['Size']) for f in selected.values())
    assert total<300_000_000, f'Unexpected compilation download size {total}'
    for name,fields in selected.items():
        dest=folder/Path(fields['Filename']).name
        if not dest.exists(): urllib.request.urlretrieve(BASE+fields['Filename'],dest)
        assert dest.stat().st_size==int(fields['Size'])
        assert hashlib.sha256(dest.read_bytes()).hexdigest()==fields['SHA256']
        print('CUDA_COMPONENT_READY',name,dest.stat().st_size,flush=True)
    (folder/'components.json').write_text(json.dumps({'source':BASE,'bytes':total,'components':selected},indent=2))

if __name__=='__main__': main()
