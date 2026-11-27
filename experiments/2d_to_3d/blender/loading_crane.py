"""Shared dockside portal crane and overhead hoist."""
import bpy

from create_hardsurface_crate import box


def build_crane(group, x, y, width, depth, steel, beam, *, height, outreach=2.65,
                basin_depth=0, submerged_feet=()):
    parts = []
    def member(label, position, dimensions, material):
        parts.append(box(label, position, dimensions, material, .018))

    for side in (-1, 1):
        foot_y = y+side*depth*.32
        if side in submerged_feet:
            member("Crane basin foundation", (x,foot_y,-basin_depth/2),
                   (width*.32,depth*.11,basin_depth/2), steel)
        member("Crane footing", (x,y+side*depth*.32,.12),
               (width*.41,depth*.14,.12), steel)
        member("Crane portal leg", (x,y+side*depth*.32,height*.5),
               (.13,.15,height*.5), beam)
    member("Crane portal beam", (x,y,height), (.16,depth*.44,.14), beam)
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
