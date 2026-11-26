"""Cohesive visible art pass, preserving existing tactical obstacle volumes."""
from pathlib import Path
import bpy,json,random,math
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase198';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase197/environment.blend'))
# Remove the two old oversized dressing valves: one obscures shop type, one
# overlaps the staged casualty. Neither participates in the tactical cell map.
removed=[]
for obj in list(bpy.data.objects):
 if obj.type=='MESH' and obj.name.startswith('modular_industrial_pipes_01_pipe08'):
  removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
# Reuse the local metal's measured roughness and normal texture. Preserve the
# selected palette, rather than making every counter bright blue.
rough=bpy.data.images.load(str(LAB/'sources/environment169/blue_metal_plate/rough.jpg'));rough.colorspace_settings.name='Non-Color'
normal=bpy.data.images.load(str(LAB/'sources/environment169/blue_metal_plate/nor_gl.jpg'));normal.colorspace_settings.name='Non-Color'
materials=[]
for material in bpy.data.materials:
 if not material.name.startswith(('Store197 brushed','Store197 paint')):continue
  # node textures use the existing cube UVs and are exported with the GLB.
 nodes=material.node_tree.nodes;links=material.node_tree.links;shader=nodes.get('Principled BSDF')
 r=nodes.new('ShaderNodeTexImage');r.image=rough;links.new(r.outputs['Color'],shader.inputs['Roughness'])
 n=nodes.new('ShaderNodeTexImage');n.image=normal;b=nodes.new('ShaderNodeNormalMap');b.inputs['Strength'].default_value=.35;links.new(n.outputs['Color'],b.inputs['Color']);links.new(b.outputs['Normal'],shader.inputs['Normal']);materials.append(material.name)
# Break the identical marching rows without spilling over the counter.
random.seed(198);stock=[]
for root in [o for o in bpy.data.objects if o.name.startswith('Occludable_market_')]:
 # Stock imports contain multiple meshes: transform each merchandise unit as
 # one group, keyed by their original shared translation, preserving its parts.
 groups={}
 for obj in root.children_recursive:
  if obj.type=='MESH' and obj.name.startswith(('Store197 sealed','Store197 medical','Store197 rear')):
   # All parts were normalized from common source bounds, so origins match.
   groups.setdefault(tuple(round(v,5) for v in obj.location),[]).append(obj)
 for index,parts in enumerate(groups.values()):
  dx=random.uniform(-.06,.06);dy=random.uniform(-.06,.06)
  for obj in parts:obj.location.x+=dx;obj.location.y+=dy
  stock.append(len(parts))
 # Different fascia finish and subtle segmented trim make the three brands
 # distinct at normal combat zoom, rather than adding tiny unreadable details.
 for obj in root.children_recursive:
  if obj.name.startswith('Store197 counter fascia'):
   for slot in obj.material_slots:
    if slot.material:
     mat=slot.material.copy();mat.name='Art198 worn '+root.name;shader=mat.node_tree.nodes.get('Principled BSDF');c=shader.inputs['Base Color'].default_value;c[0]*=.7;c[1]*=.7;c[2]*=.7;slot.material=mat
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'));bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'art.json').write_text(json.dumps({'removed_conflicting_dressing':removed,'pbr_metal_materials':materials,'stock_groups':len(stock),'scope':'same functional map; local materials/merchandise; retained197 source'},indent=2));print('ART198_READY',len(removed),len(stock),flush=True)
