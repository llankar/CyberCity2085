"""Export only deform bones and measure original authored poses before export."""
import hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Matrix

root=Path('E:/CyberCity2085-3d-lab');source=root/'sources/blenderkit_cyberpunk143'
out=root/'generated/phase2/amjviz_runtime144';out.mkdir(exist_ok=True)
full_diagnostic='--all-bones-diagnostic' in sys.argv
if full_diagnostic:
    out=root/'generated/phase2/amjviz_full144';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'source.blend'),use_scripts=False)
scene=bpy.context.scene;rig=bpy.data.objects['rig'];body=bpy.data.objects['Character']
linear_diagnostic='--linear-diagnostic' in sys.argv
if linear_diagnostic:
    for bone in rig.data.bones:bone.bbone_segments=1
# The first source Armature modifier has no target; remove only that no-op.
removed=[]
for modifier in list(body.modifiers):
    if modifier.type=='ARMATURE' and modifier.object is None:
        removed.append(modifier.name);body.modifiers.remove(modifier)
assert len(removed)==1
tracks=list(rig.animation_data.nla_tracks);originals=[]
for track in tracks:
    assert len(track.strips)==1
    strip=track.strips[0];originals.append((track,strip,strip.action))
    track.name=strip.action.name;track.mute=True
references={}
for track,strip,action in originals:
    if '--reset-reference' in sys.argv:
        for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    rig.animation_data.action=action
    if action.slots:rig.animation_data.action_slot=action.slots[0]
    start,end=strip.action_frame_start,strip.action_frame_end
    samples=[]
    for step in range(round((end-start)*2)+1):
        frame=start+step/2
        scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()
        evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        points=[evaluated.matrix_world@v.co for v in mesh.vertices]
        samples.append({'time_s':(frame-start)/24,
                        'bounds_blender':[[min(p[i] for p in points) for i in range(3)],
                                          [max(p[i] for p in points) for i in range(3)]]})
        evaluated.to_mesh_clear()
    references[action.name]=samples
if linear_diagnostic or '--reset-reference' in sys.argv:
    reference_name=('reset_linear_source_reference.json' if linear_diagnostic else 'reset_source_reference.json') if '--reset-reference' in sys.argv else 'linear_source_reference.json'
    (out/reference_name).write_text(json.dumps(references,indent=2))
    print('AMJVIZ_LINEAR_BONE_DIAGNOSTIC_ONLY',sum(len(s) for s in references.values()),flush=True)
    raise SystemExit(0)
rig.animation_data.action=None
for track,strip,action in originals:
    strip.influence=1.;strip.use_animated_influence=False
    track.mute=action.name!='T_pose'
scene.frame_set(0);bpy.context.view_layer.update()
for obj in scene.objects:obj.select_set(obj in (rig,body))
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text(encoding='utf8')+'\n144 candidate: omit non-deforming control bones from sampled GLB; preserve source anatomy/materials and all four source clips. Private evaluation only; no final Rook adoption.\n'
bpy.data.texts.new('PRIVATE_SOURCE_LICENSE').write(notice)
if not full_diagnostic:bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'unshifted_export.glb'),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,
    export_def_bones=not full_diagnostic,export_all_influences=True,export_optimize_animation_size=False,
    export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'native_reference.json').write_text(json.dumps(references,indent=2))
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'export_report.json').write_text(json.dumps({'source_sha256':hashlib.sha256((source/'source.blend').read_bytes()).hexdigest(),
    'raw_glb_sha256':hashlib.sha256((out/'unshifted_export.glb').read_bytes()).hexdigest(),
    'removed_noop_modifiers':removed,'source_bones':len(rig.data.bones),
    'samples':sum(len(s) for s in references.values()),'clips':list(references),
    'scope':'Candidate export; native source pose preservation and artistic review pending'},indent=2))
print('AMJVIZ_DEFORM_EXPORT_READY',sum(len(s) for s in references.values()),flush=True)
