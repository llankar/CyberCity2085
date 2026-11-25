"""Inspect source geometry/material orientation, never execute embedded asset scripts."""
import json,hashlib
from pathlib import Path
import bpy
root=Path('E:/CyberCity2085-3d-lab');source=root/'sources/blenderkit_p320153'
out=root/'generated/phase2/amjviz_components153'
bpy.ops.wm.open_mainfile(filepath=str(source/'source.blend'),use_scripts=False)
rows=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    points=[obj.matrix_world@v.co for v in obj.data.vertices]
    rows.append({'name':obj.name,'vertices':len(points),'faces':len(obj.data.polygons),
        'bounds':[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]],
        'materials':[m.name for m in obj.data.materials]})
(out/'p320_source_audit.json').write_text(json.dumps({'objects':rows,
    'source_sha256':hashlib.sha256((source/'source.blend').read_bytes()).hexdigest(),
    'packed_images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE'],
    'scope':'Source geometry/material inventory; not fitted or artistically accepted'},indent=2))
print('P320_ORIGINAL_SOURCE_INVENTORIED',json.dumps(rows),flush=True)
