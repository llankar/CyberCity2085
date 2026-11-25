"""Ground only the two new retargeted clips against actual deformed body geometry."""
import bpy,sys,json,math,shutil,hashlib
from pathlib import Path
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb
from game_materials import restore
root=Path('E:/CyberCity2085-3d-lab/generated/phase2');folder=root/'motion_extension159'
for name in ('human.blend','human.glb','native_actions.json','native_reference.json'):
 backup=folder/('ungrounded_'+name)
 if not backup.exists():shutil.copy2(folder/name,backup)
bpy.ops.wm.open_mainfile(filepath=str(folder/'ungrounded_human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');body=max((o for o in scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
base=Matrix(json.loads((root/'amjviz_actions146/bake_report.json').read_text())['base_game_world']);report={}
for label in ('HitStudy','CoverStudy'):
 track=next(t for t in rig.animation_data.nla_tracks if t.name==label)
 for other in rig.animation_data.nla_tracks:other.mute=other!=track
 action=track.strips[0].action
 for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
 rig.matrix_world=base.copy()
 curves=[f for layer in action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]
 z=next(f for f in curves if f.data_path=='location' and f.array_index==2)
 offsets=[]
 for key in z.keyframe_points:
  frame=float(key.co.x);scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()
  evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();floor=min((evaluated.matrix_world@v.co).z for v in mesh.vertices);evaluated.to_mesh_clear()
  offsets.append(.001-floor)
 for key,delta in zip(z.keyframe_points,offsets):
  key.co.y+=delta;key.handle_left.y+=delta;key.handle_right.y+=delta
 z.update();report[label]={'samples':len(offsets),'minimum_root_z_adjustment_m':min(offsets),'maximum_root_z_adjustment_m':max(offsets),'target_floor_m':.001}
for track in rig.animation_data.nla_tracks:track.mute=track.name!='Hard stand'
rig.animation_data.action=None;rig.matrix_world=base.copy();scene.frame_set(0);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human.blend'))
for o in scene.objects:o.select_set(o==rig or o.type=='MESH')
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(folder/'human_ground_raw.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,export_rest_position_armature=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_optimize_animation_keep_anim_object=True,export_all_influences=True)
g=Glb(folder/'human_ground_raw.glb');restore(g,Glb(folder/'ungrounded_human.glb'));g.save(folder/'human.glb')
metadata=json.loads((folder/'motions.json').read_text());metadata.setdefault('ungrounded_variant_sha256',metadata['variant_sha256']);metadata['variant_sha256']=hashlib.sha256((folder/'human.glb').read_bytes()).hexdigest();metadata['grounding']=report;(folder/'motions.json').write_text(json.dumps(metadata,indent=2))
(folder/'grounding.json').write_text(json.dumps(report,indent=2));print('MOTION159_GROUNDED',json.dumps(report))
