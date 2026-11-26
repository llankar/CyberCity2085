"""Combine retained source motions and the already-bound pistol into one portable model."""
from pathlib import Path
import bpy,json
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=LAB/'generated/phase2';OUT=ROOT/'armored203';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'unvanquished_weapon01/pistol_fit01/human_pistol.blend'))
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE' and len(o.data.bones)==122)
names=['Idle','Walk','Run','Attack','Death','Crouch'];wanted=['Baked_'+n for n in names]
with bpy.data.libraries.load(str(ROOT/'unvanquished_motion01/human_actions.blend'),link=False) as (available,loaded):
 loaded.actions=[n for n in wanted if n not in bpy.data.actions]
assert all(n in bpy.data.actions for n in wanted)
rig.animation_data_create();rig.animation_data.action=None
for track in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(track)
for alias in names+['Pistol_Attack_Study']:
 action=bpy.data.actions['Baked_'+alias];action.use_fake_user=True
 track=rig.animation_data.nla_tracks.new();track.name=alias;strip=track.strips.new(alias,0,action)
 if action.slots:strip.action_slot=action.slots[0]
for obj in scene.objects:obj.select_set(obj==rig or obj.type=='MESH')
bpy.context.view_layer.objects.active=rig;scene.frame_set(0)
notice=(ROOT/'unvanquished_weapon01/pistol_fit01/CREDITS.txt').read_text()+'\n203: existing authored body/pistol and six source motions combined; no retarget or geometry repaint.\n'
(OUT/'CREDITS.txt').write_text(notice,encoding='utf8')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'armored_actions.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'armored_actions.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(OUT/'assembly.json').write_text(json.dumps({'source_body':'unvanquished_weapon01/pistol_fit01/human_pistol.blend','source_motions':'unvanquished_motion01/human_actions.blend','clips':names+['Pistol_Attack_Study'],'scope':'self-contained existing authored meshes/materials/animations; no new AI generation or artistic acceptance'},indent=2));print('ARMORED203_ASSEMBLED',flush=True)
