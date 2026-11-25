"""Fit the real CC0 nine-part pistol from actual posed finger landmarks."""
import hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from grip_geometry import circle_center,grip_frame
from glb_document import Glb
from game_materials import restore

root=Path('E:/CyberCity2085-3d-lab/generated/phase2');animated='--animated' in sys.argv
out=root/('amjviz_actions146' if animated else 'amjviz_combat146')
pad_fit='--index-pad-fit' in sys.argv
stem='human_actions' if animated else ('shoot_equipped_pad' if pad_fit else 'shoot_equipped')
bpy.ops.wm.open_mainfile(filepath=str(out/('animated_unarmed.blend' if animated else 'shoot_pose.blend')),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE' and len(o.data.bones)==262)
if animated:
    for track in rig.animation_data.nla_tracks:track.mute=track.name!='ShootStudy'
    selected=next(t.strips[0] for t in rig.animation_data.nla_tracks if t.name=='ShootStudy')
    scene.frame_set(round((selected.frame_start+selected.frame_end)/2));bpy.context.view_layer.update()
def position(name):return rig.matrix_world@rig.pose.bones[name].matrix.translation
centers=[circle_center([list(position(f'DEF-f_{digit}.{joint:02d}.R')) for joint in (1,2,3)]) for digit in ('middle','ring','pinky')]
grip,basis=grip_frame(centers,position('DEF-forearm.R'),position('DEF-hand.R'))
placement=Matrix(basis.tolist()).to_4x4();anchor=Vector((0,-.012,.052))
placement.translation=Vector(grip)-placement.to_3x3()@anchor
relative=(rig.matrix_world@rig.pose.bones['DEF-hand.R'].matrix).inverted()@placement
bind=(rig.matrix_world@rig.data.bones['DEF-hand.R'].matrix_local)@relative
names={'Pistol','trigger','barrel','hammer','magazine (loaded)','9mm.001','9mm','slide','night sights'}
with bpy.data.libraries.load(str(root/'firewarden_pistol01/pistol.blend'),link=False) as (available,data):
    data.objects=[name for name in available.objects if name in names]
props=list(data.objects);assert len(props)==9
for prop in props:scene.collection.objects.link(prop)
bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();equipped=[]
body=next(o for o in scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers))
group=body.vertex_groups['DEF-f_index.03.R'];bone=rig.data.bones['DEF-f_index.03.R']
inverse=(rig.matrix_world@bone.matrix_local).inverted()
indices=[v.index for v in body.data.vertices if any(g.group==group.index and g.weight>.5 for g in v.groups)
         and (inverse@body.matrix_world@v.co).y>.7*bone.length]
assert indices,'Actual index-tip skin selection empty'
evaluated=body.evaluated_get(graph);mesh=evaluated.to_mesh()
tip_points=[evaluated.matrix_world@mesh.vertices[i].co for i in indices];evaluated.to_mesh_clear()
trigger=next(o for o in props if o.name=='trigger')
trigger_center=placement@trigger.matrix_world@(sum((v.co for v in trigger.data.vertices),Vector())/len(trigger.data.vertices))
tip=min(tip_points,key=lambda p:(p-trigger_center).length)
pad_delta=tip-trigger_center
if pad_fit:
    assert pad_delta.length<.08,'Contact fit would move weapon too far'
    placement.translation+=pad_delta
    relative=(rig.matrix_world@rig.pose.bones['DEF-hand.R'].matrix).inverted()@placement
    bind=(rig.matrix_world@rig.data.bones['DEF-hand.R'].matrix_local)@relative
for prop in props:
    mesh=bpy.data.meshes.new_from_object(prop.evaluated_get(graph),depsgraph=graph)
    mesh.transform((rig.data.bones['DEF-hand.R'].matrix_local@relative)@prop.matrix_world)
    obj=bpy.data.objects.new('EquippedPistol_'+prop.name,mesh);scene.collection.objects.link(obj)
    obj.parent=rig;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
    group=obj.vertex_groups.new(name='DEF-hand.R');group.add(list(range(len(mesh.vertices))),1.,'REPLACE')
    modifier=obj.modifiers.new('MeasuredWristBinding','ARMATURE');modifier.object=rig;equipped.append(obj)
for prop in props:scene.collection.objects.unlink(prop)
for obj in scene.objects:
    if obj.type=='ARMATURE' and obj!=rig:obj.hide_render=True;obj.hide_set(True)
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in obj.modifiers)))
bpy.context.view_layer.objects.active=rig;bpy.context.view_layer.update()
references={}
graph=bpy.context.evaluated_depsgraph_get()
for obj in scene.objects:
    if not obj.select_get() or obj.type!='MESH':continue
    evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
    points=[evaluated.matrix_world@v.co for v in mesh.vertices]
    references[obj.name.replace('.','_').replace(' ','_')]=[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
    evaluated.to_mesh_clear()
notice=(out/'CREDITS.txt').read_text(encoding='utf8')+'\nFireWarden Lowpoly Pistol; CC0 1.0; https://opengameart.org/content/lowpoly-pistol\n146 nine-part genuine source pistol fit from posed finger landmarks. No invented gameplay item. Contact/art acceptance pending.\n'
bpy.data.texts.new('WEAPON_CC0_NOTICE').write(notice)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/(stem+'.blend')))
if animated:
    for track in rig.animation_data.nla_tracks:track.mute=track.name!='T_pose'
    rig.animation_data.action=None
    rig.matrix_world=Matrix(json.loads((out/'bake_report.json').read_text())['base_game_world'])
    scene.frame_set(0);bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=str(out/(stem+'_raw.glb')),export_format='GLB',use_selection=True,
    export_animations=animated,export_current_frame=not animated,export_rest_position_armature=animated,
    export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,
    export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,
    export_optimize_animation_keep_anim_object=True,
    export_all_influences=True,export_copyright=notice)
compiled=Glb(out/(stem+'_raw.glb'));materials=restore(compiled,Glb(root/'amjviz_pruned145/human.glb'))
compiled.save(out/(stem+'.glb'));(out/'CREDITS_equipped.txt').write_text(notice,encoding='utf8')
(out/('equipped_pad_reference.json' if pad_fit else 'equipped_pose_reference.json')).write_text(json.dumps(references,indent=2))
(out/('weapon_fit_pad.json' if pad_fit else 'weapon_fit.json')).write_text(json.dumps({'bone':'DEF-hand.R','parts':9,'grip_world':list(grip),
    'index_tip_vertices':indices,'initial_index_trigger_distance_m':pad_delta.length,
    'index_pad_fit_enabled':pad_fit,'weapon_translation_delta_m':list(pad_delta) if pad_fit else [0,0,0],
    'relative_matrix':[list(row) for row in relative],'finger_circle_centers':[list(c) for c in centers],
    'material_restoration':materials,'glb_sha256':hashlib.sha256((out/(stem+'.glb')).read_bytes()).hexdigest(),
    'limitations':['Animation bundle requires native/artist review' if animated else 'Static pose only','Landmarks are not a contact solver','Trigger/support-hand contacts need visual inspection']},indent=2))
print('AMJVIZ_REAL_PISTOL_FIT_READY',list(grip),flush=True)
