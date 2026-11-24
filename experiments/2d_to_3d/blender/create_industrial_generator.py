"""Reference-based industrial generator study with explicit rigid parts."""
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box,make_material

output=Path(sys.argv[sys.argv.index('--')+1]).resolve()
if output.drive.upper()!='E:': raise ValueError('External output required')
output.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
yellow=make_material('SafetyYellowEnamel',(.55,.29,.035,1),.4,.55)
steel=make_material('MachinedSteel',(.20,.23,.24,1),.85,.35)
iron=make_material('CastIron',(.045,.055,.06,1),.6,.62)
copper=make_material('CopperWinding',(.36,.14,.045,1),.8,.35)
rubber=make_material('HoseRubber',(.018,.022,.023,1),0,.85)
screen=make_material('StatusDisplay',(.025,.35,.55,1),.1,.3,1.2)

def cylinder(name,location,radius,depth,material,axis='Z',vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=location)
    obj=bpy.context.object
    obj.name=name
    if axis=='Y': obj.rotation_euler.x=math.pi/2
    if axis=='X': obj.rotation_euler.y=math.pi/2
    obj.data.materials.append(material)
    bevel=obj.modifiers.new('MachinedRim','BEVEL'); bevel.width=.008; bevel.segments=2
    obj.modifiers.new('WeightedNormals','WEIGHTED_NORMAL')
    return obj

def tube(name,points,radius,material):
    curve=bpy.data.curves.new(name,'CURVE'); curve.dimensions='3D'
    curve.bevel_depth=radius; curve.bevel_resolution=2
    spline=curve.splines.new('BEZIER'); spline.bezier_points.add(len(points)-1)
    for point,position in zip(spline.bezier_points,points):
        point.co=position; point.handle_left_type='AUTO'; point.handle_right_type='AUTO'
    obj=bpy.data.objects.new(name,curve); bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    bpy.context.view_layer.objects.active=obj; obj.select_set(True)
    bpy.ops.object.convert(target='MESH'); obj.select_set(False)
    return obj

box('SkidBase',(0,0,.13),(.78,.57,.10),iron,.04)
for x in [-.64,.64]:
    for y in [-.44,.44]:
        box('VibrationFoot',(x,y,.035),(.11,.10,.035),rubber,.012)
        cylinder('MountBolt',(x,y,.245),.035,.04,steel,vertices=6)
box('EnamelHousing',(-.35,0,.79),(.29,.44,.53),yellow,.09)
box('VentRecess',(-.35,-.455,.8),(.205,.018,.36),iron,.025)
for i in range(10):
    box('VentLouver',(-.35,-.485,.49+i*.065),(.17,.018,.009),steel,.006)
for x in [-.56,-.14]:
    for z in [.44,1.17]:
        cylinder('HousingFastener',(x,-.459,z),.025,.022,steel,'Y',6)
for z,radius in [(.53,.20),(1.02,.23)]:
    cylinder('RotorCore',(.33,.02,z),radius,.75,iron,'Y')
    for i in range(13):
        cylinder('CoolingFin',(.33,-.34+i*.056,z),radius+.025,.015,steel,'Y')
    for side in [-1,1]:
        cylinder('EndBearing',(.33,side*.40,z),radius*.65,.07,copper,'Y')
        cylinder('AxleCap',(.33,side*.45,z),radius*.25,.045,steel,'Y')
for x in [-.65,.65]:
    tube('ProtectiveRollCage',[(x,-.50,.25),(x,-.50,1.20),(x,-.36,1.43),
                              (x,.36,1.43),(x,.50,1.20),(x,.50,.25)],.035,steel)
for y in [-.3,.3]:
    tube('TopCrossBrace',[(-.65,y,1.43),(.65,y,1.43)],.03,steel)
tube('ExhaustPipe',[(.55,.42,.3),(.72,.42,.3),(.72,.42,1.15),(.60,.42,1.26)],.045,iron)
tube('CoolantReturn',[(.52,-.40,.45),(.69,-.43,.60),(.69,-.42,.88),(.52,-.38,1.04)],.025,rubber)
box('ControlPod',(.04,-.58,.84),(.14,.12,.23),iron,.035)
display=box('Display',(.04,-.707,.94),(.10,.012,.065),screen,.009)
for x in [-.02,.06,.12]:
    cylinder('ControlButton',(x,-.715,.79),.017,.015,yellow,'Y',12)
for x in [-.55,-.35,-.15]:
    box('UpperServicePanel',(x,0,1.35),(.07,.27,.014),iron,.008)
parts=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(parts)>60
bpy.ops.object.select_all(action='DESELECT')
copies=[]
for part in parts:
    copy=part.copy(); copy.data=part.data.copy()
    bpy.context.collection.objects.link(copy)
    copy.select_set(True); copies.append(copy)
bpy.context.view_layer.objects.active=copies[0]
bpy.ops.object.convert(target='MESH')
bpy.ops.object.join()
merged=bpy.context.object
merged.name='GeneratorRealtimeDerivative'
bpy.ops.export_scene.gltf(filepath=str(output/'generator.glb'),export_format='GLB',export_apply=True,use_selection=True)
bpy.data.objects.remove(merged,do_unlink=True)
scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1000; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world=bpy.data.worlds.new('Neutral'); scene.world.color=(.18,.18,.18)
for location,energy in [((3,-4,5),650),((-3,2,4),450)]:
    bpy.ops.object.light_add(type='AREA',location=location)
    bpy.context.object.data.energy=energy; bpy.context.object.data.size=4
bpy.ops.object.camera_add(location=(3,-4,2.8)); camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,.75))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'; camera.data.ortho_scale=2.6; scene.camera=camera
scene.render.filepath=str(output/'generator_neutral.png')
bpy.ops.wm.save_as_mainfile(filepath=str(output/'generator.blend'))
bpy.ops.render.render(write_still=True)
print('INDUSTRIAL_GENERATOR_EXPORTED parts=',len(parts))
