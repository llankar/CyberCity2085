"""Non-destructive palette study on licensed authored clothing, not final Rook."""
import sys
import json
from pathlib import Path
import bpy

output = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
if output.drive.upper() != 'E:':
    raise ValueError('Keep derived resources on E:')
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/generated/phase2/authored_armor01/authored_outfit.blend')
changed = []
for obj in bpy.context.scene.objects:
    name = obj.name.lower()
    is_armor = 'helios' in name
    is_hair = 'short' in name
    if not (is_armor or is_hair):
        continue
    for slot in obj.material_slots:
        if not slot.material or not slot.material.use_nodes:
            continue
        slot.material = slot.material.copy()
        nodes = slot.material.node_tree.nodes
        links = slot.material.node_tree.links
        shader = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
        base = shader.inputs['Base Color']
        tint = (0.075, 0.12, 0.115, 1) if is_armor else (0.65, 0.19, 0.035, 1)
        if base.links:
            previous = base.links[0].from_socket
            mixer = nodes.new('ShaderNodeMixRGB')
            mixer.blend_type = 'MULTIPLY'
            mixer.inputs[0].default_value = 1
            mixer.inputs[2].default_value = tint
            links.new(previous, mixer.inputs[1])
            links.new(mixer.outputs[0], base)
        else:
            base.default_value = tint
        shader.inputs['Roughness'].default_value = 0.65 if is_armor else 0.78
        shader.inputs['Metallic'].default_value = 0.25 if is_armor else 0
        changed.append(obj.name)
assert changed, 'No matching authored outfit parts'
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'authored_outfit.blend'))
(output / 'material_factors.json').write_text(json.dumps({
    'armor_helios': [0.075, 0.12, 0.115, 1],
    'short02': [0.65, 0.19, 0.035, 1]
}), encoding='utf-8')
print('TACTICAL_MATERIAL_STUDY', changed)
