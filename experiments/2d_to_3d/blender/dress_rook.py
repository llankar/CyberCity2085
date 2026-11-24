"""Derive separate fitted garment meshes while preserving MPFB skin weights."""
import sys
from pathlib import Path
import bpy
import bmesh

args = sys.argv[sys.argv.index('--') + 1:]
output = Path(args[0]).resolve()
if output.drive.upper() != 'E:':
    raise ValueError('Generated resources require E:')
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/generated/phase2/rook_mpfb/rook_mpfb.blend')
body = bpy.data.objects['rook_mpfb']
rig = body.parent

def garment(name, predicate, color, thickness):
    obj = body.copy()
    obj.data = body.data.copy()
    bpy.context.collection.objects.link(obj)
    obj.name = name
    # Remove mask modifiers; retain the armature and inherited vertex groups.
    for modifier in list(obj.modifiers):
        if modifier.type != 'ARMATURE':
            obj.modifiers.remove(modifier)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # Only body vertices, never MPFB helper geometry.
    body_group = body.vertex_groups['body'].index
    deform = bm.verts.layers.deform.active
    remove = [v for v in bm.verts if not predicate(v.co) or not deform or v[deform].get(body_group, 0) < 0.5]
    bmesh.ops.delete(bm, geom=remove, context='VERTS')
    bm.to_mesh(obj.data)
    bm.free()
    mat = bpy.data.materials.new(name + '_material')
    mat.use_nodes = True
    shader = mat.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = 0.65
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    solid = obj.modifiers.new('GarmentThickness', 'SOLIDIFY')
    solid.thickness = thickness
    solid.offset = 1
    return obj

garment('Rook_Trousers', lambda p: 0.13 < p.z < 0.96, (0.018, 0.025, 0.03), 0.012)
garment('Rook_Undershirt', lambda p: 0.94 < p.z < 1.43 and abs(p.x) < 0.22, (0.008, 0.012, 0.015), 0.009)
garment('Rook_JacketShell', lambda p: 0.98 < p.z < 1.46 and (p.y > -0.055 or abs(p.x) > 0.10), (0.025, 0.09, 0.055), 0.025)
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'rook_dressed.blend'))
bpy.context.scene.render.filepath = str(output / 'rook_dressed_preview.png')
bpy.ops.render.render(write_still=True)
print('CYBERCITY_ROOK_GARMENTS_EXPORTED')
