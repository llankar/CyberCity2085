"""Measure actual hand/cuff landmarks before altering the authored glove."""
import json
from pathlib import Path
import bpy
import bmesh

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'rook_wrist132';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_run129/human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
for t in rig.animation_data.nla_tracks:t.mute=t.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
graph=bpy.context.evaluated_depsgraph_get()
wrist=rig.matrix_world@rig.pose.bones['RightHand'].matrix.translation
elbow=rig.matrix_world@rig.pose.bones['RightForeArm'].matrix.translation
axis=(elbow-wrist).normalized()
parts=[]
for obj in scene.objects:
    if obj.type!='MESH' or not obj.vertex_groups:continue
    if obj.name!='char1' and len(obj.data.vertices)!=206:continue
    ev=obj.evaluated_get(graph);mesh=ev.to_mesh()
    points=[ev.matrix_world@v.co for v in mesh.vertices]
    right_groups={g.index for g in obj.vertex_groups if g.name in ('RightForeArm','RightHand')}
    near=[p for i,p in enumerate(points) if (p-wrist).length<.12 and (obj.name!='char1' or sum(g.weight for g in obj.data.vertices[i].groups if g.group in right_groups)>.5)]
    parts.append({'name':obj.name,'vertices':len(mesh.vertices),'near_wrist_count':len(near),'axial_range_near_wrist_m':[min((p-wrist).dot(axis) for p in near),max((p-wrist).dot(axis) for p in near)] if near else None,'near_points':[list(p) for p in near]})
    if len(mesh.vertices)==206:
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        edges=[e for e in bm.edges if e.is_boundary]
        boundary={v for e in edges for v in e.verts}
        parts[-1]['boundary_vertices']=len(boundary)
        parts[-1]['boundary_axial_m']=[(ev.matrix_world@v.co-wrist).dot(axis) for v in boundary]
        bm.free()
    ev.to_mesh_clear()
report={'wrist_world':list(wrist),'elbow_world':list(elbow),'toward_elbow':list(axis),'parts':parts,'scope':'Restored Ready0 vertex landmark audit, not surface contact proof'}
(out/'wrist_audit.json').write_text(json.dumps(report,indent=2))
print('WRIST_LANDMARKS',json.dumps({**report,'parts':[{k:v for k,v in p.items() if k!='near_points'} for p in parts]}),flush=True)
