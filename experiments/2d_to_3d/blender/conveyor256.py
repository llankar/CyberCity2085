"""Reusable source-guided roller conveyor: rigid mechanical geometry, not an extrusion."""
from pathlib import Path
import bpy,sys,math,json
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box,make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'environment-library/assets/roller_conveyor256';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
steel=make_material('Conveyor worn blue-black steel',(.06,.09,.11,1),.85,.5)
roller=make_material('Machined steel rollers',(.24,.27,.29,1),.9,.3)
paint=make_material('Safety ochre brackets',(.48,.23,.025,1),.55,.6)
rubber=make_material('Drive belt rubber',(.014,.018,.021,1),0,.85)
nodes=steel.node_tree.nodes;links=steel.node_tree.links;shader=nodes.get('Principled BSDF')
for file,socket in [('diff.jpg','Base Color'),('rough.jpg','Roughness')]:
 tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(LAB/'sources/environment169/blue_metal_plate'/file))
 if socket=='Roughness':tex.image.colorspace_settings.name='Non-Color'
 links.new(tex.outputs['Color'],shader.inputs[socket])
parts=[]
def part(name,p,s,m):
 o=box(name,p,s,m,.012);parts.append(o);return o
def cylinder(name,p,r,depth,material,axis='Y'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth,location=p);o=bpy.context.object;o.name=name
 if axis=='Y':o.rotation_euler.x=math.pi/2
 if axis=='X':o.rotation_euler.y=math.pi/2
 o.data.materials.append(material)
 bevel=o.modifiers.new('Machined rim','BEVEL');bevel.width=.006;bevel.segments=2
 for face in o.data.polygons:face.use_smooth=len(face.vertices)==4
 parts.append(o);return o
for y in [-.54,.54]:
 part('Load-bearing side rail',(0,y,.79),(2.05,.065,.12),steel)
 part('Yellow edge guard',(0,y,.94),(2.02,.035,.025),paint)
 for x in [-1.7,0,1.7]:
  part('Support leg',(x,y,.35),(.06,.06,.35),steel)
  part('Bolted floor foot',(x,y,.035),(.15,.12,.035),steel)
  for sx in [-1,1]:cylinder('Foundation bolt',(x+sx*.09,y,.075),.025,.025,roller,'Z')
for i in range(22):
 x=-1.92+i*3.84/21
 cylinder('Transverse roller',(x,0,.86),.082,.94,roller)
 for side in [-1,1]:
  cylinder('Roller bearing',(x,side*.51,.86),.047,.07,paint)
  cylinder('Bearing end cap',(x,side*.57,.86),.024,.025,steel)
for x in [-1.65,0,1.65]:part('Underframe crossmember',(x,0,.55),(.055,.55,.055),steel)
for side in [-1,1]:
 brace=part('Diagonal frame brace',(.85,side*.54,.35),(.9,.025,.025),steel);brace.rotation_euler.y=math.radians(17)
cylinder('Electric drive motor',(1.65,.84,.64),.19,.42,steel)
cylinder('Motor fan housing',(1.65,1.07,.64),.205,.08,roller)
for i in range(8):
 a=i*math.tau/8
 part('Motor cooling fin',(1.65+math.cos(a)*.19,.84,.64+math.sin(a)*.19),(.012,.2,.012),steel)
part('Reduction gearbox',(1.65,.59,.67),(.22,.14,.22),steel)
part('Drive guard',(1.65,.59,.93),(.23,.15,.035),paint)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'source.blend'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(OUT/'model.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.context.view_layer.update();points=[o.matrix_world@Vector(c) for o in parts for c in o.bound_box]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
(OUT/'asset.json').write_text(json.dumps({'id':'roller_conveyor256','family':'Industry','models':{'blend':str(OUT/'source.blend'),'glb':str(OUT/'model.glb')},'source_map':'city_industrial_factory_floor','source_object_id':'west_assembly','dimensions':[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],'anchor':'center_frame_ground; asymmetric motor extends toward +Z in glTF','orientation':'glTF Y up; long axis X','provenance':'Source-guided precise mechanical assembly; existing PBR maps; inferred side construction','authentic_views':1,'generated_views':0,'artistic_status':'NEEDS_NATIVE_REVIEW'},indent=2))
print('ROLLER_CONVEYOR256_EXPORTED',len(parts),'parts')
