"""Controlled explicit tangent-frame export; geometry/material source unchanged."""
import hashlib,json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'rook_single_neck138';out=root/'rook_tangents139';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for o in scene.objects:o.select_set(o==rig or (o.type=='MESH' and o not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text()+'\n139diagnostic: explicitly exported glTF tangent frames, original source normal texture retained. Not artistic acceptance.\n'
for tangents,name in [(False,'control'),(True,'explicit')]:
    bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),export_format='GLB',use_selection=True,
        export_apply=True,export_tangents=tangents,export_animations=True,export_animation_mode='NLA_TRACKS',
        export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,
        export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf-8')
(out/'export_report.json').write_text(json.dumps({'source_blend_sha256':hashlib.sha256((source/'human.blend').read_bytes()).hexdigest(),
    'control_sha256':hashlib.sha256((out/'control.glb').read_bytes()).hexdigest(),
    'explicit_sha256':hashlib.sha256((out/'explicit.glb').read_bytes()).hexdigest(),
    'scope':'Controlled export setting only; source meshes and original photograph/normal/specular textures unchanged'},indent=2))
print('ROOK_TANGENT_AB_EXPORT_FINISHED',flush=True)
