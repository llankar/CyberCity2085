"""Attach actual muzzle/axis sockets to the painted robot's cannon-bearing bone."""
from pathlib import Path
import bpy,json
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/robot193';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/robot191/robot_actions.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');body=next(o for o in bpy.data.objects if o.type=='MESH')
points=[body.matrix_world@v.co for v in body.data.vertices if v.co.z>1.6]
edge=min(p.x for p in points)
cap=[p for p in points if p.x<edge+.025]
rear=[p for p in points if edge+.14<p.x<edge+.18]
assert cap and rear
tip=sum(cap,Vector())/len(cap);breech=sum(rear,Vector())/len(rear);direction=(tip-breech).normalized()
# Keep the barrel rigid on its actual carrying bone.
barrel=[v.index for v in body.data.vertices if v.co.x<edge+.32 and v.co.z>1.65]
for group in body.vertex_groups:group.remove(barrel)
body.vertex_groups['upper_arm.R'].add(barrel,1,'REPLACE')
for name,point in [('CannonMuzzle193',tip),('CannonAxis193',tip+direction*.25)]:
 obj=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(obj)
 obj.parent=rig;obj.parent_type='BONE';obj.parent_bone='upper_arm.R';obj.matrix_world=Matrix.Translation(point)
bpy.context.view_layer.update();bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'robot_actions.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'robot_actions.glb'),export_format='GLB',use_selection=True,export_animation_mode='ACTIONS',export_force_sampling=True)
(OUT/'muzzle.json').write_text(json.dumps({'muzzle_blender_world':list(tip),'barrel_axis_blender_world':list(direction),'cap_vertices':len(cap),'bone':'upper_arm.R','scope':'geometry-derived sockets; native placement review required'},indent=2))
print('CANNON193_SOCKETS',list(tip),list(direction),flush=True)
