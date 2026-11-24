"""Inspect retained evaluated weights and authored attachment mechanisms."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
bpy.ops.wm.open_mainfile(filepath=str(root/'einar_geometry01/einar_evaluated.blend'),use_scripts=False)
report=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH': continue
    source=bpy.data.objects.get(obj.name.removesuffix('_GameStudy'))
    report.append({'object':obj.name,'vertices':len(obj.data.vertices),
                   'weighted_vertices':sum(bool(v.groups) for v in obj.data.vertices),
                   'max_group_index':max((g.group for v in obj.data.vertices for g in v.groups),default=-1),
                   'original_groups':[g.name for g in source.vertex_groups] if source else [],
                   'parent':source.parent.name if source and source.parent else None,
                   'parent_bone':source.parent_bone if source else None,
                   'constraints':[{'type':c.type,'target':getattr(getattr(c,'target',None),'name',None),
                                   'subtarget':getattr(c,'subtarget',None)} for c in source.constraints] if source else [],
                   'armatures':[m.object.name for m in source.modifiers if m.type=='ARMATURE' and m.object] if source else []})
path=root/'einar_review/skinning_audit.json'
path.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('EINAR_SKIN_AUDIT_OK',len(report),sum(r['weighted_vertices']>0 for r in report),flush=True)
