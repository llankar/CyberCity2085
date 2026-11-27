"""Shared dockside portal crane and overhead hoist."""
import math

import bpy

from create_hardsurface_crate import box


def build_crane(group, x, y, width, depth, steel, beam, *, height, outreach=2.65,
                basin_depth=0, submerged_feet=(), compact_footings=False):
    parts = []
    def member(label, position, dimensions, material):
        parts.append(box(label, position, dimensions, material, .018))

    for side in (-1, 1):
        foot_y = y+side*depth*.32
        if side in submerged_feet:
            member("Crane basin foundation", (x,foot_y,-basin_depth/2),
                   (width*.32,depth*.11,basin_depth/2), steel)
        member("Crane footing", (x,y+side*depth*.32,.12),
               (min(width*.41,.36),min(depth*.14,.44),.12) if compact_footings
               else (width*.41,depth*.14,.12), steel)
        member("Crane portal leg", (x,y+side*depth*.32,height*.5),
               (.13,.15,height*.5), beam)
    member("Crane portal beam", (x,y,height), (.16,depth*.44,.14), beam)
    if compact_footings:
        # Freight-yard truss members are overhead and leave the two feet unchanged.
        chord_height = min(.46, depth*.13)
        chord_span = depth*.64
        member("Freight crane upper chord", (x,y,height+chord_height),
               (.12,chord_span*.5,.085), beam)
        bay = chord_span/4
        for index in range(4):
            slope = math.atan2(chord_height,bay) * (-1 if index % 2 else 1)
            member("Freight crane diagonal web", (x,y+(index-1.5)*bay,height+chord_height/2),
                   (.078,math.hypot(bay,chord_height)*.5,.062), beam)
            parts[-1].rotation_euler.x = slope
        for side in (-1, 1):
            member("Freight crane end post", (x,y+side*chord_span*.5,height+chord_height*.5),
                   (.105,.085,chord_height*.5), steel)
    # The jib extends toward the harbor, above ground level.
    member("Crane harbor jib", (x-outreach*.47,y,height+.23),
           (outreach*.55,.14,.18), beam)
    member("Crane motor housing", (x,y,height+.28), (.32,.28,.23), steel)
    member("Crane hoist cable", (x-outreach*.91,y,height-.58), (.018,.018,.73), steel)
    member("Crane spreader", (x-outreach*.91,y,height-1.32), (.28,.14,.065), beam)
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    bpy.context.object.name = "Dockside loading crane"
    bpy.context.object.parent = group
