"""Read-only source topology diagnostics for mechanical gait export."""
import json
import sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from authored_scene import load_authored_scene

load_authored_scene(Path('E:/CyberCity2085-3d-lab/sources/charge_studio/security_bot_v1/security_bot_release_v1.blend'))
result={}
for obj in bpy.data.objects:
    if 'cable_tube_leg' not in obj.name: continue
    result[obj.name]={'type':obj.type,'modifiers':[]}
    for mod in obj.modifiers:
        record={'name':mod.name,'type':mod.type}
        if mod.type=='NODES' and mod.node_group:
            record['nodes']=[{'name':n.name,'type':n.bl_idname,
                              'mode':getattr(n,'mode',None),
                              'inputs':{s.name:str(s.default_value) for s in n.inputs if hasattr(s,'default_value')}} for n in mod.node_group.nodes]
        if mod.type=='SCREW': record['steps']=mod.steps
        result[obj.name]['modifiers'].append(record)
    if obj.type=='CURVE':
        result[obj.name]['resolution']=obj.data.resolution_u
        result[obj.name]['splines']=[{'type':s.type,'points':len(s.points),'bezier_points':len(s.bezier_points)} for s in obj.data.splines]
out=Path('E:/CyberCity2085-3d-lab/generated/phase2/security_walk01/cable_audit.json')
out.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
