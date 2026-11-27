"""Assemble technology market stalls from shared market geometry from original map traces."""
import json
import math
from pathlib import Path
import sys
import time

import bpy

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material
from library_placement import place

started = time.perf_counter()
root = Path(__file__).resolve().parents[3]
lab = Path("E:/CyberCity2085-3d-lab")
output = lab / "generated/phase2/techmarket341"
name = "city_district_tech_market"
source = root / "assets/maps" / name
survey = json.loads(source.with_suffix(".wall-traces.json").read_text())
gw, gh = json.loads(source.with_suffix(".walls.json").read_text())["grid"]
cw, ch = survey["canvas_size"]
stall = output / "shared_electronics_stall.glb"
bpy.ops.wm.open_mainfile(filepath=str(lab / "generated/phase2/market325/environment.blend"))
source_group = bpy.data.objects["Occludable_market_ne"]
descendants = set(source_group.children_recursive)
for obj in bpy.context.scene.objects:
    obj.select_set(obj in descendants and obj.type == "MESH")
bpy.ops.export_scene.gltf(filepath=str(stall), export_format="GLB", use_selection=True, export_apply=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0

selected = {
    "northwestern_shop", "western_small_stall", "center_north_stall", "southeast_bottom_stall",
    "north_stall_purple", "western_stall_extensions", "west_alley_canopy", "northeast_blue_stall",
}
roof = make_material("Tech market original rooftops", (.1,.1,.1,1), .1,.80)
roof_image = roof.node_tree.nodes.new("ShaderNodeTexImage")
roof_image.image = bpy.data.images.load(str(source.with_suffix(".png")))
roof.node_tree.links.new(roof_image.outputs["Color"], roof.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
cladding = make_material("Tech market dark facade", (.045,.065,.08,1), .45,.66)
window = lab / "environment-library/assets/urban_facade280/window.glb"
buildings = []
placed = []
for row in survey["walls"]:
    identifier = row["id"]
    if identifier.startswith("building_"):
        outline = [(px*gw/cw-gw/2, gh/2-py*gh/ch) for px, py in row["polygon"]]
        if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(outline, outline[1:]+outline[:1])) < 0:
            outline.reverse()
        height = (3.1, 3.6, 2.9)[len(buildings)%3]
        count = len(outline)
        edges = list(zip(outline, outline[1:]+outline[:1]))
        faces = [tuple(range(count, 2*count))]
        faces.extend((i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count))
        mesh = bpy.data.meshes.new(identifier)
        mesh.from_pydata([(x,y,z) for z in (0,height) for x,y in outline], [], faces)
        mesh.materials.append(cladding)
        mesh.materials.append(roof)
        mesh.polygons[0].material_index = 1
        uv = mesh.uv_layers.new()
        for loop in mesh.polygons[0].loop_indices:
            x,y,_ = mesh.vertices[mesh.loops[loop].vertex_index].co
            uv.data[loop].uv = (x/gw+.5,y/gh+.5)
        group = bpy.data.objects.new("Occludable_"+identifier,None)
        bpy.context.collection.objects.link(group)
        shell = bpy.data.objects.new(identifier,mesh)
        bpy.context.collection.objects.link(shell)
        shell.parent = group
        for (ax,ay),(bx,by) in edges:
            dx,dy = bx-ax,by-ay
            length = math.hypot(dx,dy)
            if length < 1.4:
                continue
            yaw = math.atan2(dy,dx)
            nx,ny = dy/length,-dx/length
            band = box("Facade division", ((ax+bx)/2+nx*.031,(ay+by)/2+ny*.031,height*.53),
                       (length/2,.042,.045),cladding,.009)
            band.rotation_euler.z = yaw
            band.parent = group
            bays = max(1,int(length/2.2))
            for index in range(bays):
                ratio = (index+.5)/bays
                x,y = ax+dx*ratio+nx*.065,ay+dy*ratio+ny*.065
                place(window, group, (x,y,height*.63), (1.36,.30,.69), yaw=yaw, merge=True)
        buildings.append(identifier)
        continue
    if identifier not in selected:
        continue
    x1,y1,x2,y2 = row["rect"]
    w,d = (x2-x1)*gw/cw,(y2-y1)*gh/ch
    x,y = (x1+x2)*gw/(2*cw)-gw/2,gh/2-(y1+y2)*gh/(2*ch)
    group = bpy.data.objects.new("Occludable_"+identifier,None)
    bpy.context.collection.objects.link(group)
    place(stall,group,(x,y,0),(w*.96,d*.96,2.5))
    placed.append(identifier)
assert set(placed) == selected
floor = make_material("Tech market source ground", (.13,.15,.17,1), .05,.84)
nodes = floor.node_tree.nodes
texture = nodes.new("ShaderNodeTexImage")
texture.image = bpy.data.images.load(str(output / "floor.png"))
floor.node_tree.links.new(texture.outputs["Color"], nodes.get("Principled BSDF").inputs["Base Color"])
bpy.ops.mesh.primitive_plane_add(size=2, location=(0,0,-.025))
bpy.context.object.scale = (gw/2,gh/2,1)
bpy.context.object.data.materials.append(floor)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB")
elapsed = round(time.perf_counter()-started,2)
(output / "assembly.json").write_text(json.dumps({
    "map": name, "stall_groups": placed, "building_groups": buildings, "reused_model_families": 2,
    "new_model_families": 0, "blender_seconds": elapsed
},indent=2))
print("TECHMARKET341_EXPORTED", len(placed), elapsed)
