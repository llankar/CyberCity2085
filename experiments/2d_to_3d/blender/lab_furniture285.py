"""Build raised laboratory work surfaces and rack fronts within surveyed bounds."""
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "lab285"
output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(phase / "lab282/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0

steel = make_material("Lab285 powder coated alloy", (.16, .22, .27, 1), .65, .38)
dark = bpy.data.materials["Lab recessed service panels"]
cyan = bpy.data.materials["Lab cyan instrumentation"]
amber = make_material("Lab285 rack status", (.6, .18, .02, 1), .2, .35, 1.5)

count = 0
for top in list(bpy.data.objects):
    if not top.name.endswith(" source worktop"):
        continue
    root = top.parent
    name = root.name
    rack = "rack" in name
    if not rack and not any(kind in name for kind in ("desk", "table", "console")):
        continue
    x, y, z = top.location
    w, d = top.scale.x, top.scale.y
    bpy.data.objects.remove(top, do_unlink=True)

    def part(label, offset, half_size, material):
        dx, dy, dz = offset
        obj = box("Lab285 " + label, (x + dx, y + dy, dz), half_size, material, .012)
        obj.parent = root

    part("solid worktop", (0, 0, z - .02), (w, d, .024), steel)
    if rack:
        face = w * (.90 if x > 0 else -.90)
        part("rack fascia", (face, 0, .69), (w * .075, d * .88, .60), steel)
        for index in range(8):
            height = .19 + index * .136
            part("server sled", (face * 1.06, 0, height), (w * .04, d * .76, .057), dark)
            part("server status", (face * 1.105, d * .63, height), (w * .012, .028, .017),
                 amber if index % 3 == 0 else cyan)
    else:
        part("instrument tray", (0, -d * .48, z + .026), (w * .48, d * .22, .026), dark)
        for index in range(3):
            part("instrument module", (w * (index - 1) * .31, -d * .48, z + .089),
                 (w * .10, d * .14, .045), steel)
        part("tray status strip", (0, -d * .66, z + .053), (w * .37, .014, .009), cyan)
    count += 1

assert count == 18, count
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.type == "LIGHT" and obj.data.type == "POINT"
                   or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True, export_lights=True)
print("LAB285_EXPORTED", count, "surveyed furniture groups")
