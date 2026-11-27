"""Shared corrugated shipping container for industrial maps."""
import math

import bpy

from create_hardsurface_crate import box


def build_container(group, x, y, w, d, container_skin, steel, beam, yaw=0.0, *,
                    ribbed_roof=False, roof_projection=None):
    body = box("Container body", (0,0,.88), (w*.46,d*.44,.88), container_skin)
    if roof_projection is not None:
        material, grid_width, grid_height = roof_projection
        mesh = body.data
        mesh.materials.append(material)
        uv = mesh.uv_layers.active
        cosine, sine = math.cos(yaw), math.sin(yaw)
        for face in mesh.polygons:
            if face.normal.z < .9:
                continue
            face.material_index = 1
            for index in face.loop_indices:
                point = mesh.vertices[mesh.loops[index].vertex_index].co
                world_x = x + cosine * point.x - sine * point.y
                world_y = y + sine * point.x + cosine * point.y
                uv.data[index].uv = (world_x / grid_width + .5, world_y / grid_height + .5)
    parts = [body]
    if ribbed_roof:
        for offset in (-.32,-.16,0,.16,.32):
            parts.append(box("Container roof stiffener", (w*offset,0,1.765),
                             (min(.035,w*.017),d*.41,.022),container_skin,.008))
        for end in (-1, 1):
            for side in (-1, 1):
                parts.append(box("Container upper corner casting", (end*w*.433,side*d*.40,1.745),
                                 (min(.075,w*.028),min(.065,d*.06),.052),steel,.012))
    for side in (-1, 1):
        for rib in range(11):
            parts.append(box("Container corrugation", ((rib-5)*w*.078,side*d*.45,.88),
                             (.026,.024,.76), container_skin, .008))
    for side in (-1,1):
        parts.append(box("Container door", (w*.469,side*d*.215,.87),
                         (.025,d*.20,.78), steel, .016))
        parts.append(box("Container lock rod", (w*.486,side*d*.16,.88),
                         (.012,.016,.72), beam, .006))
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    bpy.context.object.name = "Warehouse shipping container"
    obj = bpy.context.object
    obj.parent = group
    obj.location = (x,y,.88)
    obj.rotation_euler.z = yaw
    return obj
