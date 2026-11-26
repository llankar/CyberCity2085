"""Detail the existing platform furniture without changing its footprint."""
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "metro293"
output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(phase / "metro282/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0
trim = make_material("Platform brushed handrail", (.23, .28, .32, 1), .75, .36)
rubber = make_material("Platform rubber", (.016, .022, .027, 1), .05, .82)
amber = make_material("Platform amber label", (.62, .28, .028, 1), .25, .42)

counts = {"seat": 0, "bin": 0, "column": 0, "terminal": 0}
for obj in list(bpy.data.objects):
    if obj.type != "MESH" or obj.parent is None:
        continue
    x, y, z = obj.location
    w, d, h = obj.dimensions / 2
    def detail(name, position, size, material):
        part = box(name, position, size, material, .009)
        part.parent = obj.parent

    name = obj.name.split(".")[0]
    if name.endswith(" seat") and name.startswith("bench"):
        counts["seat"] += 1
        detail("Seat cushion", (x, y, z+h+.018), (w*.88, d*.83, .022), rubber)
        detail("Seat armrest support", (x+w*.83, y+d*.26, z+h+.12),
               (.023, .025, .12), trim)
        detail("Seat armrest", (x+w*.83, y, z+h+.23), (.036, d*.59, .023), trim)
    elif name.endswith(" structural core") and name.startswith("column"):
        counts["column"] += 1
        for face in (-1, 1):
            front = y + face * (d + .018)
            detail("Column access cover", (x, front, z-.48), (w*.80, .018, .34), trim)
            for index in range(4):
                detail("Column access grille", (x, front+face*.021, z-.61+index*.075),
                       (w*.59, .008, .014), rubber)
            detail("Column service tag", (x, front+face*.02, z+.77),
                   (w*.55, .010, .045), amber)
    elif name.endswith(" plinth") and name.startswith("ticket"):
        counts["terminal"] += 1
        detail("Ticket slot trim", (x, y-d-.052, .71), (w*.64, .022, .052), trim)
        detail("Ticket slot", (x, y-d-.077, .71), (w*.51, .008, .012), rubber)
        detail("Contactless reader", (x+w*.32, y-d-.057, .83), (w*.21, .021, .054), amber)
    elif name.endswith(" service bin"):
        counts["bin"] += 1
        detail("Bin lid", (x, y, z+h+.028), (w*.97, d*.97, .033), trim)
        detail("Bin opening", (x, y, z+h+.064), (w*.59, d*.32, .008), rubber)
        detail("Waste sorting label", (x, y-d-.007, z+h*.48), (w*.31, .009, .063), amber)

assert counts["seat"] == 8 and counts["bin"] == 4 and all(counts.values()), counts
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.type == "LIGHT" and obj.data.type == "POINT"
                   or obj.name.startswith("Occludable_") or obj.name == "Track263VisualOnly")
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True, export_lights=True)
print("METRO293_EXPORTED", counts)
