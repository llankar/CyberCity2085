"""Mechanical robot blockout with independent rigid pivots; no human rig."""
import sys
from pathlib import Path
import bpy
import math
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material

output = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
if output.drive.upper() != 'E:':
    raise ValueError('External output required')
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
armor = make_material('Robot_WornIvory', (0.38, 0.40, 0.35, 1), 0.75, 0.4)
steel = make_material('Robot_DarkMechanics', (0.025, 0.035, 0.04, 1), 0.85, 0.3)
red = make_material('Robot_RedSensors', (1, 0.015, 0.002, 1), 0.1, 0.3, 3)

def pivot(name, location, parent=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    if parent:
        obj.parent = parent
        obj.matrix_parent_inverse = parent.matrix_world.inverted()
    bpy.context.view_layer.update()
    return obj

root = pivot('RobotRoot', (0, 0, 0))
def piece(name, location, size, mat, parent):
    obj = box(name, location, size, mat, 0.025)
    if mat == armor:
        # Shape individual armor plates rather than retaining cuboid blocks.
        for vertex in obj.data.vertices:
            height = vertex.co.z / max(size[2], 0.001)
            vertex.co.x *= 0.80 if height < 0 else 1.0
            if vertex.co.y < 0:
                vertex.co.y += abs(height) * size[1] * 0.18
        obj.data.update()
    obj.parent = parent
    obj.matrix_parent_inverse = parent.matrix_world.inverted()
    return obj

def bearing(name, location, radius, depth, parent, axis='X'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (0, math.pi / 2, 0) if axis == 'X' else (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(steel)
    bevel = obj.modifiers.new('MachinedEdge', 'BEVEL')
    bevel.width = 0.008
    bevel.segments = 2
    obj.parent = parent
    obj.matrix_parent_inverse = parent.matrix_world.inverted()
    return obj

torso = pivot('TorsoYaw', (0, 0, 1.45), root)
piece('ChestArmor', (0, 0, 1.50), (0.33, 0.19, 0.28), armor, torso)
for sign in [-1, 1]:
    panel = piece('PectoralPlate', (sign * 0.20, -0.205, 1.60), (0.135, 0.045, 0.16), armor, torso)
    panel.rotation_euler.y = sign * -0.18
    piece('AbdominalPlate', (sign * 0.13, -0.18, 1.28), (0.11, 0.045, 0.07), steel, torso)
piece('ChestCore', (0, -0.205, 1.50), (0.10, 0.025, 0.12), steel, torso)
piece('CoreLight', (0, -0.235, 1.50), (0.018, 0.012, 0.08), red, torso)
head = pivot('HeadYaw', (0, 0, 1.94), torso)
piece('HeadArmor', (0, 0, 1.94), (0.20, 0.17, 0.13), armor, head)
piece('RedVisor', (0, -0.18, 1.95), (0.16, 0.018, 0.035), red, head)
for sign, side in [(1, 'L'), (-1, 'R')]:
    hip = pivot('Hip_' + side, (sign * 0.22, 0, 1.12), root)
    bearing('HipBearing_' + side, (sign * 0.22, 0, 1.12), 0.12, 0.26, hip)
    piece('Thigh_' + side, (sign * 0.22, 0, 0.91), (0.13, 0.14, 0.23), armor, hip)
    knee = pivot('Knee_' + side, (sign * 0.22, 0, 0.65), hip)
    bearing('KneeBearing_' + side, (sign * 0.22, 0, 0.65), 0.10, 0.28, knee)
    piece('Shin_' + side, (sign * 0.22, 0, 0.42), (0.12, 0.13, 0.23), armor, knee)
    piece('Foot_' + side, (sign * 0.22, -0.09, 0.12), (0.14, 0.24, 0.10), steel, knee)
    shoulder = pivot('Shoulder_' + side, (sign * 0.44, 0, 1.67), torso)
    bearing('ShoulderBearing_' + side, (sign * 0.44, 0, 1.67), 0.15, 0.24, shoulder)
    piece('UpperArm_' + side, (sign * 0.47, 0, 1.48), (0.13, 0.14, 0.21), armor, shoulder)
    piece('ShoulderCap_' + side, (sign * 0.46, 0, 1.74), (0.18, 0.18, 0.09), armor, shoulder)
    elbow = pivot('Elbow_' + side, (sign * 0.47, 0, 1.24), shoulder)
    bearing('ElbowBearing_' + side, (sign * 0.47, 0, 1.24), 0.09, 0.25, elbow)
    piece('Forearm_' + side, (sign * 0.47, -0.02, 1.08), (0.11, 0.12, 0.17), steel, elbow)
    piece('ForearmShield_' + side, (sign * 0.47, -0.145, 1.08), (0.12, 0.035, 0.17), armor, elbow)
    piece('Hand_' + side, (sign * 0.47, -0.02, 0.86), (0.10, 0.08, 0.08), armor, elbow)
piece('ShoulderCannon', (0.45, -0.18, 1.85), (0.075, 0.30, 0.075), steel, torso)
bearing('CannonBarrel', (0.45, -0.48, 1.85), 0.045, 0.30, torso, axis='Y')
for index in range(6):
    piece('ChestVent_%02d' % index, (-0.12 + index * 0.048, -0.21, 1.37), (0.014, 0.018, 0.045), steel, torso)
for sign in [-1, 1]:
    for z in [1.42, 1.65]:
        bearing('ArmorFastener', (sign * 0.25, -0.255, z), 0.016, 0.015, torso, axis='Y')
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('NeutralWorld')
scene.world.color = (0.18, 0.18, 0.18)
for location in [(3, -4, 5), (-3, -1, 3)]:
    bpy.ops.object.light_add(type='AREA', location=location)
    bpy.context.object.data.energy = 700
    bpy.context.object.data.size = 4
bpy.ops.object.camera_add(location=(3, -4, 2.5))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 1.0))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.8
scene.camera = camera
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = scene.render.resolution_y = 768
scene.render.resolution_percentage = 100
scene.render.filepath = str(output / 'robot_blockout.png')
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'robot_blockout.blend'))
bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT')
for obj in scene.objects:
    obj.select_set(obj.type in {'MESH', 'EMPTY'})
bpy.ops.export_scene.gltf(filepath=str(output / 'robot_blockout.glb'), export_format='GLB', use_selection=True, export_apply=True)
for name, angle in [('Knee_L', 0.6), ('Elbow_R', 0.9)]:
    bpy.data.objects[name].rotation_euler.x = angle
bpy.context.view_layer.update()
scene.render.filepath = str(output / 'robot_pivot_test.png')
bpy.ops.render.render(write_still=True)
print('ARTICULATED_ROBOT_BLOCKOUT_EXPORTED')
