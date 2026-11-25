"""Verify material-only eye derivative preserves every authored textured triangle."""
from collections import Counter
import json,hashlib
from pathlib import Path
import numpy as np
from glb_document import Glb,COMPONENTS
root=Path('E:/CyberCity2085-3d-lab/generated/phase2');folder=root/'nathan_eyes01'
source=Glb(root/'renderpeople_nathan01/human.glb');target=Glb(folder/'human.glb')
def values(g,index):
 a=g.doc['accessors'][index]
 return np.frombuffer(g.expanded_values(index),dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]).reshape(-1,COMPONENTS[a['type']])
def triangles(g):
 result=Counter()
 for mesh in g.doc['meshes']:
  for primitive in mesh['primitives']:
   attrs=[values(g,primitive['attributes'][name]) for name in ['POSITION','NORMAL','TEXCOORD_0','JOINTS_0','WEIGHTS_0']]
   corners=[tuple(float(x) for attr in attrs for x in attr[i]) for i in range(len(attrs[0]))]
   for ids in values(g,primitive['indices']).reshape(-1,3):
    face=tuple(corners[int(i)] for i in ids)
    result[min(face,face[1:]+face[:1],face[2:]+face[:2])]+=1
 return result
assert triangles(source)==triangles(target),'Geometry/UV/skin changed in material-only derivative'
assert len(target.doc['skins'][0]['joints'])==89
assert source.values(source.doc['skins'][0]['inverseBindMatrices'])==target.values(target.doc['skins'][0]['inverseBindMatrices'])
assert [a['name'] for a in target.doc['animations']]==['Walk']
assert [source.doc['nodes'][i]['name'] for i in source.doc['skins'][0]['joints']]==[target.doc['nodes'][i]['name'] for i in target.doc['skins'][0]['joints']]
def tracks(g):
 a=g.doc['animations'][0];result={}
 for channel in a['channels']:
  sampler=a['samplers'][channel['sampler']];key=(g.doc['nodes'][channel['target']['node']]['name'],channel['target']['path'])
  result[key]=(g.values(sampler['input']),g.values(sampler['output']),sampler.get('interpolation','LINEAR'))
 return result
assert tracks(source)==tracks(target),'Source authored motion changed'
def image_bytes(g):
 result=[]
 for image in g.doc['images']:
  view=g.doc['bufferViews'][image['bufferView']];offset=view.get('byteOffset',0)
  result.append(bytes(g.bin[offset:offset+view['byteLength']]))
 return result
assert set(image_bytes(source))==set(image_bytes(target)),'Original8K photographic image changed'
assert len(target.doc['materials'])==2
mat=next(m for m in target.doc['materials'] if m['name']=='AuthoredEyePhototexture_CornealSurface')
assert abs(mat['pbrMetallicRoughness']['roughnessFactor']-.18)<1e-6
assert abs(mat['extensions']['KHR_materials_clearcoat']['clearcoatFactor']-.65)<1e-6
report={'glb_sha256':hashlib.sha256((folder/'human.glb').read_bytes()).hexdigest(),'triangle_corners_position_normal_uv_joints_weights':'EXACT_SOURCE','triangles':sum(triangles(target).values()),'original_8k_image_bytes':'EXACT_SOURCE','bones':89,'materials':2,'authored_animation_tracks':'EXACT_SOURCE','scope':'Material-only structural fidelity; not skin motion/native material/artistic acceptance'}
(folder/'source_preservation_check.json').write_text(json.dumps(report,indent=2))
print('NATHAN_EYE_SOURCE_PRESERVATION_OK',report['triangles'],flush=True)
