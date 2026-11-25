"""Create an editable game-rig source from the verified author's pruned GLB."""
import hashlib,json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2/amjviz_pruned145')
proof=json.loads((root/'native_equivalence.json').read_text())
assert proof['maximum_vertex_error_m']<=.000001
assert proof['candidate_sha256']==hashlib.sha256((root/'human.glb').read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(root/'human.glb'),import_pack_images=True)
rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];assert len(rigs)==1
rig=rigs[0];assert len(rig.data.bones)==262
assert all(b.bbone_segments==1 for b in rig.data.bones)
if rig.animation_data:
    rig.animation_data.action=None
    for track in rig.animation_data.nla_tracks:track.mute=True
bpy.context.scene.render.fps=24;bpy.context.scene.frame_set(0)
notice=(root/'CREDITS.txt').read_text(encoding='utf8')+'\n145 editable game rig imported from exact-equivalent author game GLB. Original high-level Rigify source remains separately preserved. No new combat clips yet.\n'
bpy.data.texts.new('PRIVATE_GAME_SOURCE_LICENSE').write(notice)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(root/'human.blend'))
images=[image for image in bpy.data.images if image.source=='FILE']
assert all(image.packed_file for image in images)
report={'bones':len(rig.data.bones),'all_linear_bones':True,
        'actions':[a.name for a in bpy.data.actions],
        'bone_constraints':sum(len(b.constraints) for b in rig.pose.bones),
        'embedded_source_scripts_executed':False,
        'packed_file_images':len(images),'missing_external_textures':[],
        'blend_sha256':hashlib.sha256((root/'human.blend').read_bytes()).hexdigest(),
        'scope':'Editable game source; not exact original Rigify B-Bone evaluation or final Rook'}
(root/'blender_game_source.json').write_text(json.dumps(report,indent=2))
print('AMJVIZ_EDITABLE_GAME_SOURCE_READY',json.dumps(report),flush=True)
