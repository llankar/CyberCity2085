"""Inspect the refused robot glass shader before choosing a game approximation."""
import json
from pathlib import Path
import bpy

bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/generated/phase2/security_geometry01/security_geometry.blend', use_scripts=False)
material = bpy.data.materials['robot_glass']
nodes = []
for node in material.node_tree.nodes:
    inputs = []
    for socket in node.inputs:
        value = getattr(socket, 'default_value', None)
        if value is not None and not isinstance(value, (str, int, float, bool)):
            try: value = list(value)
            except TypeError: value = str(value)
        inputs.append({'name': socket.name, 'value': value,
                       'links': [link.from_node.name + ':' + link.from_socket.name for link in socket.links]})
    nodes.append({'name': node.name, 'type': node.type, 'inputs': inputs})
path = Path('E:/CyberCity2085-3d-lab/generated/phase2/security_geometry01/glass_audit.json')
path.write_text(json.dumps(nodes, indent=2), encoding='utf-8')
print('CHARGE_GLASS_AUDIT_OK', len(nodes), flush=True)
