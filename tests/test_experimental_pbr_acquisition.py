import importlib.util
import hashlib
import io
import json
from pathlib import Path
import zipfile
import pytest

path=Path(__file__).resolve().parents[1]/'experiments/2d_to_3d/acquire_jacket_leather.py'
spec=importlib.util.spec_from_file_location('acquire_leather',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def configure(monkeypatch,tmp_path,host='acg-download.struffelproductions.com'):
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w') as archive:
        for suffix in ['Color.png','NormalGL.png','Roughness.png']:
            archive.writestr('Leather037_2K-PNG_'+suffix,b'fixture map '+suffix.encode())
        archive.writestr('../escaped.txt',b'Never extract this unrequested entry')
    class Response:
        url='https://'+host+'/fixture.zip'
        headers={}
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def raise_for_status(self):pass
        def iter_content(self,_):yield data.getvalue()
    monkeypatch.setattr(module,'ROOT',tmp_path/'pbr')
    monkeypatch.setattr(module,'EXPECTED_BYTES',len(data.getvalue()))
    monkeypatch.setattr(module,'EXPECTED_SHA256',hashlib.sha256(data.getvalue()).hexdigest())
    monkeypatch.setattr(module.requests,'get',lambda *a,**kw:Response())
    return module.ROOT


def test_download_whitelist_does_not_extract_archive_traversal(monkeypatch,tmp_path):
    root=configure(monkeypatch,tmp_path)
    module.acquire()
    assert not (tmp_path/'escaped.txt').exists()
    report=json.loads((root/'provenance.json').read_text())
    assert len(report['maps'])==3 and report['license']=='CC0-1.0'
    assert (root/'Leather037_2K-PNG_Color.png').read_bytes()==b'fixture map Color.png'


def test_corrupt_cached_texture_is_not_reported_as_verified(monkeypatch,tmp_path):
    root=configure(monkeypatch,tmp_path)
    module.acquire()
    (root/'Leather037_2K-PNG_Color.png').write_bytes(b'changed')
    with pytest.raises(AssertionError,match='Cached PBR map changed'):module.acquire()


def test_unreviewed_redirect_is_rejected(monkeypatch,tmp_path):
    root=configure(monkeypatch,tmp_path,host='unreviewed.invalid')
    with pytest.raises(AssertionError):module.acquire()
    assert not (root/'download.partial').exists()


def test_stream_limit_stops_payload_without_leaving_partial(monkeypatch,tmp_path):
    root=configure(monkeypatch,tmp_path)
    monkeypatch.setattr(module,'LIMIT',32)
    with pytest.raises(ValueError,match='limit exceeded'):module.acquire()
    assert not (root/'download.partial').exists()
    assert not (root/'Leather037_2K-PNG.zip').exists()


def test_valid_zip_with_unreviewed_hash_is_rejected(monkeypatch,tmp_path):
    root=configure(monkeypatch,tmp_path)
    monkeypatch.setattr(module,'EXPECTED_SHA256','0'*64)
    with pytest.raises(AssertionError,match='Reviewed PBR source changed'):module.acquire()
    assert not (root/'download.partial').exists()
    assert not (root/'Leather037_2K-PNG.zip').exists()
