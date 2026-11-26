"""Tone acquired door paint through glTF-native factors, preserving original texture pixels."""
from pathlib import Path
import bpy,json,struct
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase238';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase237/environment.blend'))
root=bpy.data.objects['Occludable_ne_building'];copies={};changed=[];tint=(.28,.34,.40,1)
for obj in root.children_recursive:
 if not obj.name.startswith('Depot237 acquired door_'):continue
 for slot in obj.material_slots:
  old=slot.material
  if not old or not old.use_nodes:continue
  if old.name not in copies:
   material=old.copy();material.name='Depot238 toned '+old.name
   shader=material.node_tree.nodes.get('Principled BSDF');socket=shader.inputs['Base Color']
   node=material.node_tree.nodes.new('ShaderNodeMix');node.data_type='RGBA';node.blend_type='MULTIPLY';node.inputs[0].default_value=1;node.inputs[7].default_value=tint
   if socket.is_linked:material.node_tree.links.new(socket.links[0].from_socket,node.inputs[6])
   else:node.inputs[6].default_value=socket.default_value
   material.node_tree.links.new(node.outputs[2],socket);copies[old.name]=material
  slot.material=copies[old.name]
 changed.append(obj.name)
assert len(changed)==2
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
path=OUT/'environment.glb';bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True)
raw=path.read_bytes();length,kind=struct.unpack_from('<II',raw,12);assert kind==0x4E4F534A
data=json.loads(raw[20:20+length]);materials=[m for m in data['materials'] if m.get('name','').startswith('Depot238 toned ')]
assert materials
for material in materials:
 pbr=material['pbrMetallicRoughness'];factor=pbr.get('baseColorFactor',[1,1,1,1])
 assert all(abs(factor[i]-tint[i])<.001 for i in range(4)),factor
 assert 'baseColorTexture' in pbr and 'normalTexture' in material,material['name']
(OUT/'material_check.json').write_text(json.dumps({'objects':changed,'tint':tint,'exported_materials':[m['name'] for m in materials],'preserved':'Original diffuse and normal textures; glTF factors verified; no image pixels edited','scope':'Door paint only; geometry unchanged'},indent=2))
print('DOOR238_TONE_EXPORTED',len(materials))
