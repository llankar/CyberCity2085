"""Measure candidate cut boundaries; never assume a closed circular neck loop."""
import json
from pathlib import Path
import bpy
import bmesh

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_head_fit126/human.blend'),use_scripts=False)
report={}
for name in ('char1','MIT_HeadFitStudy'):
    obj=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    remaining={v for e in bm.edges if e.is_boundary for v in e.verts}
    parts=[]
    while remaining:
        seed=next(iter(remaining));component={seed};stack=[seed]
        while stack:
            v=stack.pop()
            for edge in v.link_edges:
                if not edge.is_boundary:continue
                other=edge.other_vert(v)
                if other not in component:component.add(other);stack.append(other)
        remaining-=component
        coords=[obj.matrix_world@v.co for v in component]
        if max(p.z for p in coords)<1.45:continue
        parts.append({'vertices':len(component),'closed_degree2':all(sum(e.is_boundary for e in v.link_edges)==2 for v in component),'bounds':[[min(p[i] for p in coords) for i in range(3)],[max(p[i] for p in coords) for i in range(3)]],'points':[list(p) for p in coords]})
    report[name]=parts;bm.free()
(root/'rook_neck127/boundaries.json').write_text(json.dumps(report,indent=2))
print('NECK_BOUNDARIES',json.dumps({name:[{k:v for k,v in p.items() if k!='points'} for p in parts] for name,parts in report.items()}),flush=True)
