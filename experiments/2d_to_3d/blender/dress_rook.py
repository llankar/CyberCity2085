"""Derive separate fitted garment meshes while preserving MPFB skin weights."""
import sys
from pathlib import Path
import bpy
import bmesh
import math

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
    # Relax the cut boundary only; preserve the weighted interior topology.
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    boundary = [v for v in bm.verts if any(e.is_boundary for e in v.link_edges)]
    for _ in range(5):
        bmesh.ops.smooth_vert(bm, verts=boundary, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.to_mesh(obj.data)
    bm.free()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
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

garment('Rook_Trousers', lambda p: 0.13 < p.z < 1.00 and abs(p.x) < 0.25, (0.018, 0.025, 0.03), 0.018)
garment('Rook_Undershirt', lambda p: 0.94 < p.z < 1.43 and abs(p.x) < 0.22, (0.008, 0.012, 0.015), 0.009)
garment('Rook_JacketShell', lambda p: 1.00 < p.z < 1.46 and abs(p.x) < 0.40 and (p.y > -0.055 or abs(p.x) > 0.10), (0.025, 0.09, 0.055), 0.025)
def boot_piece(name, location, scale, bone, color):
    # Rounded rectangular cross-sections avoid a box silhouette while keeping
    # an editable low-poly surface with coherent rings.
    vertices = []
    faces = []
    count = 16
    for level, taper in [(-1.0, 0.85), (-0.7, 1.0), (0.65, 1.0), (1.0, 0.78)]:
        for index in range(count):
            angle = math.tau * index / count
            c, s = math.cos(angle), math.sin(angle)
            x = math.copysign(abs(c) ** 0.65, c)
            y = math.copysign(abs(s) ** 0.65, s)
            vertices.append((location[0] + x * scale[0] * taper, location[1] + y * scale[1] * taper, location[2] + level * scale[2]))
    for ring in range(3):
        for index in range(count):
            nxt = (index + 1) % count
            faces.append((ring * count + index, ring * count + nxt, (ring + 1) * count + nxt, (ring + 1) * count + index))
    faces.extend([tuple(reversed(range(count))), tuple(range(3 * count, 4 * count))])
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for polygon in mesh.polygons:
        polygon.use_smooth = len(polygon.vertices) == 4
    bevel = obj.modifiers.new('RoundedLeatherEdges', 'BEVEL')
    bevel.width = 0.004
    bevel.segments = 3
    mat = bpy.data.materials.new(name + '_material')
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*color, 1)
    mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.6
    obj.data.materials.append(mat)
    obj.parent = rig
    group = obj.vertex_groups.new(name=bone)
    group.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
    modifier = obj.modifiers.new('Skeleton', 'ARMATURE')
    modifier.object = rig
    return obj

for side, sign in [('l', 1), ('r', -1)]:
    bone = 'foot_' + side
    # Derive lateral alignment from the actual rig rather than assuming body width.
    x = rig.data.bones[bone].head_local.x
    boot_piece('Rook_BootSole_' + side, (x, -0.065, 0.035), (0.065, 0.145, 0.025), bone, (0.008, 0.01, 0.014))
    boot_piece('Rook_BootUpper_' + side, (x, -0.060, 0.090), (0.060, 0.135, 0.045), bone, (0.022, 0.03, 0.035))
    boot_piece('Rook_BootShaft_' + side, (x, 0.025, 0.185), (0.060, 0.065, 0.105), bone, (0.022, 0.03, 0.035))
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'rook_dressed.blend'))
bpy.context.scene.render.filepath = str(output / 'rook_dressed_preview.png')
bpy.ops.render.render(write_still=True)
print('CYBERCITY_ROOK_GARMENTS_EXPORTED')
