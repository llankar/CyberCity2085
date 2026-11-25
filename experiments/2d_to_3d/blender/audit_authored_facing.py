"""Measure the actual authored eye/head forward, without changing either asset."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/unvanquished_motion01')
bpy.ops.wm.open_mainfile(filepath=str(folder/'human_actions.blend'),use_scripts=False)
scene=bpy.data.scenes['AuthoredGameActions'];bpy.context.window.scene=scene
rig=bpy.data.objects['AuthoredGameRig']
report={}
for clip in ['Idle','Walk','Run','Attack','Crouch']:
    for track in rig.animation_data.nla_tracks:track.mute=track.name!=clip
    scene.frame_set(0);bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    def points(name):
        obj=bpy.data.objects[name].evaluated_get(graph);mesh=obj.to_mesh()
        result=[obj.matrix_world@v.co for v in mesh.vertices];obj.to_mesh_clear()
        return result
    head=points('Game_head')
    center=Vector([(min(p[i] for p in head)+max(p[i] for p in head))/2 for i in range(3)])
    eyes=points('Game_eye.L')+points('Game_eye.R')
    eye_center=sum(eyes,Vector())/len(eyes)
    direction=eye_center-center;direction.z=0
    assert direction.length>.005,'Cannot infer anatomical facing from this geometry'
    direction.normalize()
    report[clip]={'head_bbox_center_blender_m':list(center),'eye_surface_centroid_blender_m':list(eye_center),'horizontal_anatomical_forward_blender':list(direction),'horizontal_anatomical_forward_godot':[direction.x,direction.z,-direction.y]}
(folder/'anatomical_facing_audit.json').write_text(json.dumps(report,indent=2))
print('UNV_EYE_HEAD_FACING_AUDIT',json.dumps(report),flush=True)
