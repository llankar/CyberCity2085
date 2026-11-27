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

shared_stalls = {
    "northwestern_shop", "western_small_stall", "center_north_stall", "southeast_bottom_stall",
    "north_stall_purple", "western_stall_extensions", "west_alley_canopy", "northeast_blue_stall",
}
roof = make_material("Tech market original rooftops", (.1,.1,.1,1), .1,.80)
roof_image = roof.node_tree.nodes.new("ShaderNodeTexImage")
roof_image.image = bpy.data.images.load(str(source.with_suffix(".png")))
roof.node_tree.links.new(roof_image.outputs["Color"], roof.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
cladding = make_material("Tech market dark facade", (.045,.065,.08,1), .45,.66)
facade = make_material("Tech market weathered concrete", (.10,.13,.15,1), .12,.78)
facade_nodes = facade.node_tree.nodes
facade_shader = facade_nodes["Principled BSDF"]
facade_texture = facade_nodes.new("ShaderNodeTexImage")
facade_texture.image = bpy.data.images.load(str(output / "facade_concrete.png"))
facade.node_tree.links.new(facade_texture.outputs["Color"], facade_shader.inputs["Base Color"])
window = lab / "environment-library/assets/urban_facade280/window.glb"
entrance = window.with_name("entrance.glb")
neon = [make_material(f"Tech market facade light {index}", color, .28,.43,.42)
        for index,color in enumerate(((.055,.46,.60,1),(.46,.06,.24,1),(.62,.25,.05,1)))]
crate = lab / "environment-library/assets/cargo_crate274/model.glb"
placed = []
buildings = []
for row in survey["walls"]:
    identifier = row["id"]
    group = bpy.data.objects.new("Occludable_" + identifier, None)
    bpy.context.collection.objects.link(group)
    if "polygon" in row:
        outline = [(px*gw/cw-gw/2, gh/2-py*gh/ch) for px, py in row["polygon"]]
        if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(outline, outline[1:]+outline[:1])) < 0:
            outline.reverse()
        building = identifier.startswith("building_")
        bench = identifier == "north_bench"
        height = (3.1, 3.6, 2.9)[len(buildings)%3] if building else .48 if bench else 2.05
        bottom = 0 if building else height - (.12 if bench else .18)
        count = len(outline)
        edges = list(zip(outline, outline[1:]+outline[:1]))
        faces = [tuple(range(count, 2*count))]
        faces.extend((i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count))
        mesh = bpy.data.meshes.new(identifier)
        mesh.from_pydata([(x,y,z) for z in (bottom,height) for x,y in outline], [], faces)
        mesh.materials.append(facade)
        mesh.materials.append(roof)
        mesh.polygons[0].material_index = 1
        uv = mesh.uv_layers.new()
        for loop in mesh.polygons[0].loop_indices:
            x,y,_ = mesh.vertices[mesh.loops[loop].vertex_index].co
            uv.data[loop].uv = (x/gw+.5,y/gh+.5)
        for edge, face in zip(edges, mesh.polygons[1:]):
            repeats = math.dist(*edge)/2.8
            for loop, coord in zip(face.loop_indices, ((0,0),(repeats,0),(repeats,height/2.8),(0,height/2.8))):
                uv.data[loop].uv = coord
        shell = bpy.data.objects.new(identifier,mesh)
        bpy.context.collection.objects.link(shell)
        shell.parent = group
        if not building:
            for i,(x,y) in enumerate(outline):
                if i and math.dist(outline[i-1], (x,y)) < .40:
                    continue
                box("Bench leg" if bench else "Canopy post", (x,y,bottom/2),
                    (.039,.039,bottom/2), cladding,.008).parent = group
            if not bench:
                for (ax,ay),(bx,by) in edges:
                    length = math.hypot(bx-ax,by-ay)
                    beam = box("Canopy edge rail", ((ax+bx)/2,(ay+by)/2,bottom-.034),
                               (length/2,.033,.042),cladding,.009)
                    beam.rotation_euler.z = math.atan2(by-ay,bx-ax)
                    beam.parent = group
                if "canopy" not in identifier:
                    (ax,ay),(bx,by) = max(edges, key=lambda edge: math.dist(*edge))
                    length = math.hypot(bx-ax, by-ay)
                    dx,dy = (bx-ax)/length,(by-ay)/length
                    cx,cy = (ax+bx)/2-dy*.27,(ay+by)/2+dx*.27
                    counter = box("Market counter", (cx,cy,.43),
                                  (min(length*.25,1.15),.18,.43),cladding,.03)
                    counter.rotation_euler.z = math.atan2(dy,dx)
                    counter.parent = group
            placed.append(identifier)
            continue
        front = min(edges, key=lambda edge: math.hypot(
            (edge[0][0]+edge[1][0])/2, (edge[0][1]+edge[1][1])/2))
        for edge in edges:
            (ax,ay),(bx,by) = edge
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
            if edge == front:
                mx,my = (ax+bx)/2+nx*.062,(ay+by)/2+ny*.062
                place(entrance, group, (mx,my,0), (min(2.1,length*.37),.42,1.68), yaw=yaw, merge=True)
                light = box("Facade entrance light", (mx+nx*.073,my+ny*.073,1.74),
                            (min(.86,length*.19),.047,.043), neon[len(buildings)%len(neon)],.009)
                light.rotation_euler.z = yaw
                light.parent = group
            bays = max(1,int(length/2.2))
            for index in range(bays):
                ratio = (index+.5)/bays
                x,y = ax+dx*ratio+nx*.065,ay+dy*ratio+ny*.065
                place(window, group, (x,y,height*.63), (1.36,.30,.69), yaw=yaw, merge=True)
        buildings.append(identifier)
        continue
    x1,y1,x2,y2 = row["rect"]
    w,d = (x2-x1)*gw/cw,(y2-y1)*gh/ch
    x,y = (x1+x2)*gw/(2*cw)-gw/2,gh/2-(y1+y2)*gh/(2*ch)
    if identifier in shared_stalls:
        box("Stall raised deck", (x,y,.052), (w*.49,d*.49,.052), cladding).parent = group
        place(stall,group,(x,y,.10),(w*.96,d*.96,2.5))
    elif identifier == "northeast_crates":
        for offset in (-.24,.24):
            place(crate,group,(x+offset*w,y,0),(w*.43,d*.87,.78))
    elif identifier == "northwestern_barrels":
        radius = min(w,d)*.22
        for dx,dy in ((-.24,-.19),(.24,-.19),(0,.25)):
            bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=.81,
                                                location=(x+w*dx,y+d*dy,.405))
            barrel = bpy.context.object
            barrel.name = "Market service drum"
            barrel.data.materials.append(cladding)
            barrel.parent = group
            bpy.ops.mesh.primitive_torus_add(major_segments=20, minor_segments=6, major_radius=radius,
                                             minor_radius=.025, location=(x+w*dx,y+d*dy,.73))
            rim = bpy.context.object
            rim.name = "Market service drum rim"
            rim.data.materials.append(cladding)
            rim.parent = group
    else:
        raise ValueError(f"Unclassified Tech Market trace: {identifier}")
    placed.append(identifier)
assert len(placed) + len(buildings) == len(survey["walls"])
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
    "map": name, "fixture_groups": placed, "building_groups": buildings, "reused_model_families": 3,
    "new_model_families": 2, "blender_seconds": elapsed
},indent=2))
print("TECHMARKET341_EXPORTED", len(placed), elapsed)
