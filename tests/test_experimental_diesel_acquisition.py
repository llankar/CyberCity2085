import importlib.util
from pathlib import Path
import struct
import hashlib
import pytest

spec=importlib.util.spec_from_file_location('acquire_diesel_candidate',Path(__file__).parents[1]/'experiments/2d_to_3d/acquire_diesel_candidate.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_rejects_html_instead_of_asset():
    with pytest.raises(ValueError):module.checked_glb(b'<!doctype html><html>download</html>')


@pytest.mark.parametrize('magic,version,size',[(0,2,28),(0x46546c67,1,28),(0x46546c67,2,100)])
def test_rejects_wrong_or_truncated_envelope(magic,version,size):
    with pytest.raises(ValueError):module.checked_glb(struct.pack('<III',magic,version,size)+bytes(16))


def test_records_exact_complete_envelope_digest():
    data=struct.pack('<III',0x46546c67,2,28)+bytes(16)
    assert module.checked_glb(data)==hashlib.sha256(data).hexdigest()
