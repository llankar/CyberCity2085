"""Record real source skin material wiring before any conversion."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_single_neck138/human.blend'),use_scripts=False)
material=bpy.data.materials['sm004_head']
rows=[]
for node in material.node_tree.nodes:
    rows.append({'name':node.name,'type':node.type,
                 'image':node.image.name if node.type=='TEX_IMAGE' and node.image else None,
                 'color_space':node.image.colorspace_settings.name if node.type=='TEX_IMAGE' and node.image else None,
                 'normal_space':node.space if node.type=='NORMAL_MAP' else None,
                 'inputs':[{'name':s.name,'links':[l.from_node.name+':'+l.from_socket.name for l in s.links],
                            'value':float(s.default_value) if hasattr(s,'default_value') and isinstance(s.default_value,(float,int)) else None} for s in node.inputs]})
output=root/'rook_skin139/skin_material.json';output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(rows,indent=2))
print('SKIN_MATERIAL_AUDIT',[(r['type'],r['color_space'],r['normal_space']) for r in rows],flush=True)
