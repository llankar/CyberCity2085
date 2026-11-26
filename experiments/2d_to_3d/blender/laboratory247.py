"""First source-traced lab assembly. Art-only geometry; no collision or tactics export."""
from pathlib import Path
import bpy,json,sys,math
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box,make_material
ROOT=Path(__file__).resolve().parents[3];LAB=Path('E:/CyberCity2085-3d-lab')
OUT=LAB/'generated/phase2/lab247';OUT.mkdir(parents=True,exist_ok=True)
NAME='city_interior_research_lab'
survey=json.loads((ROOT/f'assets/maps/{NAME}.wall-traces.json').read_text())
tactics=json.loads((ROOT/f'assets/maps/{NAME}.walls.json').read_text())
gw,gh=tactics['grid'];cw,ch=survey['canvas_size']
bpy.ops.wm.read_factory_settings(use_empty=True)
steel=make_material('Lab brushed steel',(.10,.16,.18,1),.8,.32)
white=make_material('Lab clinical ceramic',(.36,.44,.47,1),.25,.37)
dark=make_material('Lab recessed service panels',(.015,.027,.032,1),.55,.4)
cyan=make_material('Lab cyan instrumentation',(.015,.52,.7,1),.3,.24,2)
glass=make_material('Lab containment blue glass',(.012,.16,.23,1),.3,.15)
glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=.65
parts=[]
def at(x,y,z):return (x/cw*gw-gw/2,gh/2-y/ch*gh,z)
def part(n,p,s,m):
 o=box(n,p,s,m,.025);parts.append(o);return o
def group(n):
 o=bpy.data.objects.new('Occludable_'+n,None);bpy.context.collection.objects.link(o);return o
def attach(o,parent):o.parent=parent;return o
def cylinder(n,p,r,depth,material,parent):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=p)
 o=bpy.context.object;o.name=n;o.data.materials.append(material)
 bevel=o.modifiers.new('Machined edges','BEVEL');bevel.width=.025;bevel.segments=2
 for face in o.data.polygons:face.use_smooth=len(face.vertices)==4
 parts.append(o);return attach(o,parent)
for item in survey['walls']:
 identifier=item['id'];root=group(identifier)
 if 'points' in item:
  points=item['points'];width=item.get('width',14)/cw*gw
  for i,(a,b) in enumerate(zip(points,points[1:])):
   start=Vector(at(*a,0));end=Vector(at(*b,0));delta=end-start
   for z,h,material,label in [(1.05,1.05,white,'partition'),(.22,.12,dark,'service channel'),(1.86,.025,cyan,'light rail')]:
    o=part(identifier+label+str(i),tuple((start+end)/2+Vector((0,0,z))),(delta.length/2,width/2,h),material)
    o.rotation_euler.z=math.atan2(delta.y,delta.x);attach(o,root)
  continue
 x1,y1,x2,y2=item['rect'];x,y,z=at((x1+x2)/2,(y1+y2)/2,0);w=(x2-x1)/cw*gw;d=(y2-y1)/ch*gh
 if identifier in ['west_wall','east_wall']:
  attach(part(identifier,(x,y,1.1),(w/2,d/2,1.1),white),root);continue
 if 'pods' in identifier:
  # Pictured three-pod bank, reconstructed as round housings rather than a
  # source image on a rectangular block. Inner anatomy is not inferred.
  for i in range(3):
   px=x+(i-1)*w/3;radius=min(w/7,d*.38)
   cylinder(identifier+' chamber'+str(i),(px,y,1.3),radius,1.85,glass,root)
   for z in [.25,.39,2.23,2.38]:cylinder(identifier+' collar',(px,y,z),radius*1.12,.14,steel,root)
   for a in [0,math.pi/2,math.pi,math.pi*1.5]:
    cylinder(identifier+' rib',(px+radius*math.cos(a),y+radius*math.sin(a),1.3),.042,1.8,steel,root)
   for offset in [-.76,.76]:cylinder(identifier+' scan column',(px+offset*radius,y-radius*.66,1.3),.025,1.7,cyan,root)
  attach(part(identifier+' console base',(x,y-d*.43,.52),(w*.45,.18,.4),dark),root)
  attach(part(identifier+' control strip',(x,y-d*.43,.94),(w*.4,.15,.025),cyan),root)
  continue
 # Furniture follows illustrated footprint, with a real work surface, recessed
 # plinth and frame. The actual cropped artwork supplies instrumentation detail.
 h=1.05 if 'desk' in identifier or 'table' in identifier or 'console' in identifier else 1.3
 attach(part(identifier+' service base',(x,y,h*.4),(max(.1,w/2-.12),max(.1,d/2-.12),h*.4),dark),root)
 attach(part(identifier+' edge frame',(x,y,h-.07),(w/2,d/2,.09),steel),root)
 crop=LAB/f'environment-library/references/{NAME}__{identifier}.png'
 mat=bpy.data.materials.new(identifier+' source instrumentation');mat.use_nodes=True
 nodes=mat.node_tree.nodes;shader=nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.35;shader.inputs['Metallic'].default_value=.4
 tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(crop));mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
 bpy.ops.mesh.primitive_plane_add(size=2,location=(x,y,h+.025));o=bpy.context.object;o.name=identifier+' source worktop';o.scale=(w/2,d/2,1);o.data.materials.append(mat);parts.append(o);attach(o,root)
 for offset in [-.44,.44]:attach(part(identifier+' frame rail',(x+w*offset,y,h*.55),(.035,max(.05,d/2-.05),h*.45),steel),root)
# Retained original floor. Original drawings under replacement volumes still need
# cleanup at cutaway; this first assembly is explicitly not artistically final.
floor=bpy.data.materials.new('Original laboratory floor');floor.use_nodes=True
tex=floor.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/f'assets/maps/{NAME}.png'))
floor.node_tree.links.new(tex.outputs['Color'],floor.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
floor.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.62
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,0,-.03));o=bpy.context.object;o.name='OriginalFloor';o.scale=(gw/2,gh/2,1);o.data.materials.append(floor);parts.append(o)
world=bpy.data.worlds.new('Lab neutral');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.17,.21,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;bpy.context.scene.world=world
for location,energy in [((0,0,15),3500),((-12,-8,8),1800)]:
 bpy.ops.object.light_add(type='AREA',location=location);o=bpy.context.object;o.data.energy=energy;o.data.size=16
bpy.ops.object.camera_add(location=(25,-32,34));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=49;camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.camera=camera;scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.filepath=str(OUT/'overview.png')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
for o in bpy.data.objects:
 if o.name.startswith('Occludable_'):o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
pod=bpy.data.objects['Occludable_north_pods'];selected=[pod]+list(pod.children_recursive)
for obj in bpy.context.scene.objects:obj.select_set(obj in selected)
bpy.ops.export_scene.gltf(filepath=str(OUT/'pod_bank.glb'),export_format='GLB',use_selection=True,export_apply=True)
points=[o.matrix_world@Vector(c) for o in selected if o.type=='MESH' for c in o.bound_box]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
(OUT/'pod_bank.json').write_text(json.dumps({'id':'laboratory_containment_bank','source_map':NAME,'source_object_id':'north_pods','source_root':pod.name,'bounds_blender':[list(lo),list(hi)],'dimensions_godot':[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],'anchor_godot':[(lo.x+hi.x)/2,lo.z,-(lo.y+hi.y)/2],'orientation':'Blender Z up to glTF Y up','materials':sorted({m.name for o in selected if o.type=='MESH' for m in o.data.materials}),'method':'Source-guided procedural rigid assembly; rejected Hunyuan trial retained separately','artistic_status':'FIRST_ASSEMBLY_NOT_FINAL'},indent=2))
bpy.ops.render.render(write_still=True)
print('LAB247_ASSEMBLY_EXPORTED',len(parts),'artistic_status=FIRST_ASSEMBLY_NOT_FINAL')
