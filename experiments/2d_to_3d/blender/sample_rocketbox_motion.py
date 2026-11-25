"""Independent Blender surface reference for the actual authored animated skin."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03/motion01')
bpy.ops.wm.open_mainfile(filepath=str(root/'human_motion.blend'),use_scripts=False)
rig=bpy.data.objects['Bip01']
mesh=next(obj for obj in bpy.context.scene.objects if obj.type=='MESH')
report=json.loads((root/'retarget_report.json').read_text())
reference={}
for clip,details in report['clips'].items():
    for track in rig.animation_data.nla_tracks: track.mute=track.name!=clip
    samples=[]
    for step in range(9):
        frame=(details['frames']-1)*step/8
        bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame))
        bpy.context.view_layer.update()
        evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        geometry=evaluated.to_mesh()
        points=[list(evaluated.matrix_world @ geometry.vertices[index].co)
                for index in range(0,len(geometry.vertices),max(1,len(geometry.vertices)//24))]
        assert all(all(abs(value)<10 for value in point) for point in points)
        evaluated.to_mesh_clear()
        samples.append({'time_s':frame/30,'points':points})
    reference[clip]=samples
(root/'surface_reference.json').write_text(json.dumps(reference),encoding='utf-8')
print('ROCKETBOX_BLENDER_SURFACE_REFERENCE_OK',len(reference),sum(len(samples) for samples in reference.values()),flush=True)
