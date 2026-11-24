"""Inventory authored visible curve hair before building a game derivative."""
import json
from pathlib import Path
import bpy

source='E:/CyberCity2085-3d-lab/sources/charge_studio/einar_release_v1.blend'
bpy.ops.wm.open_mainfile(filepath=source,use_scripts=False)
report=[]
for obj in bpy.data.collections['CH-einar'].all_objects:
    if obj.type not in {'CURVES','CURVE'} or not obj.visible_get() or obj.hide_render:
        continue
    report.append({'name':obj.name,'type':obj.type,
                   'curves':len(obj.data.curves) if obj.type=='CURVES' else len(obj.data.splines),
                   'points':len(obj.data.points) if obj.type=='CURVES' else None,
                   'curve_properties':[p.identifier for p in obj.data.curves[0].bl_rna.properties] if obj.type=='CURVES' and obj.data.curves else [],
                   'surface':getattr(getattr(obj.data,'surface',None),'name',None),
                   'modifiers':[{'name':m.name,'type':m.type,'viewport':m.show_viewport,
                                 'render':m.show_render} for m in obj.modifiers],
                   'materials':[m.name for m in obj.data.materials]})
    report[-1]['world_translation']=list(obj.matrix_world.translation)
    report[-1]['parent']=obj.parent.name if obj.parent else None
    report[-1]['parent_bone']=obj.parent_bone
path=Path('E:/CyberCity2085-3d-lab/generated/phase2/einar_review/hair_audit.json')
path.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('EINAR_VISIBLE_HAIR_AUDIT',len(report),flush=True)
