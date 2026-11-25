"""Behavioural math/buffer gates; native source comparison is a separate gate."""
import json
import struct
from pathlib import Path
import numpy as np
import pytest

LAB=Path(__file__).resolve().parents[1]/'experiments'/'2d_to_3d'


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(LAB))
    import glb_document
    import gltf_pose
    import bundle_einar_actions
    return glb_document,gltf_pose,bundle_einar_actions


def write_fixture(path,invalid_view=False):
    binary=struct.pack('<8f',1,2,3,99,4,5,6,88)
    document={'asset':{'version':'2.0'},'buffers':[{'byteLength':len(binary)}],
        'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':100 if invalid_view else 32,'byteStride':16}],
        'accessors':[{'bufferView':0,'componentType':5126,'count':2,'type':'VEC3'}]}
    encoded=json.dumps(document).encode(); encoded+=b' '*(-len(encoded)%4)
    path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(encoded)+len(binary))+
                     struct.pack('<II',len(encoded),0x4e4f534a)+encoded+
                     struct.pack('<II',len(binary),0x004e4942)+binary)


def test_interleaved_accessor_survives_copy_and_roundtrip(modules,tmp_path):
    glb,_,_=modules
    source_path=tmp_path/'source.glb'; write_fixture(source_path)
    source=glb.Glb(source_path)
    assert struct.unpack('<6f',source.values(0))==(1,2,3,4,5,6)
    target=glb.Glb(source_path)
    copied=target.copy_accessor(source,0)
    extra=target.add_floats([.25,.75],2)
    output=tmp_path/'target.glb'; target.save(output)
    loaded=glb.Glb(output)
    assert loaded.values(copied)==source.values(0)
    assert struct.unpack('<2f',loaded.values(extra))==(.25,.75)


def test_out_of_buffer_views_are_rejected(modules,tmp_path):
    glb,_,_=modules
    source=tmp_path/'invalid.glb'; write_fixture(source,invalid_view=True)
    with pytest.raises(ValueError,match='outside embedded'): glb.Glb(source)


def test_motion_weights_clear_other_clip_targets_and_keep_normal_offset(modules):
    _,_,bundle=modules
    assert bundle.padded_weights([1,0,.25,.75],2,7,3,constant=6)==[0,0,0,1,0,0,1,0,0,0,.25,.75,0,1]
    with pytest.raises(ValueError): bundle.padded_weights([1,0],2,7,3,constant=4)
    with pytest.raises(ValueError): bundle.padded_weights([1],2,7,3)


def test_rebase_preserves_skin_transform_with_different_rest_basis(modules):
    _,pose,_=modules
    old_rest=pose.matrix_trs([.1,1.5,-.2],[.2,.1,0,.97],[1,1,1])
    new_rest=pose.matrix_trs([-.2,.9,.3],[0,-.3,.1,.95],[1,1,1])
    animation=pose.matrix_trs([.2,1.4,.1],[.1,.4,-.2,.88],[1,1,1])
    target=animation @ np.linalg.inv(old_rest) @ new_rest
    t,q,s,error=pose.decompose(target)
    assert error<1e-12
    assert np.allclose(pose.matrix_trs(t,q,s) @ np.linalg.inv(new_rest), animation @ np.linalg.inv(old_rest),atol=1e-12)


def test_shear_is_not_silently_discarded(modules):
    _,pose,_=modules
    matrix=np.eye(4); matrix[0,1]=.1
    with pytest.raises(ValueError,match='shear'): pose.decompose(matrix)


def test_quaternion_sign_change_keeps_shortest_rotation(modules):
    _,pose,_=modules
    result=pose.sample([0,1],[[0,0,0,1],[0,0,0,-1]],.5,quaternion=True)
    assert np.allclose(result,[0,0,0,1])
