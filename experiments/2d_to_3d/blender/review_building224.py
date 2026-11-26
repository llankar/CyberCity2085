"""Neutral review of one acquired complete cyberpunk building, not production."""
from pathlib import Path
import bpy,json
from mathutils import Vector
LAB=Path('E:/CyberCity2085-3d-lab')
OUT=LAB/'generated/phase2/building224';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'sources/building224/source.blend'),use_scripts=False)
scene=bpy.context.scene
meshes=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
lo=Vector([min(p[i] for p in points) for i in range(3)])
hi=Vector([max(p[i] for p in points) for i in range(3)])
center=(lo+hi)/2;span=max(hi-lo)
for obj in list(scene.objects):
 if obj.type in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
scene.world=bpy.data.worlds.new('Neutral224');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.12,.12,1)
for offset,energy in [((1,-2,3),3000),((-2,1,2),1800)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*span*.6)
 lamp=bpy.context.object;lamp.data.energy=energy;lamp.data.size=span
 lamp.rotation_euler=(center-lamp.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=center+Vector((1.4,-2,1.1))*span)
scene.camera=bpy.context.object
scene.camera.rotation_euler=(center-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=span*1.35
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.filepath=str(OUT/'neutral.png');bpy.ops.render.render(write_still=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'review.blend'))
(OUT/'inventory.json').write_text(json.dumps({'dimensions':list(hi-lo),'meshes':[o.name for o in meshes],'images':[{'name':i.name,'size':list(i.size)} for i in bpy.data.images]},indent=2))
print('BUILDING224_REVIEW',len(meshes),list(hi-lo))
