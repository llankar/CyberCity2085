"""Inspect one authored hair-card source before any character adaptation."""
import bpy,json,hashlib
from pathlib import Path
root=Path('E:/CyberCity2085-3d-lab/sources/blenderkit_hair157')
bpy.ops.wm.open_mainfile(filepath=str(root/'source.blend'),use_scripts=False)
report={'source_sha256':hashlib.sha256((root/'source.blend').read_bytes()).hexdigest(),'objects':[],'materials':[]}
for o in bpy.context.scene.objects:
 record={'name':o.name,'type':o.type,'location':list(o.location),'scale':list(o.scale)}
 if o.type=='MESH':
  record.update(vertices=len(o.data.vertices),faces=len(o.data.polygons),materials=[m.name for m in o.data.materials if m],bounds=[[min((o.matrix_world@v.co)[k] for v in o.data.vertices),max((o.matrix_world@v.co)[k] for v in o.data.vertices)] for k in range(3)])
 report['objects'].append(record)
for m in bpy.data.materials:
 report['materials'].append({'name':m.name,'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None} for n in m.node_tree.nodes] if m.use_nodes else []})
(root/'audit.json').write_text(json.dumps(report,indent=2));print('HAIR157_SOURCE_AUDIT',json.dumps(report))
