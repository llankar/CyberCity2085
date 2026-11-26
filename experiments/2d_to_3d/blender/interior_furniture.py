"""Shared treatment-bed and warehouse-rack meshes."""
import bpy

from create_hardsurface_crate import box


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
