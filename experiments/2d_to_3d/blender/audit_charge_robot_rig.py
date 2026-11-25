"""Inventory actual robot joints, controls and attachment routes on E:."""
import json
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).parent))
from authored_scene import load_authored_scene
source=Path('E:/CyberCity2085-3d-lab/sources/charge_studio/security_bot_v1/security_bot_release_v1.blend')
scene=load_authored_scene(source)
rigs=[obj for obj in scene.objects if obj.type=='ARMATURE']
report={'rigs':{},'meshes':[]}
for rig in rigs:
    report['rigs'][rig.name]=[{'name':bone.name,'deform':bone.bone.use_deform,
        'properties':{key:float(value) for key,value in bone.items() if isinstance(value,(int,float))},
        'constraints':[{'type':c.type,'target':getattr(getattr(c,'target',None),'name',None),
                        'subtarget':getattr(c,'subtarget',None)} for c in bone.constraints]}
        for bone in rig.pose.bones]
for obj in scene.objects:
    if obj.type!='MESH' or obj.hide_render or not obj.name.startswith('GEO-'): continue
    report['meshes'].append({'name':obj.name,'visible':obj.visible_get(),'vertices':len(obj.data.vertices),
        'groups':len(obj.vertex_groups),'parent':obj.parent.name if obj.parent else None,
        'parent_bone':obj.parent_bone,
        'modifiers':[{'type':m.type,'target':getattr(getattr(m,'object',None),'name',None)} for m in obj.modifiers],
        'constraints':[{'type':c.type,'targets':[{'object':t.target.name if t.target else None,'bone':t.subtarget,'weight':t.weight} for t in getattr(c,'targets',[])]} for c in obj.constraints]})
folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/security_review')
(folder/'rig_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('SECURITY_ROBOT_RIG_AUDITED',[(rig.name,len(rig.pose.bones)) for rig in rigs],len(report['meshes']),flush=True)
