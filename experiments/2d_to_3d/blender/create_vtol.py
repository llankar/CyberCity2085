"""Reference-inspired rigid VTOL study; no production asset replacement."""
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from create_hardsurface_crate import box, make_material

output = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
if output.drive.upper() != 'E:':
    raise ValueError('External output required')
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
metal = make_material('Titanium', (0.16, 0.19, 0.21, 1), 0.7, 0.4)
dark = make_material('Recesses', (0.025, 0.03, 0.035, 1), 0.4, 0.55)
glass = make_material('OpaqueArmoredGlazing', (0.025, 0.10, 0.15, 1), 0.55, 0.19)
light = make_material('NavigationLights', (0.1, 0.65, 0.8, 1), 0.1, 0.3, 1.0)

def mesh_object(name, vertices, faces, material):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    bevel = obj.modifiers.new('ManufacturedEdges', 'BEVEL')
    bevel.width = 0.035
    bevel.segments = 2
    obj.modifiers.new('WeightedNormals', 'WEIGHTED_NORMAL')
    return obj

# Octagonal cross-sections define a closed tapered hull, not an image extrusion.
sections = [(-4.2, 0.22, 0.40, 0.85), (-3.0, 0.7, 0.65, 1.0),
            (-1.0, 1.05, 0.85, 1.1), (2.6, 0.95, 0.65, 1.05),
            (3.6, 0.5, 0.4, 1.0)]
vertices = []
for y, width, height, center in sections:
    for i in range(8):
        angle = 2 * math.pi * i / 8
        vertices.append((width * math.cos(angle), y, center + height * math.sin(angle)))
faces = [tuple(reversed(range(8))), tuple(range(32, 40))]
for ring in range(4):
    for i in range(8):
        j = (i + 1) % 8
        faces.append((ring*8+i, ring*8+j, (ring+1)*8+j, (ring+1)*8+i))
mesh_object('ProfiledFuselage', vertices, faces, metal)
for side in [-1, 1]:
    # Separate armored cockpit facets follow the nose taper.
    mesh_object('CockpitFacet', [(side*.13,-4.0,1.1),(side*.58,-3.05,1.5),
                (side*.76,-1.9,1.72),(side*.1,-2.0,1.93)], [(0,1,2,3)], glass)
    box('WingRoot', (side*1.3, 0.5, 0.95), (.4, .8, .12), metal)
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=10,
        location=(side*2.75,.5,.95), major_radius=1.05, minor_radius=.16)
    bpy.context.object.name = 'DuctedRotorHousing'
    bpy.context.object.data.materials.append(metal)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=.22, depth=.22,
        location=(side*2.75,.5,.96))
    bpy.context.object.name = 'RotorHub'
    bpy.context.object.data.materials.append(dark)
    for blade in range(10):
        angle = blade * math.tau / 10
        part = box('RotorBlade', (side*2.75+.59*math.cos(angle), .5+.59*math.sin(angle), .96),
                   (.40,.075,.025), dark, .015)
        part.rotation_euler.z = angle + .15
    mesh_object('TailFin', [(side*.48,2.1,1.3),(side*.7,3.55,1.25),
                (side*1.0,3.75,2.5),(side*.8,2.9,2.2)], [(0,1,2,3)], metal)
    for y in [-1.5, 2.0]:
        box('LandingStrut', (side*.85,y,.3), (.065,.09,.3), dark)
        box('LandingShoe', (side*.85,y,.055), (.24,.42,.055), metal)
    for y in [-.3,.5,1.3]:
        box('CabinWindow', (side*.99,y,1.15), (.025,.25,.12), glass, .025)
    box('WingNavigationLight', (side*3.83,.5,1.0), (.04,.15,.035), light)
box('NoseLamp', (0,-4.19,.82), (.12,.025,.08), light)
parts = list(bpy.context.scene.objects)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(output/'vtol.glb'), export_format='GLB', export_apply=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.world = bpy.data.worlds.new('Neutral')
scene.world.color = (.18,.18,.18)
bpy.ops.object.light_add(type='AREA', location=(3,-4,8))
bpy.context.object.data.energy = 1800
bpy.context.object.data.size = 7
bpy.ops.object.camera_add(location=(10,-12,10))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,1))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'
camera.data.ortho_scale=12
scene.camera=camera
scene.render.filepath=str(output/'vtol_neutral.png')
bpy.ops.wm.save_as_mainfile(filepath=str(output/'vtol.blend'))
bpy.ops.render.render(write_still=True)
print('VTOL_STUDY_EXPORTED parts=',len(parts))
