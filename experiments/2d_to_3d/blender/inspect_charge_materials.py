"""Inspect source material interfaces before designing a bake/export derivative."""
import json
import sys
from pathlib import Path
import bpy

source=Path(sys.argv[sys.argv.index('--')+1]).resolve()
output=Path(sys.argv[sys.argv.index('--')+2]).resolve()
if source.drive.upper()!='E:' or output.drive.upper()!='E:': raise ValueError('Use E:')
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
materials=[]
for material in bpy.data.materials:
    if not material.use_nodes: continue
    nodes=[]
    for node in material.node_tree.nodes:
        if node.type in {'BSDF_PRINCIPLED','GROUP','OUTPUT_MATERIAL'}:
            nodes.append({'name':node.name,'type':node.type,
                          'group':node.node_tree.name if node.type=='GROUP' else None,
                          'inputs':[s.name for s in node.inputs],
                          'outputs':[s.name for s in node.outputs]})
    materials.append({'name':material.name,'nodes':nodes})
meshes=[{'name':o.name,'vertices':len(o.data.vertices),'hidden_render':o.hide_render,
         'uv_layers':[u.name for u in o.data.uv_layers],
         'materials':[s.material.name if s.material else None for s in o.material_slots]}
        for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('GEO-')]
active=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH': continue
    uv=obj.data.uv_layers.active
    coordinates=[tuple(v.uv) for v in uv.data] if uv else []
    active.append({'name':obj.name,'materials':[s.material.name if s.material else None for s in obj.material_slots],
                   'uv_bounds':[[min(v[i] for v in coordinates),max(v[i] for v in coordinates)] for i in range(2)] if coordinates else None})
output.write_text(json.dumps({'materials':materials,'meshes':meshes,'active_meshes':active},indent=2),encoding='utf-8')
print('CHARGE_MATERIAL_INTERFACES_WRITTEN',len(materials),len(meshes))
