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


def sparse_fixture(path,ids=(1,3),with_base=False):
    binary=bytearray(struct.pack('<4f',10,20,30,40) if with_base else b'')
    views=[]
    if with_base:views.append({'buffer':0,'byteOffset':0,'byteLength':16})
    start=len(binary);binary.extend(bytes(ids));binary.extend(b'\0'*(-len(binary)%4))
    index_view=len(views);views.append({'buffer':0,'byteOffset':start,'byteLength':len(ids)})
    value_view=len(views);views.append({'buffer':0,'byteOffset':len(binary),'byteLength':8});binary.extend(struct.pack('<2f',5,7))
    accessor={'componentType':5126,'count':4,'type':'SCALAR','sparse':{'count':2,'indices':{'bufferView':index_view,'componentType':5121},'values':{'bufferView':value_view}}}
    if with_base:accessor['bufferView']=0
    doc={'asset':{'version':'2.0'},'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':[accessor]}
    encoded=json.dumps(doc).encode();encoded+=b' '*(-len(encoded)%4)
    path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary)

@pytest.mark.parametrize('with_base',[False,True])
def test_sparse_copy_expands_zero_or_authored_base(modules,tmp_path,with_base):
    reader,_,_=modules
    path=tmp_path/'sparse.glb';sparse_fixture(path,with_base=with_base)
    source=reader.Glb(path)
    with pytest.raises(ValueError,match='explicit expansion'):source.values(0)
    expected=(10,5,30,7) if with_base else (0,5,0,7)
    assert struct.unpack('<4f',source.expanded_values(0))==expected
    target=reader.Glb(path);index=target.copy_accessor(source,0)
    assert 'sparse' not in target.doc['accessors'][index]
    assert struct.unpack('<4f',target.values(index))==expected

@pytest.mark.parametrize('ids',[(1,1),(3,1),(1,4)])
def test_sparse_invalid_indices_rejected(modules,tmp_path,ids):
    reader,_,_=modules
    path=tmp_path/'invalid_sparse.glb';sparse_fixture(path,ids)
    with pytest.raises(ValueError,match='indices'):reader.Glb(path).expanded_values(0)


def test_sparse_overrun_rejected(modules,tmp_path):
    reader,_,_=modules
    path=tmp_path/'sparse.glb';sparse_fixture(path)
    source=reader.Glb(path);source.doc['accessors'][0]['sparse']['values']['byteOffset']=4
    with pytest.raises(ValueError,match='outside'):source.expanded_values(0)
