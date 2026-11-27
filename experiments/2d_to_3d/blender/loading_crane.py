"""Shared dockside portal crane and overhead hoist."""
import math

import bpy

from create_hardsurface_crate import box


def build_crane(group, x, y, width, depth, steel, beam, *, height, outreach=2.65,
                basin_depth=0, submerged_feet=(), compact_footings=False, lattice_jib=False,
                jib_yaw=0.0):
    parts = []
    def member(label, position, dimensions, material):
        parts.append(box(label, position, dimensions, material, .018))

    def jib_member(label, reach, elevation, dimensions, material, pitch=0.0):
        member(label, (x-reach*math.cos(jib_yaw), y-reach*math.sin(jib_yaw), elevation),
               dimensions, material)
        parts[-1].rotation_euler = (0.0, pitch, jib_yaw)

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
            # Brace the upper leg back into the span, above the wagon clearance.
            brace_run = min(.75, chord_span*.19)
            brace_rise = .72
            member("Freight crane knee brace",
                   (x,y+side*(chord_span-brace_run)*.5,height-brace_rise*.5),
                   (.09,math.hypot(brace_run,brace_rise)*.5,.085), steel)
            parts[-1].rotation_euler.x = -side*math.atan2(brace_rise,brace_run)
    # The jib extends toward the harbor, above ground level.
    if lattice_jib:
        rise = .34
        bay = outreach*.91/5
        for z in (height+.15, height+.15+rise):
            jib_member("Crane jib chord", bay*2.5,z, (bay*2.5,.082,.052), beam)
        for index in range(5):
            pitch = math.atan2(rise,bay) * (-1 if index % 2 else 1)
            jib_member("Crane jib diagonal", bay*(index+.5),height+.15+rise/2,
                       (math.hypot(bay,rise)/2,.053,.041), steel,pitch)
    else:
        jib_member("Crane harbor jib", outreach*.47,height+.23,
                   (outreach*.55,.14,.18), beam)
    member("Crane motor housing", (x,y,height+.28), (.32,.28,.23), steel)
    jib_member("Crane hoist cable", outreach*.91,height-.58, (.018,.018,.73), steel)
    jib_member("Crane spreader", outreach*.91,height-1.32, (.28,.14,.065), beam)
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    bpy.context.object.name = "Dockside loading crane"
    bpy.context.object.parent = group
