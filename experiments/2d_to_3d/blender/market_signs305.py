"""Add practical lighting and trade signage to existing market stalls."""
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
output = phase / "market305"
output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(phase / "showcase245/environment.blend"))
bpy.context.preferences.filepaths.save_version = 0
housing = make_material("Market stall fixture housing", (.045, .057, .064, 1), .72, .42)
signs = [
    make_material("Market stall sign " + name, (*color, 1), .1, .45, .65)
    for name, color in (("amber", (.61,.23,.045)), ("teal", (.02,.42,.35)), ("rose", (.48,.08,.25)))
]
groups = sorted((obj for obj in bpy.data.objects if obj.name.startswith("Occludable_market_")),
                key=lambda obj: obj.name)
count = 0
for index, group in enumerate(groups):
    mesh = next((obj for obj in group.children_recursive if obj.name.startswith("PBR_Facade_")), None)
    if mesh is None:
        continue
    corners = [mesh.matrix_world @ Vector(corner) for corner in mesh.bound_box]
    x0, x1 = min(v.x for v in corners), max(v.x for v in corners)
    y0, y1 = min(v.y for v in corners), max(v.y for v in corners)
    top = max(v.z for v in corners)
    x = (x0+x1)/2
    y = y0+(y1-y0)*.12
    h = min(.58, (x1-x0)*.18)
    for name, position, size, material in [
        ("Trade sign frame", (x,y,top+.22), (h,.053,.21), housing),
        ("Trade sign face", (x,y-.055,top+.22), (h*.87,.009,.145), signs[index%len(signs)]),
        ("Trade sign stem", (x,y,top+.035), (.044,.044,.10), housing),
    ]:
        obj = box(name, position, size, material, .012)
        obj.parent = group
        obj.matrix_parent_inverse = group.matrix_world.inverted()
    count += 1
assert count >= 3, count
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(output / "environment.blend"))
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH" or obj.type == "LIGHT" and obj.data.type == "POINT"
                   or obj.name.startswith("Occludable_"))
bpy.ops.export_scene.gltf(filepath=str(output / "environment.glb"), export_format="GLB",
                          use_selection=True, export_apply=True, export_lights=True)
print("MARKET305_EXPORTED", count)
