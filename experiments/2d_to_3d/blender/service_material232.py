"""Reuse acquired plate PBR textures on the interpreted service facade, not new geometry."""
from pathlib import Path
import bpy,json
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase232';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase230/environment.blend'))
root=bpy.data.objects['Occludable_south_building_w']
source=bpy.data.materials['Original229 dark roof panels']
paint=source.copy();paint.name='Service232 acquired worn plate PBR'
shader=paint.node_tree.nodes['Principled BSDF']
tex=paint.node_tree.nodes.new('ShaderNodeTexImage')
tex.image=bpy.data.images.load(str(LAB/'sources/environment169/blue_metal_plate/diff.jpg'),check_existing=True)
paint.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
shader.inputs['Metallic'].default_value=.42
changed=[]
for obj in root.children_recursive:
 if obj.type!='MESH' or not obj.name.startswith('Service230 '):continue
 if not any(term in obj.name for term in ['split service door','lower utility cover']):continue
 obj.data.materials.clear();obj.data.materials.append(paint)
 # Existing metric UVs: 2m texture repeat matches the supplied panel's large sheet.
 for uv in obj.data.uv_layers.active.data:uv.uv*=.5
 changed.append(obj.name)
assert len(changed)==4
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'materials.json').write_text(json.dumps({'objects':changed,'texture_source':'sources/environment169/blue_metal_plate','geometry_changes':False,'tactical_changes':False,'scope':'Acquired existing PBR maps; interpreted vertical facade, not recovered original view'},indent=2))
print('WORN232_EXPORTED',len(changed))
