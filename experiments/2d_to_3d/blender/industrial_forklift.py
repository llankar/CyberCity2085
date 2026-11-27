"""Place a static forklift within its surveyed rectangular footprint."""
import math

import bpy

from create_hardsurface_crate import box


def build_forklift(group, identifier, x, y, w, d, skin, frame):
    vertical = d > w
    length, width = (d,w) if vertical else (w,d)
    group.location = (x,y,0)
    group.rotation_euler.z = math.pi/2 if vertical else 0
    parts = [
        ("counterweight", (-length*.19,0,.28), (length*.27,width*.40,.23), skin),
        ("cab", (-length*.11,0,.66), (length*.21,width*.32,.24), frame),
        ("mast", (length*.14,0,.58), (.055,width*.31,.57), frame),
    ]
    parts.extend(("fork", (length*.30,width*side*.19,.09),
                  (length*.19,width*.064,.034), frame) for side in (-1,1))
    for label, position, size, material in parts:
        box(identifier + " " + label, position, size, material).parent = group

    wheel_radius = min(.17, length*.14)
    wheel_depth = width*.14
    for axle in (-.30,.10):
        for side in (-1,1):
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=16, radius=wheel_radius, depth=wheel_depth,
                location=(length*axle,width*side*.39,wheel_radius),
                rotation=(math.pi/2,0,0),
            )
            wheel = bpy.context.object
            wheel.name = identifier + " wheel"
            wheel.data.materials.append(frame)
            wheel.parent = group
