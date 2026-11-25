"""Verify actual authored OBJ topology/UV/texture survives the measured hair fit."""
import io,json,hashlib
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image
from glb_document import Glb,COMPONENTS

root=Path('E:/CyberCity2085-3d-lab');folder=root/'generated/phase2/scanned_armor_hair01';source=root/'sources/makehuman_maxwell_hair'
g=Glb(folder/'human_actions.glb');report=json.loads((folder/'hair_fit_report.json').read_text())
positions=[];uv=[];faces=[]
for line in (source/'maxwell_hair_mh.obj').read_text().splitlines():
 fields=line.split()
 if not fields:continue
 if fields[0]=='v':positions.append([float(x) for x in fields[1:4]])
 elif fields[0]=='vt':uv.append([float(x) for x in fields[1:3]])
 elif fields[0]=='f':
  assert len(fields)==4,'Reviewed source must be triangles'
  faces.append([(int(item.split('/')[0])-1,int(item.split('/')[1])-1) for item in fields[1:]])
assert len(positions)==765 and len(faces)==1468
fit=np.array(report['world_fit_blender']);raw=np.array(positions)
canonical=np.column_stack((raw[:,0],-raw[:,2],raw[:,1],np.ones(len(raw))))@fit.T
mapped=np.column_stack((canonical[:,0],canonical[:,2],-canonical[:,1]))
expected=np.array([list(mapped[v])+[uv[t][0],1-uv[t][1]] for face in faces for v,t in face])
unique,inverse=np.unique(expected,axis=0,return_inverse=True)
node=next(n for n in g.doc['nodes'] if n.get('name')=='Game_MaxwellHair');primitive=g.doc['meshes'][node['mesh']]['primitives'][0]
def array(index):
 a=g.doc['accessors'][index]
 return np.frombuffer(g.expanded_values(index),dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]).reshape(-1,COMPONENTS[a['type']])
attrs=primitive['attributes'];actual=np.column_stack((array(attrs['POSITION']),array(attrs['TEXCOORD_0'])))
assigned=[];worst=np.zeros(5)
for start in range(0,len(actual),128):
 block=actual[start:start+128];delta=block[:,None,:]-unique[None,:,:]
 nearest=(delta*delta).sum(axis=2).argmin(axis=1)
 worst=np.maximum(worst,np.abs(block-unique[nearest]).max(axis=0));assigned.extend(nearest.tolist())
assert max(worst[:3])<5e-6 and max(worst[3:])<2e-6,('Hair geometry/UV mismatch',worst)
def cyclic(face):
 face=tuple(map(int,face));return min(face,face[1:]+face[:1],face[2:]+face[:2])
assert Counter(cyclic(x) for x in inverse.reshape(-1,3))==Counter(cyclic([assigned[i] for i in face]) for face in array(primitive['indices']).reshape(-1,3)),'Source hair triangles changed'
weights=array(attrs['WEIGHTS_0']);joints=array(attrs['JOINTS_0']);mask=weights>0
assert np.allclose(weights.sum(axis=1),1) and (mask.sum(axis=1)==1).all()
names=[g.doc['nodes'][i]['name'] for i in g.doc['skins'][node['skin']]['joints']]
assert all(names[int(i)]=='head' for i in joints[mask]),'Hair not bound to actual head'
material=g.doc['materials'][primitive['material']]
assert material['alphaMode']=='MASK' and abs(material['alphaCutoff']-.35)<1e-6 and material['doubleSided']
assert 'KHR_materials_unlit' not in material.get('extensions',{}) and not any(material.get('emissiveFactor',[0,0,0]))
image_index=g.doc['textures'][material['pbrMetallicRoughness']['baseColorTexture']['index']]['source']
image=g.doc['images'][image_index];view=g.doc['bufferViews'][image['bufferView']];start=view.get('byteOffset',0);data=bytes(g.bin[start:start+view['byteLength']])
original=(source/'maxhairtex6.png').read_bytes()
assert np.array_equal(np.array(Image.open(io.BytesIO(data)).convert('RGBA')),np.array(Image.open(io.BytesIO(original)).convert('RGBA'))),'Original authored hair pixels changed'
result={'glb_sha256':hashlib.sha256((folder/'human_actions.glb').read_bytes()).hexdigest(),'source_triangles':1468,'topology':'EXACT_SOURCE','maximum_position_component_error_m':float(max(worst[:3])),'maximum_uv_component_error':float(max(worst[3:])),'source_rgba_pixels':'EXACT_SOURCE','source_png_bytes_exact':data==original,'binding':'head one influence','native_material':'lit MASK .35 double-sided no emission','scope':'Source fidelity, not scalp contact or artistic acceptance'}
(folder/'hair_source_preservation_check.json').write_text(json.dumps(result,indent=2))
print('MAXWELL_HAIR_SOURCE_PRESERVATION_OK',json.dumps(result))
