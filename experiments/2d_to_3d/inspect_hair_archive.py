"""Inspect one publisher-reviewed hair pack using bounded HTTP byte ranges only.

Archive gaps exist only in RAM. Never extract the full pack or unrelated models.
"""
import io,json,struct,hashlib,urllib.request,zipfile
from pathlib import Path

URL='https://files2.makehumancommunity.org/asset_packs/hair02/hair02_ccby.zip'
SIZE=72283345
ETAG='"44ef4d1-6160e77b9a38e"'
ROOT=Path('E:/CyberCity2085-3d-lab/sources/makehuman_hair_review')

def directory_span(tail,total_size):
    offset=tail.rfind(b'PK\x05\x06')
    if offset<0 or len(tail)-offset<22:raise ValueError('Missing ZIP end record')
    _,disk,central_disk,entries_disk,entries,size,start,comment=struct.unpack_from('<4s4H2LH',tail,offset)
    if disk or central_disk or entries_disk!=entries or offset+22+comment!=len(tail):raise ValueError('Unsupported ZIP layout')
    if entries==65535 or not 0<size<=1024*1024 or not 0<=start<start+size<=total_size-len(tail)+offset:raise ValueError('Invalid ZIP directory bounds')
    return start,size

def read_range(first,last):
    if not 0<=first<=last<SIZE or last-first+1>16*1024*1024:raise ValueError('Unreviewed byte range')
    folder=ROOT/'ranges';folder.mkdir(parents=True,exist_ok=True)
    path=folder/f'{first}-{last}.bin';expected=last-first+1
    if path.exists():
        data=path.read_bytes()
        if len(data)==expected:return data
    request=urllib.request.Request(URL,headers={'Range':f'bytes={first}-{last}','If-Match':ETAG})
    with urllib.request.urlopen(request,timeout=45) as response:
        if response.status!=206 or response.headers.get('Content-Range')!=f'bytes {first}-{last}/{SIZE}' or response.headers.get('ETag')!=ETAG:
            raise ValueError('Publisher archive version/range mismatch')
        data=response.read(expected+1)
    if len(data)!=expected:raise ValueError('Incomplete bounded range')
    path.write_bytes(data)
    return data

def open_reviewed_archive():
    tail=read_range(SIZE-65557,SIZE-1);start,size=directory_span(tail,SIZE)
    memory=io.BytesIO();memory.seek(SIZE-len(tail));memory.write(tail)
    if start<SIZE-len(tail):memory.seek(start);memory.write(read_range(start,start+size-1))
    return memory,zipfile.ZipFile(memory)

if __name__=='__main__':
    memory,archive=open_reviewed_archive()
    selected=[i for i in archive.infolist() if 'elvs_maxwell_hair' in i.filename or i.filename.startswith('packs/')]
    report={'url':URL,'archive_bytes':SIZE,'etag':ETAG,'selection':[{'path':i.filename,'bytes':i.file_size,'compressed_bytes':i.compress_size,'crc32':i.CRC,'header_offset':i.header_offset} for i in selected],'scope':'Directory inspection only; not acquired/licence-version-qualified yet'}
    (ROOT/'remote_directory_review.json').write_text(json.dumps(report,indent=2))
    print('HAIR_REMOTE_DIRECTORY_REVIEW',json.dumps(report),flush=True)
