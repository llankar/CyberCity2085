"""Re-export the saved editable action rig; never overwrite the source evidence."""
import hashlib,json,shutil
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'unvanquished_motion01';out=root/'unvanquished_roundtrip01';out.mkdir(exist_ok=True)
blend=source/'human_actions.blend';before=hashlib.sha256(blend.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(blend),use_scripts=False)
scene=bpy.data.scenes['AuthoredGameActions'];bpy.context.window.scene=scene
rig=bpy.data.objects['AuthoredGameRig']
for track in rig.animation_data.nla_tracks:track.mute=False
for obj in scene.objects:obj.select_set(True)
bpy.context.view_layer.objects.active=rig
notice=bpy.data.texts['AUTHORED_ACTION_CREDITS'].as_string()
bpy.ops.export_scene.gltf(filepath=str(out/'human_actions.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_keep_anim_armature=True,export_extras=True,export_copyright=notice)
assert hashlib.sha256(blend.read_bytes()).hexdigest()==before,'Source Blender file changed'
shutil.copyfile(source/'source_surface_reference.json',out/'source_surface_reference.json')
shutil.copyfile(source/'CREDITS.txt',out/'CREDITS.txt')
(out/'roundtrip_report.json').write_text(json.dumps({'source_blend_sha256':before,'source_glb_sha256':hashlib.sha256((source/'human_actions.glb').read_bytes()).hexdigest(),'roundtrip_glb_sha256':hashlib.sha256((out/'human_actions.glb').read_bytes()).hexdigest(),'tracks':[t.name for t in rig.animation_data.nla_tracks],'source_blend_unchanged':True},indent=2))
print('AUTHORED_HUMAN_BLEND_REEXPORTED',flush=True)
