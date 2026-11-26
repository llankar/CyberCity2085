from pathlib import Path
import bpy,json
from mathutils import Vector
p=Path('E:/CyberCity2085-3d-lab/generated/phase2')
bpy.ops.wm.open_mainfile(filepath=str(p/'showcase186/environment.blend'))
for root in sorted([o for o in bpy.data.objects if o.name.startswith('Occludable_')],key=lambda o:o.name):
 body=next((o for o in root.children_recursive if o.name.startswith('PBR_Facade_')),None)
 if body:
  pts=[body.matrix_world@Vector(c) for c in body.bound_box];lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
  print('DISTRICT195_ROOT',root.name,lo,hi,flush=True)
