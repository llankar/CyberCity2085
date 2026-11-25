"""Independent GLB checks: complete ancestral head subset, UV/image and body motion."""
import hashlib,json
from pathlib import Path
from collections import Counter
import numpy as np
from anatomical_groups import descendants
from glb_document import Glb,COMPONENTS

root=Path('E:/CyberCity2085-3d-lab/generated/phase2');folder=root/'scanned_armor_head01'
source=Glb(root/'renderpeople_nathan01/human.glb');armor=Glb(root/'unvanquished_motion01/human_actions.glb');target=Glb(folder/'human_actions.glb')
def array(g,index):
 a=g.doc['accessors'][index]
 return np.frombuffer(g.expanded_values(index),dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]).reshape(-1,COMPONENTS[a['type']])
def primitive(g,name):
 node=next(n for n in g.doc['nodes'] if n.get('name')==name)
 return g.doc['meshes'][node['mesh']]['primitives'][0]
sp=source.doc['meshes'][0]['primitives'][0];tp=primitive(target,'Game_ScannedHead')
parents={n['name']:None for n in source.doc['nodes'] if 'name' in n}
for node in source.doc['nodes']:
 for child in node.get('children',[]):parents[source.doc['nodes'][child]['name']]=node['name']
anatomy=descendants(parents,'rp_nathan_animated_003_walking_neck_06')
joint_names=[source.doc['nodes'][i]['name'] for i in source.doc['skins'][0]['joints']]
attrs=sp['attributes'];positions=array(source,attrs['POSITION']).astype(float)
joints=array(source,attrs['JOINTS_0']);weights=array(source,attrs['WEIGHTS_0'])
head_weight=np.array([[joint_names[int(i)] in anatomy for i in row] for row in joints])*weights
eligible=(positions[:,1]>1.54)&(head_weight.sum(axis=1)>.5)
source_indices=array(source,sp['indices']).reshape(-1,3)
selected=source_indices[eligible[source_indices].all(axis=1)]
selected_ids=np.unique(selected)
report=json.loads((folder/'assembly_report.json').read_text());transform=np.array(report['head_bind_transform_blender'])
blender=np.column_stack((positions[:,0],-positions[:,2],positions[:,1],np.ones(len(positions))))@transform.T
mapped=np.column_stack((blender[:,0],blender[:,2],-blender[:,1]))
features=np.column_stack((mapped,array(source,attrs['NORMAL']),array(source,attrs['TEXCOORD_0'])))
unique,inverse=np.unique(features[selected_ids],axis=0,return_inverse=True)
source_to_unique=dict(zip(selected_ids,inverse))
actual=np.column_stack([array(target,tp['attributes'][name]) for name in ['POSITION','NORMAL','TEXCOORD_0']])
assigned=[];worst=np.zeros(8)
for start in range(0,len(actual),128):
 block=actual[start:start+128];delta=block[:,None,:]-unique[None,:,:]
 nearest=(delta*delta).sum(axis=2).argmin(axis=1)
 worst=np.maximum(worst,np.abs(block-unique[nearest]).max(axis=0));assigned.extend(nearest.tolist())
assert max(worst[:3])<5e-6 and max(worst[3:6])<2e-4 and max(worst[6:])<2e-6,('Head attribute mismatch',worst)
def canonical(face):
 face=tuple(map(int,face));return min(face,face[1:]+face[:1],face[2:]+face[:2])
expected=Counter(canonical([source_to_unique[i] for i in face]) for face in selected)
observed=Counter(canonical([assigned[i] for i in face]) for face in array(target,tp['indices']).reshape(-1,3))
assert expected==observed,'Authored head triangles missing, reversed or added'
for node in target.doc['nodes']:
 if 'mesh' not in node or node['name']=='Game_ScannedHead':continue
 a=primitive(armor,node['name']);b=primitive(target,node['name'])
 for name in ['POSITION','NORMAL','TEXCOORD_0','JOINTS_0','WEIGHTS_0']:
  assert armor.values(a['attributes'][name])==target.values(b['attributes'][name]),('Body changed',node['name'],name)
 assert armor.values(a['indices'])==target.values(b['indices'])
def tracks(g):
 result={}
 for animation in g.doc['animations']:
  for channel in animation['channels']:
   sampler=animation['samplers'][channel['sampler']]
   key=(animation['name'],g.doc['nodes'][channel['target']['node']]['name'],channel['target']['path'])
   result[key]=(g.values(sampler['input']),g.values(sampler['output']),sampler.get('interpolation','LINEAR'))
 return result
assert tracks(armor)==tracks(target),'Source body animation tracks changed'
image_hashes=[]
for image in target.doc['images']:
 view=target.doc['bufferViews'][image['bufferView']];start=view.get('byteOffset',0)
 image_hashes.append(hashlib.sha256(target.bin[start:start+view['byteLength']]).hexdigest())
assert 'de30242833486227760b8b69590e9ef93b82754046191b82187ed80feef8849f' in image_hashes,'Original photographic JPEG changed'
result={'glb_sha256':hashlib.sha256((folder/'human_actions.glb').read_bytes()).hexdigest(),'head_source_triangles':sum(expected.values()),'head_topology':'EXACT_SELECTED_SOURCE','maximum_position_component_error_m':float(max(worst[:3])),'maximum_normal_component_error':float(max(worst[3:6])),'maximum_uv_component_error':float(max(worst[6:])),'original_photo_jpeg_bytes':'EXACT_SOURCE','unchanged_body_meshes':16,'animation_tracks':'EXACT_SOURCE','scope':'Structural fidelity only; neck seam, expression and Rook artistic acceptance separate'}
(folder/'source_preservation_check.json').write_text(json.dumps(result,indent=2))
print('SCANNED_HEAD_SOURCE_PRESERVATION_OK',json.dumps(result))

