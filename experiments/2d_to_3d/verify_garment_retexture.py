"""Verify every authored triangle/UV corner survives the material-only derivative."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from glb_document import Glb

ROOT=Path('E:/CyberCity2085-3d-lab/generated/phase2')


def corners(path):
    glb=Glb(path)
    nodes=glb.doc['nodes']
    assert len(nodes)==1 and nodes[0]['mesh']==0
    assert nodes[0]['extras']['source_license']=='CC BY 4.0'
    assert nodes[0]['extras']['source_author']=='Nixontrebejo'
    assert all('bufferView' in image and 'uri' not in image for image in glb.doc['images'])
    assert not any(key in nodes[0] for key in ['matrix','translation','rotation','scale'])
    assert len(glb.doc['meshes'])==1 and len(glb.doc['meshes'][0]['primitives'])==1
    primitive=glb.doc['meshes'][0]['primitives'][0]
    p=np.frombuffer(glb.values(primitive['attributes']['POSITION']),dtype='<f4').reshape(-1,3)
    uv=np.frombuffer(glb.values(primitive['attributes']['TEXCOORD_0']),dtype='<f4').reshape(-1,2)
    normal=np.frombuffer(glb.values(primitive['attributes']['NORMAL']),dtype='<f4').reshape(-1,3)
    assert np.isfinite(p).all() and np.isfinite(uv).all() and np.isfinite(normal).all()
    assert np.max(np.abs(np.linalg.norm(normal,axis=1)-1))<.001
    index_id=primitive['indices'];kind=glb.doc['accessors'][index_id]['componentType']
    indices=np.frombuffer(glb.values(index_id),dtype={5123:'<u2',5125:'<u4'}[kind])
    assert len(indices)==55200 and indices.max()<len(p)
    values=np.column_stack((p,uv))[indices].reshape(-1,3,5)
    # Canonical cyclic ordering retains triangle winding and every authored UV
    # seam while allowing harmless exporter vertex/index reordering.
    counter=Counter()
    for triangle in values:
        rows=tuple(tuple(float(v) for v in row) for row in triangle)
        counter[min(rows,rows[1:]+rows[:1],rows[2:]+rows[:2])]+=1
    return counter,len(p)


def verify(folder):
    assert folder in ['trebejo_leather01','trebejo_leather02']
    source=ROOT/'trebejo_jacket/jacket.glb';target=ROOT/folder/'jacket.glb'
    original,_=corners(source);modified,count=corners(target)
    assert original==modified,'Authored geometry, winding or UV corners changed'
    report={'source_glb_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'target_glb_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'triangles_compared':18400,'all_position_uv_corner_tuples_exact':True,
            'render_vertices':count,'artistic_acceptance':False}
    (ROOT/folder/'geometry_uv_check.json').write_text(json.dumps(report,indent=2))
    print('AUTHORED_GARMENT_GEOMETRY_UV_OK',folder,count)


if __name__=='__main__':verify(sys.argv[1] if len(sys.argv)>1 else 'trebejo_leather02')
