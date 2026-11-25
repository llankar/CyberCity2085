"""Inspect licensed authored soldier without running embedded scripts or altering it."""
import json
from pathlib import Path
import bpy
root=Path('E:/CyberCity2085-3d-lab');source=root/'sources/unvanquished_human';out=root/'generated/phase2/unvanquished_human01';out.mkdir(exist_ok=True)
acquisition=json.loads((source/'acquisition.json').read_text());assert acquisition['license']=='CC-BY-SA-3.0'
bpy.ops.wm.open_mainfile(filepath=str(source/'human_male.blend'),use_scripts=False)
rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
for r in rigs:r.data.pose_position='REST'
bpy.context.view_layer.update()
report={'source_commit':acquisition['commit'],'rigs':[],'meshes':[],'actions':[],'images':[]}
for r in rigs:report['rigs'].append({'name':r.name,'bones':len(r.data.bones),'bone_names':list(r.data.bones.keys()),'scale':list(r.scale)})
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 points=[o.matrix_world@v.co for v in o.data.vertices]
 o.data.calc_loop_triangles()
 report['meshes'].append({'name':o.name,'vertices':len(points),'triangles':len(o.data.loop_triangles),'parent':o.parent.name if o.parent else None,'hide_render':o.hide_render,'bounds':[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]],'materials':[m.name for m in o.data.materials if m]})
for a in bpy.data.actions:report['actions'].append({'name':a.name,'frames':list(a.frame_range)})
for i in bpy.data.images:report['images'].append({'name':i.name,'filepath':i.filepath,'dimensions':list(i.size),'packed':bool(i.packed_file)})
(out/'source_audit.json').write_text(json.dumps(report,indent=2))
print('UNV_AUTHORED_SOURCE_AUDIT',json.dumps({'rigs':[(r['name'],r['bones']) for r in report['rigs']],'meshes':[(m['name'],m['vertices']) for m in report['meshes']],'actions':[(a['name'],a['frames']) for a in report['actions']],'images':report['images']}),flush=True)
