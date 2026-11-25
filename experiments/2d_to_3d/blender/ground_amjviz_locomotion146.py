"""Keep authored limb motion while removing measured below-floor boot placement."""
import json,math
from pathlib import Path
import bpy
from mathutils import Matrix

folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/amjviz_actions146')
report=json.loads((folder/'bake_report.json').read_text());base=Matrix(report['base_game_world'])
bpy.ops.wm.open_mainfile(filepath=str(folder/'animated_unarmed.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
body=next(o for o in scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers))
for track in rig.animation_data.nla_tracks:track.mute=True
actions={s.action.name:s.action for t in rig.animation_data.nla_tracks for s in t.strips}
results={}
for name in ('Walk (1_24)','Run (1_18)'):
    action=actions[name];rig.animation_data.action=action
    if action.slots:rig.animation_data.action_slot=action.slots[0]
    start,end=action.frame_range;count=max(1,round(end-start));worst=0.
    for i in range(count+1):
        frame=start+(end-start)*i/count
        scene.frame_set(math.floor(frame),subframe=frame%1)
        rig.matrix_world=base.copy();rig.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
        evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        floor=min((evaluated.matrix_world@v.co).z for v in mesh.vertices);evaluated.to_mesh_clear()
        lift=max(0.,.001-floor);worst=max(worst,lift)
        matrix=base.copy();matrix.translation.z+=lift;rig.matrix_world=matrix
        rig.keyframe_insert('location',frame=frame,group='ExportFloorPlacement')
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    if curve.data_path=='location':
                        for key in curve.keyframe_points:key.interpolation='LINEAR'
    results[name]={'samples':count+1,'maximum_export_floor_lift_m':worst,
                   'scope':'Whole-actor vertical export placement only; authored bone curves unchanged'}
    print('AMJVIZ_LOCOMOTION_FLOOR_PLACEMENT',name,worst,flush=True)
rig.animation_data.action=None;rig.matrix_world=base.copy()
for track in rig.animation_data.nla_tracks:track.mute=track.name!='T_pose'
scene.frame_set(0);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'animated_unarmed.blend'))
report['original_locomotion_floor_placement']=results
(folder/'bake_report.json').write_text(json.dumps(report,indent=2))
