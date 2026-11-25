"""Read-only anatomical and boundary audit before a licensed head/armor assembly."""
import json,sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from anatomical_groups import descendants

root=Path('E:/CyberCity2085-3d-lab/generated/phase2');out=root/'scanned_armor_head01';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'renderpeople_nathan01/human.blend'),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.data.pose_position='REST'
bpy.context.view_layer.update();body=bpy.data.objects['Object_96']
points=[body.matrix_world@v.co for v in body.data.vertices]
groups={g.index:g.name for g in body.vertex_groups}
anatomy=descendants({b.name:b.parent.name if b.parent else None for b in rig.data.bones},'rp_nathan_animated_003_walking_neck_06')
head_groups={i for i,name in groups.items() if name in anatomy}
weights=[sum(g.weight for g in v.groups if g.group in head_groups) for v in body.data.vertices]
faces=[p for p in body.data.polygons if all(points[i].z>1.54 and weights[i]>.5 for i in p.vertices)]
indices={i for p in faces for i in p.vertices}
edges={}
for p in faces:
 for a,b in zip(p.vertices,list(p.vertices)[1:]+[p.vertices[0]]):
  edge=tuple(sorted((a,b)));edges[edge]=edges.get(edge,0)+1
boundary={i for edge,count in edges.items() if count==1 for i in edge}
selected=[points[i] for i in indices]
def bounds(values):return [[min(p[i] for p in values) for i in range(3)],[max(p[i] for p in values) for i in range(3)]]
report={'source_head_groups':sorted(groups[i] for i in head_groups),'selected_faces':len(faces),'selected_vertices':len(indices),'bounds_m':bounds(selected),'boundary_vertices':len(boundary),'boundary_bounds_m':bounds([points[i] for i in boundary]),'head_bone_world':list(rig.matrix_world@rig.data.bones['rp_nathan_animated_003_walking_head_07'].head_local),'eyes_bone_world':{side:list(rig.matrix_world@rig.data.bones['rp_nathan_animated_003_walking_eye_'+side+'_0'+('11' if side=='l' else '13')].head_local) for side in ['l','r']}}
bpy.ops.wm.open_mainfile(filepath=str(root/'unvanquished_human01/human_armor.blend'),use_scripts=False)
rig=bpy.data.objects['Armature'];rig.data.pose_position='REST';bpy.context.view_layer.update()
report['target_bones_world']={name:list(rig.matrix_world@rig.data.bones[name].head_local) for name in ['neck','head','eye.L','eye.R']}
for name in ['head','armor_neck','eye.L','eye.R']:
 obj=bpy.data.objects[name];report['target_'+name+'_bounds_m']=bounds([obj.matrix_world@v.co for v in obj.data.vertices])
(out/'preassembly_audit.json').write_text(json.dumps(report,indent=2))
print('SCANNED_HEAD_PREASSEMBLY_AUDIT',json.dumps(report),flush=True)
