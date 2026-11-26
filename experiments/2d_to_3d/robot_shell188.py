"""Broaden authored robot shells without roundtripping retained animation data."""
from pathlib import Path
import json,struct,copy,numpy as np
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/robot188';OUT.mkdir(exist_ok=True)
raw=(LAB/'generated/phase2/security_opaque137/robot_actions.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);old=copy.deepcopy(doc)
start=20+n;bn,kind=struct.unpack_from('<II',raw,start);original=raw[start+8:start+8+bn];binary=bytearray(original)
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4

def accessor(index,factor,normal=False):
 acc=doc['accessors'][index];view=doc['bufferViews'][acc['bufferView']]
 assert acc['componentType']==5126 and acc['type']=='VEC3' and 'sparse' not in acc
 points=np.ndarray((acc['count'],3),dtype='<f4',buffer=original,offset=view.get('byteOffset',0)+acc.get('byteOffset',0),strides=(view.get('byteStride',12),4)).copy()
 if normal:
  points/=factor;points/=np.maximum(np.linalg.norm(points,axis=1,keepdims=True),1e-8)
 else:
  center=(points.min(axis=0)+points.max(axis=0))/2;points=center+(points-center)*factor
 while len(binary)%4:binary.append(0)
 offset=len(binary);binary.extend(points.astype('<f4').tobytes())
 newview={'buffer':0,'byteOffset':offset,'byteLength':points.nbytes,'target':34962};doc['bufferViews'].append(newview)
 newacc=copy.deepcopy(acc);newacc['bufferView']=len(doc['bufferViews'])-1;newacc['byteOffset']=0
 if not normal:newacc['min']=points.min(axis=0).tolist();newacc['max']=points.max(axis=0).tolist()
 doc['accessors'].append(newacc);return len(doc['accessors'])-1
changed=[]
for node in doc['nodes']:
 name=node.get('name','')
 if 'mesh' not in node:continue
 if any(x in name for x in ['chest_shield','cpu_casing_Evaluated']):factor=np.array([1.6,1.08,1.3]);color=(.42,.28,.55)
 elif any(x in name for x in ['shell_arm','shoulder_guard']):factor=np.array([1.4,1.08,1.4]);color=(.52,.38,.16) if 'shoulder_guard' in name else (.42,.28,.55)
 elif any(x in name for x in ['shell_leg','head_cover']):factor=np.array([1.3,1.03,1.25]);color=(.42,.28,.55)
 else:continue
 mesh=copy.deepcopy(doc['meshes'][node['mesh']])
 for primitive in mesh['primitives']:
  attrs=primitive['attributes'];attrs['POSITION']=accessor(attrs['POSITION'],factor)
  if 'NORMAL' in attrs:attrs['NORMAL']=accessor(attrs['NORMAL'],factor,True)
  # Existing tangent frames are no longer correct after nonuniform shell edits.
  attrs.pop('TANGENT',None)
  if 'material' in primitive:
   mat=copy.deepcopy(doc['materials'][primitive['material']]);pbr=mat.setdefault('pbrMetallicRoughness',{})
   pbr['baseColorFactor']=[linear(c) for c in color]+[1];pbr['metallicFactor']=.5;pbr['roughnessFactor']=.6
   mat['name']=mat.get('name','Shell')+'_Armor188';primitive['material']=len(doc['materials']);doc['materials'].append(mat)
 node['mesh']=len(doc['meshes']);doc['meshes'].append(mesh);changed.append(name)
assert doc.get('animations')==old.get('animations') and doc['skins']==old['skins']
assert bytes(binary[:len(original)])==original
while len(binary)%4:binary.append(0)
doc['buffers'][0]['byteLength']=len(binary)
j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
body=struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary
(OUT/'robot_actions.glb').write_bytes(struct.pack('<III',0x46546c67,2,len(body)+12)+body)
(OUT/'armor.json').write_text(json.dumps({'changed_shells':changed,'retained_animation_count':len(doc.get('animations',[])),'animation_json_skin_and_original_binary_preserved':True,'scope':'artistic rigid shell trial; native motion review still required'},indent=2))
print('ARMOR188_READY',len(changed),len(doc.get('animations',[])))
