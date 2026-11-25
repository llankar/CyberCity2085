"""Bake actual authored humanoid poses onto a constraint-free shared game rig."""
import json,sys,math
from pathlib import Path
import bpy
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).parent.parent))
from authored_action_ranges import source_action_ranges
root=Path('E:/CyberCity2085-3d-lab');folder=root/'generated/phase2/unvanquished_motion01';folder.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'generated/phase2/unvanquished_human01/human_armor.blend'),use_scripts=False)
source_scene=bpy.context.scene;source_rig=bpy.data.objects['Armature'];source_rig.data.pose_position='POSE'
source_meshes=[o for o in source_scene.objects if o.type=='MESH']
assert len(source_meshes)==21
baseline={b.name:b.matrix_basis.copy() for b in source_rig.pose.bones}
properties={b.name:{k:b[k] for k in b.keys() if isinstance(b[k],(int,float))} for b in source_rig.pose.bones}
ranges=source_action_ranges((root/'sources/unvanquished_human/animations.txt').read_text())
selected={'Idle':'idle','Walk':'walk','Run':'run','Attack':'attack','Death':'die','Crouch':'crouch'}
game_scene=bpy.data.scenes.new('AuthoredGameActions');game_scene.render.fps=120
bpy.context.window.scene=game_scene
game=source_rig.copy();game.data=source_rig.data.copy();game.name='AuthoredGameRig';game.animation_data_clear();game_scene.collection.objects.link(game)
game.data.pose_position='POSE'
for bone in game.pose.bones:
 for constraint in list(bone.constraints):bone.constraints.remove(constraint)
 bone.rotation_mode='QUATERNION'
meshes=[]
for obj in source_meshes:
 clone=obj.copy();clone.data=obj.data.copy();clone.name='Game_'+obj.name;clone.parent=game
 for modifier in clone.modifiers:
  if modifier.type=='ARMATURE':modifier.object=game
 game_scene.collection.objects.link(clone);meshes.append(clone)
references={};reports={};max_bake_error=0.;max_surface_error=0.
for alias,original in selected.items():
 info=ranges[original];first,last,fps=info['first'],info['last'],info['fps']
 bpy.context.window.scene=source_scene
 source_rig.animation_data.action=None
 for bone in source_rig.pose.bones:
  bone.matrix_basis=baseline[bone.name]
  for key,value in properties[bone.name].items():bone[key]=value
 source_rig.animation_data.action=bpy.data.actions[original]
 bpy.context.window.scene=game_scene
 for track in game.animation_data.nla_tracks if game.animation_data else []:track.mute=True
 game.animation_data_create();game.animation_data.action=bpy.data.actions.new('Baked_'+alias)
 previous={};samples=[];sample_frames={round(first+(last-first)*i/8) for i in range(9)}
 for source_frame in range(first,last+1):
  bpy.context.window.scene=source_scene;source_scene.frame_set(source_frame);bpy.context.view_layer.update()
  graph=bpy.context.evaluated_depsgraph_get();evaluated=source_rig.evaluated_get(graph)
  poses={b.name:b.matrix.copy() for b in evaluated.pose.bones}
  if source_frame in sample_frames:
   geometry={}
   for obj in source_meshes:
    e=obj.evaluated_get(graph);mesh=e.to_mesh()
    geometry['Game_'+obj.name]=[list(e.matrix_world@mesh.vertices[i].co) for i in range(0,len(mesh.vertices),max(1,len(mesh.vertices)//12))];e.to_mesh_clear()
   samples.append({'time_s':(source_frame-first)/fps,'meshes':geometry})
  bpy.context.window.scene=game_scene;game_scene.frame_set(source_frame-first)
  for bone in game.pose.bones:
   arguments={'matrix':poses[bone.name],'matrix_local':bone.bone.matrix_local,'invert':True}
   if bone.parent:arguments.update(parent_matrix=poses[bone.parent.name],parent_matrix_local=bone.parent.bone.matrix_local)
   bone.matrix_basis=bone.bone.convert_local_to_pose(**arguments)
   quaternion=bone.rotation_quaternion.copy()
   if bone.name in previous and quaternion.dot(previous[bone.name])<0:quaternion.negate();bone.rotation_quaternion=quaternion
   previous[bone.name]=quaternion.copy()
   for path in ['location','rotation_quaternion','scale']:bone.keyframe_insert(path,frame=source_frame-first)
  bpy.context.view_layer.update()
  error=max(max(abs(a-b) for row1,row2 in zip(b.matrix,poses[b.name]) for a,b in zip(row1,row2)) for b in game.pose.bones)
  max_bake_error=max(max_bake_error,error)
  # Constraint stretch can contain shear that Blender pose TRS cannot encode.
  # Measure actual evaluated skin, independently of dimensionless bone matrices.
  if source_frame in sample_frames:
   game_graph=bpy.context.evaluated_depsgraph_get()
   for obj in meshes:
    e=obj.evaluated_get(game_graph);m=e.to_mesh()
    indices=list(range(0,len(m.vertices),max(1,len(m.vertices)//12)))
    expected=geometry[obj.name]
    surface_error=max((e.matrix_world@m.vertices[i].co-Matrix.Translation(point).translation).length for i,point in zip(indices,expected))
    max_surface_error=max(max_surface_error,surface_error)
    assert surface_error<.002,('Skin bake mismatch metres',alias,source_frame,obj.name,surface_error)
    e.to_mesh_clear()
 action=game.animation_data.action
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for curve in bag.fcurves:
     for key in curve.keyframe_points:key.interpolation='LINEAR'
 track=game.animation_data.nla_tracks.new();track.name=alias
 strip=track.strips.new(alias,0,action);strip.scale=120/fps
 game.animation_data.action=None
 references[alias]=samples;reports[alias]={'source_action':original,'source_frames':[first,last],'source_fps':fps,'duration_s':(last-first)/fps,'baked_frames':last-first+1,'game_strip_frames':[strip.frame_start,strip.frame_end]}
 print('UNV_POSE_ACTION_BAKED',alias,last-first+1,flush=True)
bpy.context.window.scene=game_scene
for track in game.animation_data.nla_tracks:track.mute=False
game_scene.frame_start=0;game_scene.frame_end=round(max(r['duration_s'] for r in reports.values())*120)
for obj in game_scene.objects:obj.select_set(True)
bpy.context.view_layer.objects.active=game
notice=(root/'generated/phase2/unvanquished_human01/CREDITS.txt').read_text()+'\nAdded: source-author export ranges and evaluated visual pose bake on shared122bone game rig; source game hand/torso composition not yet adopted. Derivative CC BY-SA3.0.\n'
bpy.data.texts.new('AUTHORED_ACTION_CREDITS').write(notice)
bpy.ops.export_scene.gltf(filepath=str(folder/'human_actions.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_keep_anim_armature=True,export_extras=True,export_copyright=notice)
for track in game.animation_data.nla_tracks:track.mute=track.name!='Idle'
game_scene.frame_set(0);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human_actions.blend'))
(folder/'source_surface_reference.json').write_text(json.dumps(references))
(folder/'motion_report.json').write_text(json.dumps({'clips':reports,'max_baked_pose_matrix_error':max_bake_error,'max_sampled_skin_error_m':max_surface_error,'bones':122,'meshes':21,'credits':notice,'limitations':['Authored body clips only; segmented/HandDelta game composition and weapon grip not yet accepted','No fabricated melee/cover/heal/PSI','Legacy specular/PBR and identity remain unaccepted']},indent=2))
(folder/'CREDITS.txt').write_text(notice,encoding='utf8')
print('UNV_SHARED_AUTHORED_ACTIONS_EXPORTED',len(reports),max_bake_error,flush=True)



