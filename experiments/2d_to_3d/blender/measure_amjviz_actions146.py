"""Measure all seven real clips at original source key/midpoint cadence (48 Hz)."""
import hashlib,json,math
from pathlib import Path
import bpy
from mathutils import Matrix

folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/amjviz_actions146')
bpy.ops.wm.open_mainfile(filepath=str(folder/'human_actions.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
base=Matrix(json.loads((folder/'bake_report.json').read_text())['base_game_world'])
rig.animation_data.action=None
meshes=[o for o in scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
body=next(o for o in meshes if not o.name.startswith('EquippedPistol_'));references={}
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
    'blend_sha256':hashlib.sha256((folder/'human_actions.blend').read_bytes()).hexdigest()},indent=2))
print('AMJVIZ_ACTION_REFERENCES_READY',sum(len(s) for s in references.values()),flush=True)
