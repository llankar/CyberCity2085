"""Measure actual hand landmarks in the retargeted firing pose."""
import json
from pathlib import Path
import bpy
root=Path('E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03/motion01')
bpy.ops.wm.open_mainfile(filepath=str(root/'human_motion.blend'),use_scripts=False)
rig=bpy.data.objects['Bip01']
for track in rig.animation_data.nla_tracks: track.mute=track.name!='Pistol_Shoot'
bpy.context.scene.frame_set(9); bpy.context.view_layer.update()
points={bone.name:list(rig.matrix_world @ bone.matrix.translation) for bone in rig.pose.bones
        if any(word in bone.name for word in ['Forearm','Hand','Finger'])}
(root/'grip_landmarks.json').write_text(json.dumps(points,indent=2),encoding='utf-8')
for name,point in points.items():
    if name.startswith('Bip01 R'): print(name,point,flush=True)
