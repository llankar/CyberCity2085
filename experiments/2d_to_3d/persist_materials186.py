"""Persist the scene186 material direction in a real GLB (embedded textures retained)."""
from pathlib import Path
import json,struct,copy
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase186';OUT.mkdir(exist_ok=True)
raw=(LAB/'generated/phase2/showcase185/environment.glb').read_bytes();chunks=[];offset=12
while offset<len(raw):
 size,kind=struct.unpack_from('<II',raw,offset);offset+=8;chunks.append((kind,raw[offset:offset+size]));offset+=size
def srgb(v):return 12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
scene=json.loads(next(data for kind,data in chunks if kind==0x4e4f534a));changed=0
for node in scene['nodes']:
 if 'mesh' not in node:continue
 label=node.get('name','');mesh=copy.deepcopy(scene['meshes'][node['mesh']]);modified=False
 for surface,primitive in enumerate(mesh['primitives']):
  if 'material' not in primitive:continue
  mat=copy.deepcopy(scene['materials'][primitive['material']])
  if mat.get('emissiveTexture') or any(mat.get('emissiveFactor',[0,0,0])):continue
  if label.startswith('AuthoredGarageShutter'):factor=(.28,.34,.38);metal=.35;rough=.78
  elif label.startswith('PBR_Facade') and surface==1:factor=(.45,.50,.55);metal=.08;rough=.92
  elif label.startswith(('AuthoredFacade_wall','AuthoredGarageBay')):factor=(.65,.72,.76);metal=None;rough=max(.75,mat.get('pbrMetallicRoughness',{}).get('roughnessFactor',1))
  else:continue
  pbr=mat.setdefault('pbrMetallicRoughness',{});color=pbr.get('baseColorFactor',[1,1,1,1]);pbr['baseColorFactor']=[linear(srgb(color[i])*factor[i]) for i in range(3)]+[color[3]]
  pbr['roughnessFactor']=rough
  if metal is not None:pbr['metallicFactor']=metal
  mat['name']=mat.get('name','Material')+'_Direction186'
  primitive['material']=len(scene['materials']);scene['materials'].append(mat);changed+=1;modified=True
 if modified:node['mesh']=len(scene['meshes']);scene['meshes'].append(mesh)
encoded=json.dumps(scene,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4)
output=[]
for kind,data in chunks:output.append(struct.pack('<II',len(encoded) if kind==0x4e4f534a else len(data),kind)+(encoded if kind==0x4e4f534a else data))
content=b''.join(output);(OUT/'environment.glb').write_bytes(struct.pack('<III',0x46546c67,2,12+len(content))+content)
(OUT/'material_direction.json').write_text(json.dumps({'changed_primitive_materials':changed,'scope':'same source geometry, textures and direction as Godot186'},indent=2))
print('MATERIAL186_GLB',changed)
