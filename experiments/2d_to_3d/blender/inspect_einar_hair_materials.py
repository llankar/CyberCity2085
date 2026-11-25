"""Inspect authored hair shading inputs before choosing a game approximation."""
import json
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).parent))
from authored_scene import load_einar_scene
load_einar_scene()
report=[]
def inspect(tree,seen):
    if tree.as_pointer() in seen: return []
    seen.add(tree.as_pointer()); result=[]
    for node in tree.nodes:
        if node.type=='GROUP': result.extend(inspect(node.node_tree,seen))
        if 'HAIR' in node.type or node.type in {'BSDF_PRINCIPLED','BSDF_DIFFUSE','MIX_SHADER'}:
            inputs=[]
            for socket in node.inputs:
                value=getattr(socket,'default_value',None)
                if value is not None and not isinstance(value,(float,int,str,bool)):
                    try: value=list(value)
                    except TypeError: value=str(value)
                inputs.append({'name':socket.name,'value':value,
                    'links':[{'node':link.from_node.name,'type':link.from_node.type,'socket':link.from_socket.name} for link in socket.links]})
            result.append({'tree':tree.name,'node':node.name,'type':node.type,
                'parametrization':getattr(node,'parametrization',None),'inputs':inputs})
    return result
for name in ['GEO-einar_beard','GEO-einar_mustache','GEO-einar_eyebrows','GEO-einar_hair']:
    obj=bpy.data.objects[name]
    report.append({'object':name,'materials':[{'name':material.name,'shaders':inspect(material.node_tree,set())} for material in obj.data.materials]})
folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/einar_review')
(folder/'hair_material_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('EINAR_HAIR_SHADERS_AUDITED',[(part['object'],[(mat['name'],len(mat['shaders'])) for mat in part['materials']]) for part in report],flush=True)
