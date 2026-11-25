"""Measure original authored deform-bone endpoints after resetting source poses."""
import hashlib,json,math
from pathlib import Path
import bpy
from mathutils import Matrix,Vector

root=Path('E:/CyberCity2085-3d-lab');out=root/'generated/phase2/amjviz_runtime144'
source=root/'sources/blenderkit_cyberpunk143/source.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
scene=bpy.context.scene;rig=bpy.data.objects['rig']
tracks=list(rig.animation_data.nla_tracks)
for track in tracks:track.mute=True
names=[b.name for b in rig.data.bones if b.use_deform]
references={}
for track in tracks:
    strip=track.strips[0];action=strip.action
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    rig.animation_data.action=action
    if action.slots:rig.animation_data.action_slot=action.slots[0]
    start,end=strip.action_frame_start,strip.action_frame_end;samples=[]
    for step in range(round((end-start)*2)+1):
        frame=start+step/2;scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()
        evaluated=rig.evaluated_get(bpy.context.evaluated_depsgraph_get());bones={}
        for name in names:
            pose=evaluated.pose.bones[name];matrix=evaluated.matrix_world@pose.matrix
            bones[name]={'head':list(matrix.translation),
                         'tail':list(matrix@Vector((0,rig.data.bones[name].length,0))),
                         'length':rig.data.bones[name].length}
        samples.append({'time_s':(frame-start)/24,'bones':bones})
    references[action.name]=samples
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'clips':references,
        'scope':'Original rig endpoints, reset before every authored clip; no linearized B-Bones'}
(out/'bone_reference145.json').write_text(json.dumps(report,separators=(',',':')))
print('AMJVIZ_SOURCE_BONES_MEASURED',len(names),sum(len(s) for s in references.values()),flush=True)
