"""Source-guided subway: recessed escalators, seats, service columns and terminals."""
from pathlib import Path
import bpy,json,sys,math
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box,make_material
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=Path(__file__).resolve().parents[3]
OUT=LAB/'generated/phase2/metro250';OUT.mkdir(parents=True,exist_ok=True)
NAME='city_transit_subway_platform';survey=json.loads((ROOT/f'assets/maps/{NAME}.wall-traces.json').read_text());tactics=json.loads((ROOT/f'assets/maps/{NAME}.walls.json').read_text());gw,gh=tactics['grid'];cw,ch=survey['canvas_size']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
steel=make_material('Subway worn dark steel',(.055,.075,.085,1),.8,.45)
seat=make_material('Subway blue enamel seating',(.025,.12,.20,1),.45,.35)
black=make_material('Rubber and recessed joints',(.01,.016,.019,1),.15,.65)
chrome=make_material('Brushed stair nosing',(.22,.27,.3,1),.85,.3)
yellow=make_material('Platform safety yellow',(.65,.34,.035,1),.3,.5)
cyan=make_material('Platform service lighting',(.02,.4,.65,1),.25,.22,2)
nodes=steel.node_tree.nodes;links=steel.node_tree.links;shader=nodes.get('Principled BSDF');coords=nodes.new('ShaderNodeTexCoord')
for filename,socket in [('diff.jpg','Base Color'),('rough.jpg','Roughness')]:
 tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(LAB/'sources/environment169/blue_metal_plate'/filename));tex.projection='BOX';tex.projection_blend=.15;links.new(coords.outputs['Generated'],tex.inputs['Vector'])
 if socket=='Roughness':tex.image.colorspace_settings.name='Non-Color'
 links.new(tex.outputs['Color'],shader.inputs[socket])
display=make_material('Original subway service display',(.02,.1,.2,1),.1,.3)
nodes=display.node_tree.nodes;links=display.node_tree.links;shader=nodes.get('Principled BSDF');tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'source_display.png'));links.new(tex.outputs['Color'],shader.inputs['Base Color']);links.new(tex.outputs['Color'],shader.inputs['Emission Color']);shader.inputs['Emission Strength'].default_value=.5
parts=[]
def part(n,p,s,m,parent):
 o=box(n,p,s,m,.018);o.parent=parent;parts.append(o);return o
def panel(n,p,s,reference,parent):
 material=bpy.data.materials.new(n+' source panel');material.use_nodes=True
 tex=material.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(reference));shader=material.node_tree.nodes.get('Principled BSDF');material.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color']);shader.inputs['Roughness'].default_value=.4
 o=part(n,p,s,material,parent);return o
for item in survey['walls']:
 identifier=item['id'];x1,y1,x2,y2=item['rect'];w=(x2-x1)*gw/cw;d=(y2-y1)*gh/ch;x=(x1+x2)/2*gw/cw-gw/2;y=gh/2-(y1+y2)/2*gh/ch
 parent=bpy.data.objects.new('Occludable_'+identifier,None);bpy.context.collection.objects.link(parent)
 if 'wall' in identifier:
  part(identifier,(x,y,.85),(w/2,d/2,.85),steel,parent)
  continue
 if 'stair' in identifier:
  # Descending escalators, not solid raised obstacle cubes. Separate treads,
  # cheeks and handrails sit inside a transparent opening in the art floor.
  direction=1 if '_n' in identifier else -1
  for lane in [-1,1]:
   px=x+lane*w*.23
   for i in range(14):
    py=y+direction*(-d*.43+(i+.5)*d*.86/14);z=-(i+1)/14*1.9
    part(identifier+' tread',(px,py,z),(w*.19,d*.86/28,.055),steel,parent)
    part(identifier+' tread lip',(px,py-direction*d*.86/28,z+.06),(w*.18,.012,.009),chrome,parent)
   for side in [-1,1]:
    rail=part(identifier+' handrail',(px+side*w*.20,y,-.3),(.045,d*.47,.055),black,parent)
    rail.rotation_euler.x=direction*math.atan2(1.9,d*.86)
  for side in [-1,1]:
   part(identifier+' landing frame',(x+side*w*.49,y,.14),(.06,d*.5,.16),steel,parent)
  part(identifier+' landing light',(x,y-direction*d*.47,.035),(w*.45,.04,.025),yellow,parent)
 elif 'bench' in identifier:
  for i in range(4):
   px=x-w*.45+(i+.5)*w*.9/4
   part(identifier+' seat',(px,y,.5),(w*.9/8-.025,d*.34,.07),seat,parent)
   part(identifier+' back',(px,y+d*.32,.85),(w*.9/8-.025,.065,.32),seat,parent)
   part(identifier+' leg',(px,y,.24),(.04,d*.25,.24),steel,parent)
   for side in [-1,1]:part(identifier+' armrest',(px+side*(w*.9/8-.02),y,.75),(.025,d*.3,.025),chrome,parent)
 elif 'column' in identifier:
  part(identifier+' footing',(x,y,.12),(w*.5,d*.5,.12),steel,parent)
  part(identifier+' structural core',(x,y,1.35),(w*.28,d*.28,1.25),steel,parent)
  for side in [-1,1]:part(identifier+' illuminated face',(x+side*w*.29,y,1.35),(.025,d*.22,.6),display,parent)
  part(identifier+' crown',(x,y,2.6),(w*.38,d*.38,.1),chrome,parent)
 elif 'ticket' in identifier:
  part(identifier+' plinth',(x,y,.5),(w*.45,d*.38,.5),steel,parent)
  part(identifier+' recessed fascia',(x,y-d*.39,.65),(w*.4,.025,.25),black,parent)
  reference=LAB/f'environment-library/references/{NAME}__{identifier}.png'
  panel(identifier+' control surface',(x,y,1.08),(w*.43,d*.35,.08),reference,parent)
 else:
  part(identifier+' service bin',(x,y,.55),(w*.42,d*.42,.55),steel,parent)
  part(identifier+' lid',(x,y,1.14),(w*.45,d*.45,.06),black,parent)
  part(identifier+' indicator',(x,y-d*.43,.8),(w*.28,.015,.035),cyan,parent)
floor=bpy.data.materials.new('Original subway floor with recessed stair openings');floor.use_nodes=True
tex=floor.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'floor.png'));shader=floor.node_tree.nodes.get('Principled BSDF');floor.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color']);floor.node_tree.links.new(tex.outputs['Alpha'],shader.inputs['Alpha']);shader.inputs['Roughness'].default_value=.65;floor.surface_render_method='DITHERED'
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,0,-.02));o=bpy.context.object;o.name='OriginalSubwayFloor';o.scale=(gw/2,gh/2,1);o.data.materials.append(floor);parts.append(o)
world=bpy.data.worlds.new('Subway neutral');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.08,.1,.13,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;bpy.context.scene.world=world
for p,power in [((0,0,16),3400),((-10,-8,8),1600)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.data.energy=power;o.data.size=15
bpy.ops.object.camera_add(location=(25,-32,34));o=bpy.context.object;o.data.type='ORTHO';o.data.ortho_scale=49;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler();scene=bpy.context.scene;scene.camera=o
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.filepath=str(OUT/'overview.png');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in scene.objects:o.select_set(o.type=='MESH' or o.name.startswith('Occludable_'))
bpy.context.view_layer.objects.active=parts[0];bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
catalog=[]
for identifier,source_id in [('subway_escalator_pair','stair_nw'),('subway_seat_bank','bench_n'),('subway_service_column','column_nw'),('subway_ticket_terminal','ticket_north')]:
 root=bpy.data.objects['Occludable_'+source_id];objects=[root]+list(root.children_recursive)
 points=[o.matrix_world@Vector(c) for o in objects if o.type=='MESH' for c in o.bound_box]
 lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
 anchor=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,0 if 'escalator' in identifier else lo.z))
 root.location=-anchor
 for o in scene.objects:o.select_set(o in objects)
 bpy.ops.export_scene.gltf(filepath=str(OUT/(identifier+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
 root.location=(0,0,0)
 catalog.append({'id':identifier,'source_object_id':source_id,'source_root':root.name,'family':'Transit','models':{'blend':str(OUT/'environment.blend'),'glb':str(OUT/(identifier+'.glb'))},'dimensions':[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],'anchor':'entry_plane_normalized' if 'escalator' in identifier else 'center_ground_normalized','orientation':'glTF Y up','source_blender_anchor':list(anchor),'materials':sorted({m.name for o in objects if o.type=='MESH' for m in o.data.materials}),'artistic_status':'FIRST_ASSEMBLY_NOT_FINAL'})
(OUT/'assets.json').write_text(json.dumps(catalog,indent=2))
bpy.ops.render.render(write_still=True);print('METRO250_EXPORTED',len(parts),'meshes; first assembly, not final')
