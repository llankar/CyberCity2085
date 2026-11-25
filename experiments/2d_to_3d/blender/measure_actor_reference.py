"""Measure selected actual actor meshes at the established six-clip sample times."""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy

parser=argparse.ArgumentParser();parser.add_argument('--folder',required=True)
parser.add_argument('--dense-run',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path('E:/CyberCity2085-3d-lab/generated/phase2').resolve()
folder=(root/args.folder).resolve()
assert folder.is_relative_to(root) and folder!=root
bpy.ops.wm.open_mainfile(filepath=str(folder/'human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
meshes=[o for o in scene.objects if o.type=='MESH' and o not in helpers]
template=json.loads((root/'cyborg_actions01/native_reference.json').read_text())
references={}
for track in rig.animation_data.nla_tracks:
    for other in rig.animation_data.nla_tracks:other.mute=track!=other
    strip=track.strips[0];samples=[]
    sample_times=template[track.name]
    if args.dense_run and track.name=='run':
        count=round((strip.frame_end-strip.frame_start)*8)
        sample_times=[{'time_s':i/(8*24)} for i in range(count+1)]
    for sample in sample_times:
        value=strip.frame_start+sample['time_s']*24
        scene.frame_set(math.floor(value),subframe=value%1);bpy.context.view_layer.update()
        graph=bpy.context.evaluated_depsgraph_get();boxes={}
        for obj in meshes:
            evaluated=obj.evaluated_get(graph);data=evaluated.to_mesh()
            points=[evaluated.matrix_world@v.co for v in data.vertices]
            boxes[obj.name.replace('.','_').replace(' ','_')]=[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
            evaluated.to_mesh_clear()
        samples.append({'time_s':sample['time_s'],'mesh_bounds_blender':boxes})
    references[track.name]=samples
(folder/'native_reference.json').write_text(json.dumps(references,indent=2))
print('ACTOR_REFERENCE_MEASURED',len(meshes),sum(map(len,references.values())),flush=True)
