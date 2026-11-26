"""Improve lighting of Ashfield fractures while preserving their footprints and top artwork."""
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "wasteland301"
output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(phase / "wasteland297/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0

concrete = bpy.data.materials["Ruin weathered concrete"]
count = 0
mapped_faces = 0
for obj in bpy.context.scene.objects:
    if obj.type != "MESH" or not any(tag in obj.name for tag in (" fractured slab", " broken wall")):
        continue
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
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
assert count > 0 and mapped_faces > 0
floor = bpy.data.materials["Original ashfield ground"]
texture = next(node for node in floor.node_tree.nodes if node.type == "TEX_IMAGE")
texture.image = bpy.data.images.load(str(output / "floor.png"))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"),
                          export_format="GLB", use_selection=True, export_apply=True)
print("ASHFIELD301_EXPORTED", count, mapped_faces)
