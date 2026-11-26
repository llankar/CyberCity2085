"""Check cosmetic facade work preserves the saved roof and tactical body geometry."""
from pathlib import Path
import bpy,json,hashlib
ROOT=Path('E:/CyberCity2085-3d-lab/generated/phase2')
def signature(folder):
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/folder/'environment.blend'))
 root=bpy.data.objects['Occludable_ne_building']
 selected=[o for o in root.children_recursive if o.type=='MESH' and (o.name.startswith('PBR_Facade_') or o.name.startswith('Original236 '))]
 data={o.name:{'matrix':[list(row) for row in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons]} for o in selected}
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest(),len(data)
before,count=signature('showcase236');after,actual=signature('showcase237')
assert before==after and count==actual,(count,actual)
(ROOT/'showcase237/geometry_check.json').write_text(json.dumps({'sha256':after,'meshes_compared':count,'scope':'Original236 roof and base body vertices/faces/transforms; materials intentionally excluded','pass':True},indent=2))
print('DEPOT237_GEOMETRY_PRESERVED',count)
