"""Measured real CC0 pistol fit on the source-specific composed hand pose."""
import json,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from grip_geometry import circle_center,grip_frame

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
scanned_shoot='--scanned-shoot' in sys.argv
source=root/('scanned_armor_shoot01' if scanned_shoot else 'unvanquished_weapon01');out=source/'pistol_fit01';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human_actions.blend'),use_scripts=False)
scene=bpy.data.scenes['AuthoredGameActions'];bpy.context.window.scene=scene
rig=bpy.data.objects['AuthoredGameRig'];scene.frame_set(8);bpy.context.view_layer.update()
if scanned_shoot:
 for track in list(rig.animation_data.nla_tracks):
  if track.name!='Shoot':rig.animation_data.nla_tracks.remove(track)
  else:track.mute=False
 scene.frame_set(8);bpy.context.view_layer.update()
def position(name):return rig.matrix_world@rig.pose.bones[name].matrix.translation
centers=[circle_center([list(position('finger_'+digit+'.0'+str(j)+'.R')) for j in [1,2,3]]) for digit in ['middle','ring','pinky']]
grip,basis=grip_frame(centers,position('forearm.R'),position('hand.R'))
anchor=Vector((0,-.012,.052))
placement=Matrix(basis.tolist()).to_4x4();placement.translation=Vector(grip)-placement.to_3x3()@anchor
relative=(rig.matrix_world@rig.pose.bones['hand.R'].matrix).inverted()@placement
conversion=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
placement_yup=conversion@placement@conversion.inverted()
with bpy.data.libraries.load(str(root/'firewarden_pistol01/pistol.blend'),link=False) as (available,loaded):
 loaded.objects=[name for name in available.objects if name in {'Pistol','trigger','barrel','hammer','magazine (loaded)','9mm.001','9mm','slide','night sights'}]
props=list(loaded.objects);assert len(props)==9
for prop in props:scene.collection.objects.link(prop)
bpy.context.view_layer.update()
reference=[]
for frame in range(0,17,1 if scanned_shoot else 2):
 scene.frame_set(frame);bpy.context.view_layer.update()
 current=rig.matrix_world@rig.pose.bones['hand.R'].matrix@relative
 reference.append({'time_s':frame/120,'parts':{'EquippedPistol_'+p.name:[list(current@p.matrix_world@v.co) for v in p.data.vertices] for p in props}})
scene.frame_set(8);bpy.context.view_layer.update()
bind=rig.matrix_world@rig.data.bones['hand.R'].matrix_local@relative
graph=bpy.context.evaluated_depsgraph_get();equipped=[]
for prop in props:
 mesh=bpy.data.meshes.new_from_object(prop.evaluated_get(graph),depsgraph=graph)
 mesh.transform(bind@prop.matrix_world)
 obj=bpy.data.objects.new('EquippedPistol_'+prop.name,mesh);scene.collection.objects.link(obj)
 obj.parent=rig;obj.matrix_world=Matrix.Identity(4)
 group=obj.vertex_groups.new(name='hand.R');group.add(list(range(len(mesh.vertices))),1,'REPLACE')
 modifier=obj.modifiers.new('MeasuredWristBinding','ARMATURE');modifier.object=rig
 equipped.append(obj)
for prop in props:scene.collection.objects.unlink(prop)
for obj in scene.objects:obj.select_set(obj==rig or obj.type=='MESH')
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text()+'\nWeapon: FireWarden Lowpoly Pistol CC0 1.0 https://opengameart.org/content/lowpoly-pistol\nMeasured finger-landmark fit, not accepted hand-contact solution.\n'
bpy.data.texts.new('EQUIPPED_WEAPON_CREDITS').write(notice)
# Portable equipped study is deliberately Shoot-only; body GLB retains seven
# actions and the native stage attaches/hides this real prop explicitly.
if scanned_shoot:
 for track in rig.animation_data.nla_tracks:track.mute=track.name!='Shoot'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human_pistol.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human_pistol.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_keep_anim_armature=True,export_extras=True,export_copyright=notice)
(out/'weapon_surface_reference.json').write_text(json.dumps(reference))
(out/'fit_report.json').write_text(json.dumps({'bone':'hand.R','clip':'Shoot' if scanned_shoot else 'Pistol_Attack_Study','reference_time_s':8/120,'finger_circle_centers':[list(c) for c in centers],'grip_world':list(grip),'relative_blender':[list(row) for row in relative],'world_placement_blender':[list(row) for row in placement],'world_placement_yup':[list(row) for row in placement_yup],'parts':len(equipped),'weapon_source':'FireWarden Lowpoly Pistol CC0','limitations':['Bone circle fit is not finger/trigger contact validation','Source game parity and modern Rook identity not accepted']},indent=2))
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
print('UNV_MEASURED_PISTOL_FIT',list(grip),len(equipped),flush=True)
