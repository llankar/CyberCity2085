"""Create an editable, packed Blender companion for the shared five-clip GLB."""
import json
from pathlib import Path
import bpy

folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/einar_bundle02')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene; scene.render.fps=30
bpy.ops.import_scene.gltf(filepath=str(folder/'human_actions.glb'),merge_vertices=False)
rigs=[obj for obj in scene.objects if obj.type=='ARMATURE']
helpers={bone.custom_shape for rig in rigs for bone in rig.pose.bones if bone.custom_shape}
meshes=[obj for obj in scene.objects if obj.type=='MESH' and obj not in helpers]
for obj in helpers: obj.hide_render=True; obj.hide_set(True)
assert len(rigs)==1 and len(meshes)==76
assert len([bone for bone in rigs[0].data.bones if bone.name.startswith('J')])==222
expected={'Idle','Walk','Pistol_Shoot','Punch_Cross','Death01'}
owners=[*scene.objects,*[obj.data.shape_keys for obj in meshes if obj.data.shape_keys]]
tracks={}
for owner in owners:
    animation=owner.animation_data
    if not animation: continue
    names=[track.name for track in animation.nla_tracks]
    tracks[owner.name]=names
    animation.action=None
    for track in animation.nla_tracks: track.mute=track.name!='Idle'
assert set(tracks[rigs[0].name])==expected
assert all(set(names)==expected for name,names in tracks.items())
bpy.ops.file.pack_all()
unpacked=[image.name for image in bpy.data.images if image.source=='FILE' and not image.packed_file]
assert not unpacked,unpacked
scene.frame_start=0; scene.frame_end=72; scene.frame_set(0)
bpy.context.view_layer.objects.active=rigs[0]
for obj in scene.objects: obj.select_set(obj==rigs[0])
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human_actions.blend'))
report={'bones':222,'meshes':76,'fps':30,'nla_tracks_by_owner':tracks,
        'non_rendering_bone_shape_helpers':[obj.name for obj in helpers],
        'packed_images':sum(bool(image.packed_file) for image in bpy.data.images),
        'selected_clip':'Idle','remaining':'Blender re-export roundtrip not yet verified; artistic action quality not accepted'}
(folder/'blender_import_check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('EINAR_BUNDLE_BLENDER_SAVED',len(tracks),report['packed_images'],flush=True)
