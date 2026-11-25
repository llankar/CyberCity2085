"""Reuse authored spell/kneeling interaction for private tactical visual demo.

24fps bake, no campaign logic. Medical adaptation needs prop/recipient staging;
the source kneeling interaction is not claimed to be an authored medical clip.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0,str(Path(__file__).parent.parent))
import bpy
from amjviz_fk import load, solve
from glb_document import Glb
from game_materials import restore

c=load()
root=c.root/'generated/phase2'
out=root/'support167';out.mkdir(exist_ok=True)
for track in list(c.game.animation_data.nla_tracks):
    c.game.animation_data.nla_tracks.remove(track)
actions=[]
for label,source in [('PsiCast','Spell_Simple_Shoot'),('MedicalAidPrototype','Fixing_Kneeling')]:
    first,last=c.clips[source].frame_range
    count=max(1,round(last-first))
    action=bpy.data.actions.new(label);action.use_fake_user=True
    c.game.animation_data.action=action
    previous={}
    for frame in range(count+1):
        solve(c,source,first+(last-first)*frame/count)
        for bone in c.game.pose.bones:
            if bone.name in previous:bone.rotation_quaternion.make_compatible(previous[bone.name])
            previous[bone.name]=bone.rotation_quaternion.copy()
            for channel in ('location','rotation_quaternion','scale'):
                bone.keyframe_insert(channel,frame=frame,group=bone.name)
    actions.append(action)
    print('SUPPORT_ACTION_BAKED',label,count+1,flush=True)
bpy.data.libraries.write(str(out/'actions.blend'),set(actions),fake_user=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'sole_skin162/human.blend'))
with bpy.data.libraries.load(str(out/'actions.blend'),link=False) as (src,dst):
    dst.actions=src.actions
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
rig.animation_data_create();rig.animation_data.action=None
for action in dst.actions:
    action.use_fake_user=True
    start,end=action.frame_range
    track=rig.animation_data.nla_tracks.new();track.name=action.name
    strip=track.strips.new(action.name,int(start),action)
    strip.action_frame_start=start;strip.action_frame_end=end
    strip.frame_start=start;strip.frame_end=end
    track.mute=True
previous_fps=bpy.context.scene.render.fps/bpy.context.scene.render.fps_base
bpy.context.scene.render.fps=24
# Existing 120fps actions retain their original playback through NLA time scaling.
for track in rig.animation_data.nla_tracks:
    if track.name not in ['PsiCast','MedicalAidPrototype']:
        for strip in track.strips:
            strip.scale *= 24/previous_fps
for obj in bpy.context.scene.objects:obj.select_set(obj==rig or obj.type=='MESH')
bpy.context.view_layer.objects.active=rig
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'raw.glb'),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,
    export_frame_range=False,export_optimize_animation_size=False)
g=Glb(out/'raw.glb');restore(g,Glb(root/'sole_skin162/human.glb'));g.save(out/'human.glb')
(out/'CREDITS.txt').write_text((root/'sole_skin162/CREDITS.txt').read_text(encoding='utf8')+
    '\n167 PSI: Quaternius CC0 Spell_Simple_Shoot. MedicalAidPrototype: adaptation of CC0 Fixing_Kneeling, medical staging required, not final medical animation. Existing motion durations preserved. Private scene only.\n',encoding='utf8')
print('SUPPORT167_EXPORTED',flush=True)
