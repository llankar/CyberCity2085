"""Paneled utility pair from actual map silhouette/colors, inferred depth."""
from pathlib import Path
import sys,bpy,json,math
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box,make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'environment-library/assets/purple_paneled_pair'
data=json.loads((OUT/'source.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
purple=make_material('Weathered muted purple panels',(.12,.055,.105,1),.45,.66)
steel=make_material('Dark structural strips',(.022,.027,.035,1),.65,.6)
edge=make_material('Dull bronze hinge hardware',(.16,.105,.055,1),.6,.6)
for filename,socket in [('rough.jpg','Roughness'),('nor_gl.jpg','Normal')]:
 tex=purple.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(LAB/'sources/environment169/blue_metal_plate'/filename));tex.image.colorspace_settings.name='Non-Color'
 shader=purple.node_tree.nodes['Principled BSDF']
 if socket=='Normal':
  normal=purple.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.45
  purple.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);purple.node_tree.links.new(normal.outputs['Normal'],shader.inputs[socket])
 else:purple.node_tree.links.new(tex.outputs['Color'],shader.inputs[socket])
parts=[]
for x in [-.39,.39]:
 parts.append(box('Chamfered utility housing',(x,0,.42),(.365,.77,.39),purple,.055))
 parts.append(box('Inset lid',(x,0,.825),(.31,.7,.018),purple,.02))
 for dx in [-.31,.31]:parts.append(box('Long reinforcement',(x+dx,0,.85),(.017,.70,.016),steel,.005))
 for y in [-.68,0,.68]:
  parts.append(box('Cross-panel seam',(x,y,.85),(.31,.014,.016),steel,.004))
  for dx in [-.30,.30]:parts.append(box('Hinge fitting',(x+dx,y,.875),(.026,.036,.014),edge,.006))
 for dx in [-.34,.34]:
  for y in [-.68,.68]:parts.append(box('Corner protection',(x+dx,y,.44),(.022,.04,.34),steel,.008))
 for y in [-.79,.79]:
  parts.append(box('Recessed end access',(x,y,.42),(.25,.012,.26),steel,.015))
  parts.append(box('Panel handle',(x,y*1.025,.56),(.09,.015,.014),edge,.005))
 parts.append(box('Base plinth',(x,0,.035),(.37,.77,.035),steel,.02))
for o in bpy.context.scene.objects:o.select_set(o in parts)
bpy.ops.file.pack_all()
bpy.ops.export_scene.gltf(filepath=str(OUT/'optimized.glb'),export_format='GLB',use_selection=True,export_apply=True)
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Neutral228');scene.world.color=(.15,.15,.15)
for pos,power in [((2,-3,4),500),((-2,2,3),350)]:
 bpy.ops.object.light_add(type='AREA',location=pos);lamp=bpy.context.object;lamp.data.energy=power;lamp.data.size=4
 lamp.rotation_euler=(Vector((0,0,.4))-lamp.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2,-3,3));scene.camera=bpy.context.object
scene.camera.rotation_euler=(Vector((0,0,.4))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=3.5
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.filepath=str(OUT/'neutral.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'source.blend'))
points=[obj.matrix_world@Vector(corner) for obj in parts for corner in obj.bound_box]
data['dimensions']=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
data['dimension_status']='Reconstructed mesh bounds; source footprint estimated, height inferred'
data.update(models={'glb':str(OUT/'optimized.glb'),'blend':str(OUT/'source.blend')},artistic_status='BLENDER_PROTOTYPE_PENDING_NATIVE_REVIEW',method='Blender mechanical interpretation from one original source; no Hunyuan inference')
(OUT/'source.json').write_text(json.dumps(data,indent=2))
p=LAB/'environment-library/library.json';catalog=json.loads(p.read_text(encoding='utf8'));catalog['assets']=[data if a['id']==data['id'] else a for a in catalog['assets']];p.write_text(json.dumps(catalog,indent=2,ensure_ascii=False),encoding='utf8')
print('CONTAINER228_EXPORTED',len(parts))
