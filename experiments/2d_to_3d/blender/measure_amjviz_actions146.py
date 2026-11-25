"""Measure all seven real clips at original source key/midpoint cadence (48 Hz)."""
import hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Matrix

folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/amjviz_actions146')
base_folder=folder
hair_study='--hair-study' in sys.argv
support_study='--support-study' in sys.argv
skin_study='--sole-skin162' in sys.argv
foot_study=skin_study or '--foot-lock161' in sys.argv
transition_study='--cover-transitions160' in sys.argv or foot_study
motion_study='--motion-extension159' in sys.argv or transition_study
wardrobe_study='--wardrobe150-study' in sys.argv or motion_study
assert sum([hair_study,support_study,wardrobe_study])<=1
if hair_study:folder=folder.parent/'amjviz_hair148'
if support_study:folder=folder.parent/'amjviz_grip149'
if wardrobe_study:folder=folder.parent/'amjviz_wardrobe150'
if motion_study:folder=folder.parent/('sole_skin162' if skin_study else ('foot_contact161' if foot_study else ('cover_transitions160' if transition_study else 'motion_extension159')))
blend_path=folder/('human.blend' if hair_study or motion_study else 'human_actions.blend')
bpy.ops.wm.open_mainfile(filepath=str(blend_path),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
base=Matrix(json.loads((base_folder/'bake_report.json').read_text())['base_game_world'])
rig.animation_data.action=None
meshes=[o for o in scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
body=max(meshes,key=lambda o:len(o.data.vertices));references={}
for track in rig.animation_data.nla_tracks:
    for other in rig.animation_data.nla_tracks:other.mute=other!=track
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    rig.matrix_world=base.copy();strip=track.strips[0]
    start,end=strip.frame_start,strip.frame_end
    intervals=max(1,math.ceil((end-start)/2.5));samples=[]
    for i in range(intervals+1):
        frame=start+(end-start)*i/intervals
        scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()
        graph=bpy.context.evaluated_depsgraph_get();boxes={}
        for obj in meshes:
            evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
            points=[evaluated.matrix_world@v.co for v in mesh.vertices]
            boxes[obj.name.replace('.','_').replace(' ','_')]=[[min(p[j] for p in points) for j in range(3)],[max(p[j] for p in points) for j in range(3)]]
            evaluated.to_mesh_clear()
        samples.append({'time_s':frame/scene.render.fps,'mesh_bounds_blender':boxes})
    references[track.name]=samples
    print('AMJVIZ_ACTION_REFERENCE',track.name,len(samples),flush=True)
(folder/'native_reference.json').write_text(json.dumps({'clips':references,'fps':scene.render.fps,
    'body_name':body.name.replace('.','_').replace(' ','_'),'sample_cadence_hz':48,
    'blend_sha256':hashlib.sha256(blend_path.read_bytes()).hexdigest()},indent=2))
print('AMJVIZ_ACTION_REFERENCES_READY',sum(len(s) for s in references.values()),flush=True)
