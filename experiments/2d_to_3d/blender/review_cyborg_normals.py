"""Isolate stale custom normals after collapse; do not alter lighting/vertices."""
import hashlib
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'rook_normals01';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_material01/human.blend'),use_scripts=False)
body=bpy.data.objects['char1']
positions=[tuple(v.co) for v in body.data.vertices]
body.data.normals_split_custom_set([(0,0,0)]*len(body.data.loops))
for face in body.data.polygons:face.use_smooth=True
body.data.update()
assert positions==[tuple(v.co) for v in body.data.vertices]
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
helpers={bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
for obj in bpy.context.scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=(root/'rook_material01/CREDITS.txt').read_text())
(out/'normal_review.json').write_text(json.dumps({'positions_unchanged':True,'change':'Clear custom split normals; smooth geometric normals, original texture maps and lighting retained','glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'artistic_acceptance':'NOT VERIFIED'},indent=2),encoding='utf8')
print('CYBORG_GEOMETRIC_NORMAL_REVIEW_READY',flush=True)
