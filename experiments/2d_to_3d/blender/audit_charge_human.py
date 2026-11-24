"""Record the authored human's real game-conversion costs without changing it."""
import json
import sys
from pathlib import Path
import bpy

source, output = map(Path, sys.argv[sys.argv.index('--') + 1:])
if source.resolve().drive.upper() != 'E:' or output.resolve().drive.upper() != 'E:':
    raise ValueError('External experimental files only')
bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
collection = bpy.data.collections['CH-einar']
meshes = []
for obj in collection.all_objects:
    if obj.type != 'MESH' or obj.hide_render:
        continue
    meshes.append({
        'name': obj.name, 'base_vertices': len(obj.data.vertices),
        'visible': obj.visible_get(), 'hidden_view_layer': obj.hide_get(),
        'materials': [slot.material.name if slot.material else None for slot in obj.material_slots],
        'modifiers': [{'name': m.name, 'type': m.type,
                       'viewport': m.show_viewport, 'render': m.show_render,
                       'levels': getattr(m, 'levels', None),
                       'render_levels': getattr(m, 'render_levels', None)} for m in obj.modifiers],
        'vertex_groups': len(obj.vertex_groups), 'shape_keys':
        len(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else 0,
    })
used = {name for obj in meshes for name in obj['materials'] if name}
materials = []
for name in sorted(used):
    material = bpy.data.materials[name]
    outputs = [n for n in material.node_tree.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output]
    route = []
    if outputs:
        for link in outputs[0].inputs['Surface'].links:
            node = link.from_node
            route.append({'type': node.type, 'node': node.name,
                          'group': node.node_tree.name if node.type == 'GROUP' else None,
                          'outputs': [s.name for s in node.outputs]})
    materials.append({'name': name, 'surface_route': route})
report = {'source': str(source), 'meshes': meshes, 'materials': materials,
          'base_vertices': sum(o['base_vertices'] for o in meshes),
          'credit': 'Einar Rig (CC-BY) Blender Foundation | studio.blender.org',
          'license': 'https://creativecommons.org/licenses/by/4.0/',
          'limitations': ['Base topology count excludes evaluated subdivisions and hair',
                          'Film rig and actions are not yet converted to a game rig',
                          'Source Surface Deform bindings require original topology during evaluation']}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2), encoding='utf-8')
assert meshes and materials and report['base_vertices'] > 1000
print('CHARGE_HUMAN_AUDIT_OK', len(meshes), len(materials), report['base_vertices'], flush=True)
