import importlib.util,struct
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('hair_archive',Path(__file__).parents[1]/'experiments/2d_to_3d/inspect_hair_archive.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def record(size=100,start=800,disk=0,entries_disk=1,entries=1,comment=b''):
    return struct.pack('<4s4H2LH',b'PK\x05\x06',disk,0,entries_disk,entries,size,start,len(comment))+comment

def test_directory_range_excludes_payload():
    assert module.directory_span(record(comment=b'hello'),1000)==(800,100)

@pytest.mark.parametrize('data,total',[ (b'not a zip',1000),(record()[:-1],1000),(record(disk=1),1000),(record(entries_disk=2),1000),(record(start=950),1000),(record(size=1048577),2000000),(record(entries=65535,entries_disk=65535),1000)])
def test_invalid_or_unbounded_directory_rejected(data,total):
    with pytest.raises(ValueError):module.directory_span(data,total)
