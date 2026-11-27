"""Shared treatment-bed and warehouse-rack meshes."""
import math

import bpy

from create_hardsurface_crate import box
from library_placement import place


def build_bed(group, x, y, w, d, steel, linen, pad):
    long_y = d > w
    length, width = (d,w) if long_y else (w,d)
    parts = []
    def piece(label, along, across, z, half_length, half_width, half_height, material):
        dx,dy = (across,along) if long_y else (along,across)
        a,b = (half_width,half_length) if long_y else (half_length,half_width)
        parts.append(box(label,(x+dx,y+dy,z),(a,b,half_height),material,.025))
    for end in (-1,1):
        for side in (-1,1):
            piece("Bed leg",end*length*.32,side*width*.31,.24,.05,.05,.24,steel)
    piece("Bed frame",0,0,.48,length*.46,width*.43,.065,steel)
    piece("Bed mattress",0,0,.57,length*.44,width*.4,.075,linen)
    piece("Bed pillow",length*.30,0,.66,length*.105,width*.31,.045,linen)
    piece("Bed cover",-length*.13,0,.644,length*.29,width*.405,.021,pad)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    bpy.context.object.name="Clinic treatment bed"
    bpy.context.object.parent=group


def build_rack(group, x, y, w, d, steel, beam):
    parts = []
    def rack_part(label, location, dimensions, material):
        parts.append(box(label, location, dimensions, material, .012))

    for side_x in (-1, 1):
        for side_y in (-1, 0, 1):
            rack_part("Rack upright", (x+side_x*w*.43,y+side_y*d*.44,1.12),
                      (.046,.05,1.12), steel)
    for height in (.38,1.16,1.94):
        rack_part("Slotted shelf deck", (x,y,height), (w*.43,d*.45,.038), steel)
        for side in (-1,1):
            rack_part("Safety shelf rail", (x+side*w*.42,y,height+.01),
                      (.048,d*.46,.065), beam)
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    bpy.context.object.name = "Warehouse pallet rack"
    bpy.context.object.parent = group


def build_containment_chamber(group, x, y, w, d, steel, trim, screen):
    box("Containment footprint deck", (x, y, .075), (w*.50, d*.50, .075), steel).parent = group
    box("Containment specimen tray", (x, y, .27), (w*.28, d*.37, .12), trim).parent = group
    for side in (-1, 1):
        edge = x + side*w*.34
        box("Containment drive housing", (edge, y, .38), (w*.14, d*.44, .26), steel).parent = group
        box("Containment light rail", (x+side*w*.215, y, .49),
            (.025, d*.35, .028), screen).parent = group
        for offset in (-.31, 0, .31):
            box("Containment clamp", (edge, y+offset*d, .67),
                (w*.11, d*.077, .043), trim).parent = group
        box("Containment end bulkhead", (x, y+side*d*.396, .40),
            (w*.20, d*.055, .17), steel).parent = group


def build_medical_scanner(group, x, y, w, d, enamel, trim, screen):
    box("Scanner chassis", (x, y, .13), (w*.48, d*.47, .13), trim).parent = group
    box("Scanner patient table", (x, y-d*.09, .40),
        (w*.23, d*.34, .08), enamel).parent = group
    box("Scanner table pad", (x, y-d*.13, .50), (w*.19, d*.22, .035), screen).parent = group
    radius = min(w*.33, .57)
    gantry_y = y+d*.20
    box("Scanner gantry support", (x, gantry_y, .37), (w*.43, d*.13, .24), enamel).parent = group
    for label, offset, tube, material in (
        ("Scanner gantry shell", 0, .12, enamel),
        ("Scanner gantry light", -.10, .028, screen),
    ):
        bpy.ops.mesh.primitive_torus_add(
            major_segments=32, minor_segments=10, major_radius=radius, minor_radius=tube,
            location=(x, gantry_y+offset, .60+radius), rotation=(math.pi/2, 0, 0),
        )
        ring = bpy.context.object
        ring.name = label
        ring.data.materials.append(material)
        ring.parent = group



def build_security_bay(group, identifier, x, y, w, d, wall, crate, steel, trim, screen):
    # Side bays face the main aisle. The northern bays and guardrooms face south.
    yaw = 0
    if identifier.startswith(("southwest_", "west_middle_")):
        yaw = math.pi/2
    elif identifier.startswith(("southeast_", "east_middle_")):
        yaw = -math.pi/2
    front_width, depth = (w,d) if yaw == 0 else (d,w)
    cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)

    def center(u, v, z):
        return x+u*cos_yaw-v*sin_yaw, y+u*sin_yaw+v*cos_yaw, z

    def part(label, u, v, z, dimensions, material):
        piece = box(label, center(u,v,z), dimensions, material, .015)
        piece.rotation_euler.z = yaw
        piece.parent = group

    part("Security bay floor pan", 0,0,.038, (front_width*.495,depth*.495,.038), trim)
    part("Security bay doorway threshold", 0,-depth*.453,.094,
         (front_width*.16,.065,.024), steel)
    spans = [
        (0,depth*.44,front_width*.94,0),
        (-front_width*.46,0,depth*.84,math.pi/2),
        (front_width*.46,0,depth*.84,math.pi/2),
    ]
    for side in (-1,1):
        spans.append((side*front_width*.335,-depth*.44,front_width*.27,0))
    for u,v,length,turn in spans:
        count = max(1, math.ceil(length/2.0))
        span = length/count
        for i in range(count):
            offset = ((i+.5)/count-.5)*length
            place(wall, group, center(u+offset*math.cos(turn),v+offset*math.sin(turn),.076),
                  (span,.36,1.37), yaw=yaw+turn, merge=True)
    part("Security bay worktop", -front_width*.13,depth*.20,.70,
         (front_width*.235,.32,.065), steel)
    part("Security bay console cabinet", -front_width*.13,depth*.20,.38,
         (front_width*.21,.28,.30), trim)
    part("Security bay monitor enclosure", -front_width*.15,depth*.24,.90,
         (.23,.052,.14), steel)
    part("Security bay monitor", -front_width*.15,depth*.24-.057,.90,
         (.19,.012,.095), screen)
    place(crate, group, center(front_width*.28,depth*.12,.076),
          (front_width*.26,depth*.38,.72), yaw=yaw)
