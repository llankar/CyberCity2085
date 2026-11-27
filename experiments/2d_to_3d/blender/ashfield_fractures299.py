"""Improve lighting of Ashfield fractures while preserving their footprints and top artwork."""
from pathlib import Path

import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "wasteland320"
output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(phase / "wasteland297/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0

concrete = bpy.data.materials["Ruin weathered concrete"]
count = 0
mapped_faces = 0
widened_walls = 0
for obj in bpy.context.scene.objects:
    if obj.type != "MESH" or not any(tag in obj.name for tag in (" fractured slab", " broken wall")):
        continue
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
    if (" broken wall" in obj.name and obj.parent and "ruin" in obj.parent.name
            and obj.dimensions.z > 1.25):
        face = max((face for face in mesh.faces if abs(face.normal.z) < .15),
                   key=lambda face: face.calc_area())
        axis = Vector((face.normal.x, face.normal.y, 0)).normalized()
        points = [vertex.co.dot(axis) for vertex in mesh.verts]
        midpoint = (min(points)+max(points))/2
        # thicken the existing wall around its centerline
        for vertex in mesh.verts:
            vertex.co += axis * ((vertex.co.dot(axis)-midpoint)*.95)
        widened_walls += 1
    mesh.to_mesh(obj.data)
    mesh.free()
    bevel = obj.modifiers.new("Fracture edge wear", "BEVEL")
    bevel.width = .046 if " slab" in obj.name else .027
    bevel.segments = 2
    bevel.limit_method = "ANGLE"
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    if concrete.name not in obj.data.materials:
        obj.data.materials.append(concrete)
    slot = obj.data.materials.find(concrete.name)
    uv = obj.data.uv_layers.active
    for face in obj.data.polygons:
        # Keep the map projection on the broad upward surface. Assign
        # local concrete coordinates to cut sides and the narrow bevels.
        if face.normal.z > .88 and face.material_index != slot:
            continue
        face.material_index = slot
        axis = Vector((0, 0, 1)).cross(face.normal)
        if axis.length_squared < 1e-8:
            axis = Vector((1, 0, 0))
        axis.normalize()
        vertical = face.normal.cross(axis).normalized()
        for loop in face.loop_indices:
            point = obj.data.vertices[obj.data.loops[loop].vertex_index].co
            uv.data[loop].uv = (point.dot(axis)/1.5, point.dot(vertical)/1.5)
        mapped_faces += 1
    count += 1
assert count > 0 and mapped_faces > 0 and widened_walls > 0
print("ASHFIELD320_THICKENED", widened_walls)
# Use the original triangular slab top to keep roof pieces inside each ruin.
roof_material = bpy.data.materials.new("Ashfield oxidized roof sheets")
roof_material.use_nodes = True
shader = roof_material.node_tree.nodes.get("Principled BSDF")
shader.inputs["Base Color"].default_value = (.115, .056, .028, 1)
shader.inputs["Metallic"].default_value = .55
shader.inputs["Roughness"].default_value = .77
for group in [obj for obj in bpy.data.objects if obj.name.startswith("Occludable_")]:
    if "ruin" not in group.name:
        continue
    candidates = [obj for obj in group.children if " fractured slab0" in obj.name]
    if not candidates:
        continue
    # Broad top faces survive the bevel and define the plane of the fallen sheet.
    slab = candidates[0]
    face = max(slab.data.polygons, key=lambda poly: poly.area if poly.normal.z > .5 else 0)
    if face.normal.z <= .5 or len(face.vertices) < 3:
        continue
    a, b, c = [slab.matrix_world @ slab.data.vertices[i].co for i in face.vertices[:3]]
    vertices = []
    faces = []
    for rib in range(12):
        t = .16 + rib*.054
        lift = .05 + (.037 if rib % 2 else 0)
        # Preserve the slab outline while giving the torn sheet a wider end
        # and a staggered edge. Barycentric weights remain positive.
        outer_edge = min(.41 + (.022 if rib % 3 == 0 else 0), .96-t)
        for v in (.12, outer_edge):
            point = a*(1-t-v) + b*t + c*v + Vector((0, 0, lift))
            vertices.append(tuple(point))
        if rib:
            j = 2*rib
            faces.append((j-2, j, j+1, j-1))
    mesh = bpy.data.meshes.new("Corrugated roof fragment")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(roof_material)
    panel = bpy.data.objects.new("Collapsed corrugated roofing", mesh)
    bpy.context.collection.objects.link(panel)
    panel.parent = group
    panel.matrix_parent_inverse = group.matrix_world.inverted()
    thickness = panel.modifiers.new("Sheet thickness", "SOLIDIFY")
    thickness.thickness = .024

rust = bpy.data.materials["Exposed oxidized reinforcement"]
structural_walls = [
    obj for obj in bpy.data.objects
    if obj.type == "MESH" and " broken wall" in obj.name
    and obj.parent and "ruin" in obj.parent.name and obj.dimensions.z > 1.25
]
for wall in structural_walls:
    corners = [wall.matrix_world @ Vector(corner) for corner in wall.bound_box]
    center = sum(corners, Vector()) / len(corners)
    # Follow the wall direction rather than the global axes.
    face = max((poly for poly in wall.data.polygons if abs(poly.normal.z) < .15),
               key=lambda poly: poly.area)
    normal = (wall.matrix_world.to_3x3() @ face.normal).normalized()
    plane = wall.matrix_world @ face.center
    anchor = center + normal * ((plane-center).dot(normal) + .025)
    height = wall.dimensions.z * .79
    post = box("Ruined wall steel upright", (anchor.x, anchor.y, height/2),
               (.062, .038, height/2), rust, .009)
    post.rotation_euler.z = Vector((0, 1)).angle_signed(normal.xy)
    post.parent = wall.parent
    tangent = Vector((normal.y, -normal.x, 0))
    projections = [(corner-anchor).dot(tangent) for corner in corners]
    left, right = min(projections), max(projections)
    if right-left >= .65:
        midpoint = anchor+tangent*((left+right)*.5)
        tie = box("Ruined wall exposed horizontal steel tie", (midpoint.x,midpoint.y,height*.68),
                  ((right-left)*.40,.034,.048), rust,.009)
        tie.rotation_euler.z = post.rotation_euler.z
        tie.parent = wall.parent

assert structural_walls
print("ASHFIELD320_UPRIGHTS", len(structural_walls))
floor = bpy.data.materials["Original ashfield ground"]
texture = next(node for node in floor.node_tree.nodes if node.type == "TEX_IMAGE")
texture.image = bpy.data.images.load(str(phase / "wasteland301/floor.png"))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"),
                          export_format="GLB", use_selection=True, export_apply=True)
print("ASHFIELD320_EXPORTED", count, mapped_faces)
