"""Acquisition must reject unreviewed paths and corrupted official payloads."""
import importlib.util
from pathlib import Path
import pytest

SOURCE=Path(__file__).resolve().parents[1]/'experiments/2d_to_3d/acquire_rocketbox_candidate.py'
spec=importlib.util.spec_from_file_location('rocket_acquire',SOURCE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
PREFIX='Assets/Avatars/Professions/Military_Male_03/'


def test_corrupt_same_size_payload_is_rejected():
    entry={'path':'Textures/example.tga','size':4,'git_blob':module.blob_hash(b'good')}
    assert module.verified_payload(b'good',entry)==b'good'
    for invalid in [b'evil',b'good plus HTML error']:
        with pytest.raises(ValueError,match='size/hash mismatch'):
            module.verified_payload(invalid,entry)


@pytest.mark.parametrize('path',['../escape','/absolute','C:\\escape',PREFIX+'../other.fbx','Assets/Other/huge.fbx'])
def test_paths_cannot_escape_reviewed_candidate(tmp_path,path):
    with pytest.raises(ValueError): module.destination_for(tmp_path,path,PREFIX)


def test_license_and_original_texture_layout_preserved(tmp_path):
    assert module.destination_for(tmp_path,'LICENSE.md',PREFIX)==tmp_path/'LICENSE.md'
    assert module.destination_for(tmp_path,PREFIX+'Textures/body.tga',PREFIX)==tmp_path/'Textures/body.tga'


@pytest.mark.parametrize('manifest',['../../external.json','download_everything.json'])
def test_unreviewed_manifest_rejected_before_network(manifest):
    with pytest.raises(ValueError,match='Unreviewed'): module.acquire(manifest)
