"""Derive separate fitted garment meshes while preserving MPFB skin weights."""
import sys
from pathlib import Path
import bpy
import bmesh
import math
from mathutils import Vector

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
jacket = garment('Rook_JacketShell', lambda p: 1.00 < p.z < 1.46 and abs(p.x) < 0.205 and (p.y > -0.055 or abs(p.x) > 0.10), (0.025, 0.09, 0.055), 0.025)

def jacket_panel(name, vertices, faces):
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(jacket.data.materials[0])
    # Transfer weights from the body surface, preserving multi-bone deformation.
    obj.parent = rig
    for group in body.vertex_groups:
        obj.vertex_groups.new(name=group.name)
    for vertex in mesh.vertices:
        nearest = min(body.data.vertices, key=lambda v: (v.co - vertex.co).length_squared)
        for weight in nearest.groups:
            obj.vertex_groups[weight.group].add([vertex.index], weight.weight, 'REPLACE')
    armature = obj.modifiers.new('Skeleton', 'ARMATURE')
    armature.object = rig
    solid = obj.modifiers.new('LeatherThickness', 'SOLIDIFY')
    solid.thickness = 0.009
    bevel = obj.modifiers.new('SoftSeams', 'BEVEL')
    bevel.width = 0.005
    bevel.segments = 2
    return obj

# Replace the body-derived jacket with an open, regular quad surface.
# Keep its material as the common garment material for modular panels.
jacket.hide_render = True
jacket.hide_viewport = True
levels = [(1.00, 0.185, 0.125), (1.12, 0.17, 0.125), (1.28, 0.245, 0.125), (1.40, 0.235, 0.115), (1.45, 0.18, 0.12)]
torso_vertices = []
segments = 24
body_eval = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
body_surface = body_eval.to_mesh()
surface_points = [v.co.copy() for v in body_surface.vertices]
body_eval.to_mesh_clear()
for z, width, depth in levels:
    for index in range(segments + 1):
        angle = -math.pi / 2 + 0.30 + (math.tau - 0.60) * index / segments
        c, s = math.cos(angle), math.sin(angle)
        x = width * math.copysign(abs(c) ** 0.75, c)
        y = -0.055 + depth * math.copysign(abs(s) ** 0.75, s)
        candidates = [p.y for p in surface_points if abs(p.x - x) < 0.03 and abs(p.z-z) < 0.035]
        if candidates:
            y = max(y, max(candidates) + 0.025) if s > 0 else min(y, min(candidates) - 0.025)
        torso_vertices.append((x, y, z))
torso_faces = [(ring * (segments + 1) + i, ring * (segments + 1) + i + 1, (ring + 1) * (segments + 1) + i + 1, (ring + 1) * (segments + 1) + i) for ring in range(len(levels) - 1) for i in range(segments)]
torso = jacket_panel('Rook_JacketTorso', torso_vertices, torso_faces)
for polygon in torso.data.polygons:
    polygon.use_smooth = True

for sign, side in [(1, 'l'), (-1, 'r')]:
    jacket_panel('Rook_Lapel_' + side,
        [(sign * x, y, z) for x, y, z in [(0.06, -0.145, 1.47), (0.15, -0.175, 1.40), (0.10, -0.185, 1.24), (0.055, -0.18, 1.37)]],
        [(0, 1, 2, 3)] if sign > 0 else [(3, 2, 1, 0)])
collar_vertices = []
for z, radius in [(1.43, 0.092), (1.51, 0.105)]:
    for index in range(13):
        angle = math.pi * 1.35 * index / 12 - math.pi * 0.175
        collar_vertices.append((radius * math.cos(angle), radius * math.sin(angle) + 0.005, z))
jacket_panel('Rook_RaisedCollar', collar_vertices, [(i, i + 1, i + 14, i + 13) for i in range(12)])

for side in ['l', 'r']:
    upper = rig.data.bones['upperarm_' + side]
    lower = rig.data.bones['lowerarm_' + side]
    centers = [upper.head_local - (upper.tail_local - upper.head_local).normalized() * 0.045, upper.head_local.lerp(upper.tail_local, 0.5), upper.head_local.lerp(upper.tail_local, 0.85), upper.tail_local, lower.head_local.lerp(lower.tail_local, 0.15), lower.head_local.lerp(lower.tail_local, 0.4), lower.head_local.lerp(lower.tail_local, 0.7)]
    radii = [0.098, 0.085, 0.075, 0.071, 0.068, 0.062, 0.056]
    axis = (lower.tail_local - upper.head_local).normalized()
    tangent = axis.cross(Vector((0, 1, 0))).normalized()
    bitangent = axis.cross(tangent).normalized()
    vertices = []
    for center, radius in zip(centers, radii):
        for index in range(16):
            angle = math.tau * index / 16
            vertices.append(tuple(center + radius * (math.cos(angle) * tangent + math.sin(angle) * bitangent)))
    faces = [(ring * 16 + i, ring * 16 + (i + 1) % 16, (ring + 1) * 16 + (i + 1) % 16, (ring + 1) * 16 + i) for ring in range(len(centers) - 1) for i in range(16)]
    sleeve = jacket_panel('Rook_Sleeve_' + side, vertices, faces)
    # Retain the inherited shoulder blend; use explicit normalized elbow blends.
    lower_weights = [0.0, 0.0, 0.15, 0.5, 0.85, 1.0, 1.0]
    for ring in range(1, len(centers)):
        indices = list(range(ring * 16, (ring + 1) * 16))
        for group in sleeve.vertex_groups:
            group.remove(indices)
        weight = lower_weights[ring]
        sleeve.vertex_groups['upperarm_' + side].add(indices, 1 - weight, 'REPLACE')
        sleeve.vertex_groups['lowerarm_' + side].add(indices, weight, 'REPLACE')
    for polygon in sleeve.data.polygons:
        polygon.use_smooth = True
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

# Swept sculptural locks: actual mesh tubes, sharing a replaceable hair material.
hair_material = bpy.data.materials.new('Rook_CopperHair')
hair_material.use_nodes = True
hair_shader = hair_material.node_tree.nodes['Principled BSDF']
hair_shader.inputs['Base Color'].default_value = (0.32, 0.065, 0.008, 1)
hair_shader.inputs['Roughness'].default_value = 0.52
evaluated_body = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
evaluated_mesh = evaluated_body.to_mesh()
scalp = [v.co.copy() for v in evaluated_mesh.vertices if v.co.z > 1.60]
cap_mesh = evaluated_mesh.copy()
evaluated_body.to_mesh_clear()
bm = bmesh.new()
bm.from_mesh(cap_mesh)
remove = [v for v in bm.verts if not (v.co.z > 1.665 or (v.co.z > 1.605 and v.co.y > -0.065))]
bmesh.ops.delete(bm, geom=remove, context='VERTS')
boundary = [v for v in bm.verts if any(edge.is_boundary for edge in v.link_edges)]
for _ in range(4):
    bmesh.ops.smooth_vert(bm, verts=boundary, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
bm.normal_update()
for vertex in bm.verts:
    vertex.co += vertex.normal * 0.0025
bm.to_mesh(cap_mesh)
bm.free()
cap_mesh.materials.clear()
cap_mesh.materials.append(hair_material)
cap = bpy.data.objects.new('Rook_ShortHairScalp', cap_mesh)
bpy.context.collection.objects.link(cap)
cap.parent = rig
group = cap.vertex_groups.new(name='head')
group.add(list(range(len(cap_mesh.vertices))), 1, 'REPLACE')
armature = cap.modifiers.new('Skeleton', 'ARMATURE')
armature.object = rig
for polygon in cap_mesh.polygons:
    polygon.use_smooth = True
for index in range(16):
    t = index / 15
    curve = bpy.data.curves.new('Rook_HairLock', 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.012
    curve.bevel_resolution = 2
    curve.resolution_u = 8
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(3)
    arch = math.sin(math.pi * t)
    points = [(-0.060 + t * 0.12, 0.018, 1.615 + 0.025 * arch), (-0.055 + t * 0.11, -0.015, 1.66 + 0.035 * arch), (-0.070 + t * 0.10, -0.09, 1.67 + 0.025 * arch), (-0.075 + t * 0.075, -0.142, 1.61 + 0.025 * arch)]
    for point, coordinate, radius in zip(spline.bezier_points, points, [0.5, 1.0, 0.85, 0.08]):
        x, y, z = coordinate
        candidates = [v.z for v in scalp if abs(v.x - x) < 0.018 and abs(v.y - y) < 0.018]
        surface = max(candidates) if candidates else min(scalp, key=lambda v: (v.x-x)**2 + (v.y-y)**2).z
        point.co = (x, y, surface + 0.008 + (0.025 * arch if radius > 0.5 else 0))
        point.radius = radius
        point.handle_left_type = point.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new('Rook_HairLock_%02d' % index, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(hair_material)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')
    obj = bpy.context.object
    obj.parent = rig
    group = obj.vertex_groups.new(name='head')
    group.add(list(range(len(obj.data.vertices))), 1, 'REPLACE')
    modifier = obj.modifiers.new('Skeleton', 'ARMATURE')
    modifier.object = rig

for side, sign in [('l', 1), ('r', -1)]:
    bone = 'foot_' + side
    # Derive lateral alignment from the actual rig rather than assuming body width.
    x = rig.data.bones[bone].head_local.x
    boot_piece('Rook_BootSole_' + side, (x, -0.065, 0.035), (0.065, 0.145, 0.025), bone, (0.008, 0.01, 0.014))
    boot_piece('Rook_BootUpper_' + side, (x, -0.060, 0.090), (0.060, 0.135, 0.045), bone, (0.022, 0.03, 0.035))
    boot_piece('Rook_BootShaft_' + side, (x, 0.025, 0.185), (0.060, 0.065, 0.105), bone, (0.022, 0.03, 0.035))
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'rook_dressed.blend'))
export_copies = []
bpy.ops.object.select_all(action='DESELECT')
for source in list(bpy.context.scene.objects):
    if source.type != 'MESH' or source.name == 'PreviewFloor' or source.hide_render:
        continue
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.collection.objects.link(obj)
    obj.name = source.name + '_Export'
    # The current phenotype is already baked into mesh coordinates. Export
    # copies do not need MPFB's authoring shape keys, which block mask baking.
    if obj.data.shape_keys:
        mixed = obj.shape_key_add(name='ExportCurrentPhenotype', from_mix=True)
        positions = [point.co.copy() for point in mixed.data]
        obj.shape_key_clear()
        for vertex, position in zip(obj.data.vertices, positions):
            vertex.co = position
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    # glTF export_apply=False preserves skins but ignores non-armature
    # modifiers: bake those explicitly on disposable copies.
    for modifier in list(obj.modifiers):
        if modifier.type != 'ARMATURE':
            bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    export_copies.append(obj)
rig.select_set(True)
for obj in export_copies:
    obj.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.gltf(filepath=str(output / 'rook_dressed.glb'), export_format='GLB', use_selection=True, export_apply=False, export_yup=True)
for obj in export_copies:
    mesh = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.meshes.remove(mesh)
bpy.context.scene.render.filepath = str(output / 'rook_dressed_preview.png')
bpy.ops.render.render(write_still=True)
camera = bpy.context.scene.camera
for label, position in [('front', (0, -2.8, 1.4)), ('back', (0, 2.8, 1.4)), ('side', (2.8, 0, 1.4))]:
    camera.location = position
    camera.rotation_euler = (Vector((0, 0, 1.25)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.lens = 75
    bpy.context.scene.render.filepath = str(output / ('rook_detail_' + label + '.png'))
    bpy.ops.render.render(write_still=True)
for side, angle in [('l', 0.9), ('r', 0.9)]:
    bone = rig.pose.bones['lowerarm_' + side]
    bone.rotation_mode = 'XYZ'
    bone.rotation_euler.x = angle
bpy.context.view_layer.update()
camera.location = (1.8, -2.8, 1.5)
camera.rotation_euler = (Vector((0, 0, 1.25)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.render.filepath = str(output / 'rook_elbow_test.png')
bpy.ops.render.render(write_still=True)
for side in ['l', 'r']:
    rig.pose.bones['lowerarm_' + side].rotation_euler = (0, 0, 0)
print('CYBERCITY_ROOK_GARMENTS_EXPORTED')
