"""One reviewed CC0 PBR surface; bounded public download, all files on E:."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
import zipfile
import requests

ROOT=Path('E:/CyberCity2085-3d-lab/sources/ambientcg_Leather037')
URL='https://ambientcg.com/get?file=Leather037_2K-PNG.zip'
LIMIT=64_000_000
EXPECTED_BYTES=57_088_064
EXPECTED_SHA256='055968fef7b4f1b401f30e9fa952e1b0ade2dfb27c82f297cef8e75eb67e3dc7'


def acquire():
    ROOT.mkdir(exist_ok=True)
    archive=ROOT/'Leather037_2K-PNG.zip'
    if archive.exists():
        report=json.loads((ROOT/'provenance.json').read_text())
        assert archive.stat().st_size==EXPECTED_BYTES
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==report['sha256']==EXPECTED_SHA256
        for item in report['maps']:
            assert Path(item['name']).name==item['name']
            payload=(ROOT/item['name']).read_bytes()
            assert len(payload)==item['bytes'] and hashlib.sha256(payload).hexdigest()==item['sha256'], 'Cached PBR map changed'
        print('Reviewed PBR archive already verified');return
    temporary=ROOT/'download.partial'
    digest=hashlib.sha256();size=0
    try:
        with requests.get(URL,stream=True,timeout=45) as response:
            response.raise_for_status()
            assert urlparse(response.url).hostname in ['ambientcg.com','acg-download.struffelproductions.com']
            assert int(response.headers.get('Content-Length',0))<=LIMIT
            with temporary.open('wb') as output:
                for block in response.iter_content(65536):
                    size+=len(block)
                    if size>LIMIT:raise ValueError('Reviewed PBR download limit exceeded')
                    digest.update(block);output.write(block)
        assert size==EXPECTED_BYTES and digest.hexdigest()==EXPECTED_SHA256, 'Reviewed PBR source changed'
        with zipfile.ZipFile(temporary) as bundle:
            assert sum(info.file_size for info in bundle.infolist())<160_000_000
            assert bundle.testzip() is None
            extracted=[]
            for suffix in ['Color.png','NormalGL.png','Roughness.png']:
                name='Leather037_2K-PNG_'+suffix
                assert name in bundle.namelist()
                payload=bundle.read(name)
                (ROOT/name).write_bytes(payload)
                extracted.append({'name':name,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()})
        temporary.replace(archive)
        report={'asset':'Leather037','source':'https://ambientcg.com/view?id=Leather037',
                'download':URL,'license':'CC0-1.0','license_source':'https://docs.ambientcg.com/license/',
                'bytes':size,'sha256':digest.hexdigest(),'maps':extracted,
                'scope':'One 2K PBR set for authored garment retexturing. No human model or AI weights.'}
        (ROOT/'provenance.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        (ROOT/'CREDITS.txt').write_text('Leather037 by Lennart Demes / ambientCG.com. CC0 1.0.\nhttps://ambientcg.com/view?id=Leather037\nhttps://docs.ambientcg.com/license/\n',encoding='utf8')
        print('LEATHER_PBR_ACQUIRED',size,digest.hexdigest())
    finally:
        temporary.unlink(missing_ok=True)


if __name__=='__main__':acquire()
