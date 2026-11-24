"""Inspect actual rig attachment routes before reducing the authored control rig."""
import json
from pathlib import Path
import bpy

bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/sources/charge_studio/einar_release_v1.blend',use_scripts=False)
report={'rigs':{},'rigid':[]}
for obj in bpy.data.collections['CH-einar'].all_objects:
    if obj.type=='ARMATURE':
        report['rigs'][obj.name]=[{'name':b.name,'parent':b.parent.name if b.parent else None,
                                 'deform':b.use_deform,'length':b.length} for b in obj.data.bones]
    elif obj.type=='MESH' and obj.visible_get() and not obj.hide_render and not obj.vertex_groups:
        attachments=[]
        for c in obj.constraints:
            if c.type=='ARMATURE':
                attachments.extend({'target':t.target.name if t.target else None,
                                    'bone':t.subtarget,'weight':t.weight} for t in c.targets)
        report['rigid'].append({'name':obj.name,'parent':obj.parent.name if obj.parent else None,
                                'parent_bone':obj.parent_bone,'armature_targets':attachments})
folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/einar_review')
(folder/'rig_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('EINAR_RIG_AUDIT_OK',[(name,len(bones)) for name,bones in report['rigs'].items()],flush=True)
