"""Review one small external aircraft candidate under neutral light."""
from pathlib import Path
import json
import bpy
from mathutils import Vector

LAB = Path('E:/CyberCity2085-3d-lab')
OUT = LAB / 'generated/phase2/dropship217'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(LAB / 'sources/dropship217/dropship_blender.glb'))
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
points = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
center = (low + high) / 2
span = max(high - low)
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Neutral studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.16, .16, .16, 1)
for name, offset, energy, size in [('Key', (1,-1,2), 18000, 15), ('Fill',(-1,1,1),9000,12)]:
    bpy.ops.object.light_add(type='AREA', location=center + Vector(offset)*span*.7)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (center-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=center + Vector((1,-1,.8))*span)
scene.camera = bpy.context.object
scene.camera.rotation_euler = (center-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.type = 'ORTHO'
scene.camera.data.ortho_scale = span*1.35
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = str(OUT/'neutral.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'candidate.blend'))
(OUT/'inventory.json').write_text(json.dumps({'meshes':len(meshes),'dimensions':list(high-low),'objects':[o.name for o in meshes]},indent=2))
(OUT/'CREDITS.txt').write_text('Sci-Fi Dropship v1 — tevy.dev\nhttps://tevy.dev/models/scifi-dropship\nCC0 1.0 according to source page. Downloaded 2026-11-26.\nCandidate review only; not integrated into production.\n',encoding='utf8')


