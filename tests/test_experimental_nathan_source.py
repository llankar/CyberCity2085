import importlib.util
from pathlib import Path
import sys
import pytest

folder=Path(__file__).resolve().parents[1]/'experiments/2d_to_3d'
sys.path.insert(0,str(folder))
spec=importlib.util.spec_from_file_location('nathan_source',folder/'acquire_nathan_candidate.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def primary():
    return {'uid':module.UID,'user':{'username':'renderpeople'},
            'license':{'slug':'by','url':'http://creativecommons.org/licenses/by/4.0/'}}


def test_specific_original_grant_is_accepted():
    module.validate_primary(primary())


@pytest.mark.parametrize('change',['uid','author','license_slug','license_url'])
def test_wrong_model_or_license_is_rejected(change):
    data=primary()
    if change=='uid':data['uid']='different'
    if change=='author':data['user']['username']='unreviewed'
    if change=='license_slug':data['license']['slug']='by-nc'
    if change=='license_url':data['license']['url']='https://creativecommons.org/licenses/by-nc/4.0/'
    with pytest.raises(ValueError,match='not verified'):module.validate_primary(data)


def scene():
    return {'asset':{'extras':{'source':'https://sketchfab.com/3d-models/'+module.UID,
                            'license':'CC-BY-4.0 (http://creativecommons.org/licenses/by/4.0/)',
                            'author':'Renderpeople (https://sketchfab.com/renderpeople)'}},
            'images':[{'uri':'textures/rp_nathan_animated_003_mat_baseColor.jpeg'}],
            'buffers':[{'uri':'scene.bin'}]}


def test_only_reviewed_offline_resources_are_accepted():
    module.validate_scene(scene())


@pytest.mark.parametrize('uri',['https://unreviewed.invalid/other.jpeg','../outside.jpeg'])
def test_scene_cannot_add_remote_or_escaped_texture(uri):
    data=scene();data['images'][0]['uri']=uri
    with pytest.raises(ValueError,match='Unreviewed external'):module.validate_scene(data)
