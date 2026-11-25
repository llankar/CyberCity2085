"""Audit the licensed animation skeleton in the actual installed Blender importer."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/sources/quaternius_ual_standard')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(root/'Unreal-Godot/UAL1_Standard.glb'))
rigs=[obj for obj in bpy.context.scene.objects if obj.type=='ARMATURE']
assert len(rigs)==1
rig=rigs[0]
report={'rig':rig.name,'scale':list(rig.scale),'fps':bpy.context.scene.render.fps,
        'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,
                  'head':list(rig.matrix_world @ b.head_local),'tail':list(rig.matrix_world @ b.tail_local)} for b in rig.data.bones],
        'actions':[{'name':a.name,'frames':list(a.frame_range)} for a in bpy.data.actions],
        'nla':[{'name':t.name,'mute':t.mute} for t in rig.animation_data.nla_tracks]}
(root/'blender_inventory.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'animation_library.blend'))
print('UAL_BLENDER_IMPORT_OK',rig.name,len(rig.data.bones),len(bpy.data.actions),flush=True)
