"""Check body dimensions and armature survive the experimental GLB export."""
import sys
from pathlib import Path
import bpy
from mathutils import Vector

folder = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(folder / 'rook_dressed.blend'))
body = bpy.data.objects['rook_mpfb']
evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh = evaluated.to_mesh()
points = [body.matrix_world @ v.co for v in mesh.vertices]
expected = [(min(p[i] for p in points), max(p[i] for p in points)) for i in range(3)]
evaluated.to_mesh_clear()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(folder / 'rook_dressed.glb'))
body = next(o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name.startswith('rook_mpfb_Export'))
points = [body.matrix_world @ v.co for v in body.data.vertices]
actual = [(min(p[i] for p in points), max(p[i] for p in points)) for i in range(3)]
# glTF import can rotate the object; world coordinates restore Blender Z-up.
error = max(abs(a-b) for pair_a, pair_b in zip(expected, actual) for a,b in zip(pair_a, pair_b))
assert error < 0.002, (expected, actual, error)
assert any(m.type == 'ARMATURE' and len(m.object.data.bones) == 53 for m in body.modifiers)
print('CYBERCITY_BODY_ROUNDTRIP_PASS max_bound_error_m=%.8f' % error)
