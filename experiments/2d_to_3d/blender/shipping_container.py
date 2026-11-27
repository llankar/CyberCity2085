"""Shared corrugated shipping container for industrial maps."""
import bpy

from create_hardsurface_crate import box


def build_container(group, x, y, w, d, container_skin, steel, beam, yaw=0.0, *, ribbed_roof=False):
    parts = [box("Container body", (0,0,.88), (w*.46,d*.44,.88), container_skin)]
    if ribbed_roof:
        for offset in (-.32,-.16,0,.16,.32):
            parts.append(box("Container roof stiffener", (w*offset,0,1.765),
                             (min(.035,w*.017),d*.41,.022),container_skin,.008))
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
