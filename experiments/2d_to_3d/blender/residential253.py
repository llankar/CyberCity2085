"""Original residential footprints/roofs with acquired modular facade components."""
from pathlib import Path
import bpy,json,sys,math
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import make_material,box
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=Path(__file__).resolve().parents[3];OUT=LAB/'generated/phase2/residential253';OUT.mkdir(parents=True,exist_ok=True)
NAME='city_district_apartment_block';survey=json.loads((ROOT/f'assets/maps/{NAME}.wall-traces.json').read_text());tactics=json.loads((ROOT/f'assets/maps/{NAME}.walls.json').read_text());gw,gh=tactics['grid'];cw,ch=survey['canvas_size']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
concrete=make_material('Residential weathered concrete',(.13,.17,.20,1),.15,.75)
nodes=concrete.node_tree.nodes;links=concrete.node_tree.links;shader=nodes.get('Principled BSDF');coords=nodes.new('ShaderNodeTexCoord')
for name,socket in [('diff.jpg','Base Color'),('rough.jpg','Roughness')]:
 tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'concrete_diff.jpg' if name=='diff.jpg' else LAB/'sources/environment169/concrete_wall_001'/name));tex.projection='BOX';tex.projection_blend=.1;links.new(coords.outputs['Generated'],tex.inputs['Vector'])
 if socket=='Roughness':tex.image.colorspace_settings.name='Non-Color'
 links.new(tex.outputs['Color'],shader.inputs[socket])
# Tone actual photographic albedo for the existing night palette.
roof=make_material('Original residential roof artwork',(.1,.1,.1,1),.35,.65)
tex=roof.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/f'assets/maps/{NAME}.png'));roof.node_tree.links.new(tex.outputs['Color'],roof.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
steel=make_material('Residential dark service trim',(.035,.06,.075,1),.7,.45)
def template(name):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(LAB/'sources/environment169/modular_urban_apartments_facade/modular_urban_apartments_facade_1k.gltf'));objects=set(bpy.data.objects)-before
 o=next(o for o in objects if o.type=='MESH' and o.name==name);data=o.data.copy();data.transform(o.matrix_world)
 low=Vector([min(v.co[i] for v in data.vertices) for i in range(3)]);high=Vector([max(v.co[i] for v in data.vertices) for i in range(3)]);dims=high-low;data.transform(Matrix.Translation(-(low+high)/2))
 if dims.x<dims.y:data.transform(Matrix.Rotation(math.pi/2,4,'Z'));dims.x,dims.y=dims.y,dims.x
 for o in objects:bpy.data.objects.remove(o,do_unlink=True)
 return data,dims
door,dd=template('door_window_small_05');window,wd=template('window_centered_large_03')
parts=[];buildings=[]
def module(name,data,dims,position,width,height,angle,parent):
 o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.parent=parent
 o.matrix_world=Matrix.Translation(Vector(position))@Matrix.Rotation(angle,4,'Z')@Matrix.Diagonal(Vector((width/dims.x,min(1,.20/dims.y),height/dims.z,1)));parts.append(o)
for index,item in enumerate(survey['walls']):
 identifier=item['id']
 if 'building' not in identifier and 'tower' not in identifier and 'extension' not in identifier:continue
 polygon=item.get('polygon')
 if polygon is None:
  x1,y1,x2,y2=item['rect'];polygon=[[x1,y1],[x2,y1],[x2,y2],[x1,y2]]
 points=[Vector((x/cw*gw-gw/2,gh/2-y/ch*gh,0)) for x,y in polygon]
 if sum(a.x*b.y-b.x*a.y for a,b in zip(points,points[1:]+points[:1]))<0:points.reverse()
 height=3.1+(index%3)*.6;n=len(points);vertices=[tuple(p) for p in points]+[tuple(p+Vector((0,0,height))) for p in points]
 faces=[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
 data=bpy.data.meshes.new(identifier);data.from_pydata(vertices,[],faces);data.materials.append(concrete);data.materials.append(roof)
 parent=bpy.data.objects.new('Occludable_'+identifier,None);bpy.context.collection.objects.link(parent)
 body=bpy.data.objects.new(identifier+' shell',data);bpy.context.collection.objects.link(body);body.parent=parent;parts.append(body)
 uv=data.uv_layers.new()
 for face in data.polygons:
  face.material_index=1 if face.index==1 else 0
  for loop in face.loop_indices:
   p=data.vertices[data.loops[loop].vertex_index].co
   uv.data[loop].uv=((p.x+gw/2)/gw,(p.y+gh/2)/gh) if face.index==1 else (p.x/2,p.z/2)
 for edge,(a,b) in enumerate(zip(points,points[1:]+points[:1])):
  delta=b-a;length=delta.length
  if length<1.4:continue
  normal=Vector((delta.y,-delta.x,0)).normalized();angle=math.atan2(delta.y,delta.x)
  # Acquired facade modules are real meshes. These wall elevations are inferred;
  # authentic roof and street layouts remain the art/placement reference.
  for j in range(max(1,int(length/1.7))):
   p=a+delta*((j+.5)/max(1,int(length/1.7)))+normal*.08
   module(identifier+' window',window,wd,tuple(p+Vector((0,0,2.1))),min(1.2,length*.6),.95,angle,parent)
  if edge==0:
   p=(a+b)/2+normal*.12;module(identifier+' entrance',door,dd,tuple(p+Vector((0,0,.95))),1.05,1.85,angle,parent)
 buildings.append(identifier)
floor=make_material('Residential original street floor',(.1,.1,.1,1),.1,.7);tex=floor.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'floor.png'));floor.node_tree.links.new(tex.outputs['Color'],floor.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,0,-.025));o=bpy.context.object;o.name='OriginalResidentialStreets';o.scale=(gw/2,gh/2,1);o.data.materials.append(floor);parts.append(o)
world=bpy.data.worlds.new('Residential neutral');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.08,.1,.13,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;bpy.context.scene.world=world
for p,power in [((0,0,16),3400),((-10,-8,8),1600)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.data.energy=power;o.data.size=15
bpy.ops.object.camera_add(location=(25,-32,34));o=bpy.context.object;o.data.type='ORTHO';o.data.ortho_scale=49;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler();scene=bpy.context.scene;scene.camera=o
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.filepath=str(OUT/'overview.png');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in scene.objects:o.select_set(o.type=='MESH' or o.name.startswith('Occludable_'))
bpy.context.view_layer.objects.active=parts[0];bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
(OUT/'placements.json').write_text(json.dumps({'map':NAME,'buildings':buildings,'acquired_module_families':2,'tactical_mutation':False,'artistic_status':'FIRST_ASSEMBLY_NOT_FINAL','remaining':'Street props/vegetation and detailed elevations remain open'},indent=2))
bpy.ops.render.render(write_still=True);print('RESIDENTIAL253_EXPORTED',len(buildings),'buildings',len(parts),'parts')
