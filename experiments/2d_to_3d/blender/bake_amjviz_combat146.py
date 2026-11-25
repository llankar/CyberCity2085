"""Bake licensed combat motion through source FK controls onto the genuine game rig."""
import json,math,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from amjviz_fk import load,solve,stabilize_original_locations

c=load();out=c.root/'generated/phase2/amjviz_actions146';out.mkdir(exist_ok=True)
game=c.game;scene=c.scene;fps=120;scene.render.fps=fps
originals={s.action.name:s.action for t in game.animation_data.nla_tracks for s in t.strips}
for track in list(game.animation_data.nla_tracks):game.animation_data.nla_tracks.remove(track)
for action in originals.values():
    action.use_fake_user=True
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:
                        key.co.x*=5;key.handle_left.x*=5;key.handle_right.x*=5
for bone in game.pose.bones:bone.rotation_mode='QUATERNION'
body=next(o for o in scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==game for m in o.modifiers))
reports={};actions=dict(originals)
for label,source in [('ShootStudy','Pistol_Shoot'),('MeleeStudy','Punch_Cross'),('DeathStudy','Death01')]:
    source_action=c.clips[source];first,last=source_action.frame_range
    duration=(last-first)/24.;frames=max(1,round(duration*fps))
    action=bpy.data.actions.new(label);action.use_fake_user=True;game.animation_data.action=action
    previous={};worst=0.;max_lift=0.
    for sample in range(frames+1):
        frame=first+(last-first)*sample/frames
        worst=max(worst,solve(c,source,frame))
        evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        floor=min((evaluated.matrix_world@v.co).z for v in mesh.vertices);evaluated.to_mesh_clear()
        lift=max(0.,.001-floor);max_lift=max(max_lift,lift)
        matrix=c.game_world.copy();matrix.translation.z+=lift;game.matrix_world=matrix
        for bone in game.pose.bones:
            if bone.name in previous:bone.rotation_quaternion.make_compatible(previous[bone.name])
            previous[bone.name]=bone.rotation_quaternion.copy()
            for channel in ('location','rotation_quaternion','scale'):bone.keyframe_insert(channel,frame=sample,group=bone.name)
        game.keyframe_insert('location',frame=sample,group='ExportFloorPlacement')
        if sample%30==0:print('AMJVIZ_COMBAT_BAKE_PROGRESS',label,sample,frames,flush=True)
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
    actions[label]=action
    reports[label]={'source_clip':source,'source_frames':[first,last],'source_fps':24,
                    'duration_s':frames/fps,'samples':frames+1,'maximum_transfer_head_error_m':worst,
                    'maximum_export_floor_lift_m':max_lift}
    print('AMJVIZ_COMBAT_CLIP_BAKED',label,json.dumps(reports[label]),flush=True)
neutral_locations=stabilize_original_locations(game,originals,c.game_world)
game.animation_data.action=None;game.matrix_world=c.game_world.copy()
for label,action in actions.items():
    start,end=action.frame_range
    track=game.animation_data.nla_tracks.new();track.name=label
    strip=track.strips.new(label,0,action);strip.action_frame_start=start;strip.action_frame_end=max(end,start+.001)
    strip.frame_start=start;strip.frame_end=max(end,start+.001);strip.influence=1.;track.mute=label!='T_pose'
for obj in (c.driver,c.motion):bpy.data.objects.remove(obj,do_unlink=True)
for text in list(bpy.data.texts):
    if text.name.startswith('rig_ui'):bpy.data.texts.remove(text)
scene.frame_set(0);bpy.context.view_layer.update()
notice=(c.base/'CREDITS.txt').read_text(encoding='utf8')+'\n'+(c.root/'sources/quaternius_ual_standard/License.txt').read_text(encoding='utf8')+'\n146 derived game-rig motion study; UAL Pistol_Shoot/Punch_Cross/Death01, via original FK controls. Native interpolation, art/contacts not yet accepted. Small whole-actor floor lifts are export placement, not tactical rule changes.\n'
text=bpy.data.texts.new('PRIVATE_COMBAT_STUDY_LICENSE');text.write(notice);text.use_fake_user=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'animated_unarmed.blend'))
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'bake_report.json').write_text(json.dumps({'fps':fps,'base_game_world':[list(row) for row in c.game_world],
    'clips':reports,'preserved_source_action_names':list(originals),'added_source_base_location_tracks':neutral_locations,
    'scope':'Actual authored FK motion bake; no new characters, no native/art acceptance yet'},indent=2))
print('AMJVIZ_COMBAT_BAKE_READY',list(actions),flush=True)
