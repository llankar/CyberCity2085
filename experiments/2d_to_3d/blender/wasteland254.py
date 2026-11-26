"""Original ashfield layout: fractured slabs, wall remnants and exposed reinforcement."""
from pathlib import Path
import bpy,json,sys,random,math
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import make_material
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=Path(__file__).resolve().parents[3];OUT=LAB/'generated/phase2/wasteland254';OUT.mkdir(parents=True,exist_ok=True)
NAME='wasteland_outdoor_02_ashfield_ruins';survey=json.loads((ROOT/f'assets/maps/{NAME}.wall-traces.json').read_text());tactics=json.loads((ROOT/f'assets/maps/{NAME}.walls.json').read_text());gw,gh=tactics['grid'];cw,ch=survey['canvas_size']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
concrete=make_material('Ruin weathered concrete',(.16,.14,.12,1),.05,.85)
nodes=concrete.node_tree.nodes;links=concrete.node_tree.links;tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'concrete_diff.jpg'));links.new(tex.outputs['Color'],nodes['Principled BSDF'].inputs['Base Color'])
rust=make_material('Exposed oxidized reinforcement',(.12,.055,.025,1),.7,.8)
source=make_material('Original ashfield slab surface',(.15,.13,.1,1),.05,.85)
tex=source.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/f'assets/maps/{NAME}.png'));source.node_tree.links.new(tex.outputs['Color'],source.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
parts=[];groups=[];rng=random.Random(254)
def mesh(name,vertices,faces,material,parent):
 data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.materials.append(material)
 uv=data.uv_layers.new()
 for face in data.polygons:
  for loop in face.loop_indices:
   p=data.vertices[data.loops[loop].vertex_index].co
   uv.data[loop].uv=((p.x+gw/2)/gw,(p.y+gh/2)/gh) if material==source else (p.x+p.y,p.z)
 o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.parent=parent;parts.append(o);return o
for item in survey['walls']:
 identifier=item['id']
 if 'wreck' in identifier:continue
 polygon=item.get('polygon')
 if polygon is None:
  x1,y1,x2,y2=item['rect'];polygon=[[x1,y1],[x2,y1],[x2,y2],[x1,y2]]
 points=[Vector((x/cw*gw-gw/2,gh/2-y/ch*gh,0)) for x,y in polygon]
 center=sum(points,Vector())/len(points)
 parent=bpy.data.objects.new('Occludable_'+identifier,None);bpy.context.collection.objects.link(parent);groups.append(identifier)
 # Separate tilted triangular slab fragments; source art defines their surface,
 # while the surveyed outline limits decorative placement.
 for i,(a,b) in enumerate(zip(points,points[1:]+points[:1])):
  c=center+(a-center)*.12;top=[a+Vector((0,0,rng.uniform(.08,.35))),b+Vector((0,0,rng.uniform(.08,.35))),c+Vector((0,0,rng.uniform(.3,.85)))]
  vertices=[tuple(p) for p in top]+[tuple(Vector((p.x,p.y,.01))) for p in top]
  mesh(identifier+' fractured slab'+str(i),vertices,[[0,1,2],[5,4,3],[0,3,4,1],[1,4,5,2],[2,5,3,0]],source,parent)
  if 'ruin' not in identifier and 'wall' not in identifier:continue
  if i%2:continue
  delta=b-a
  if delta.length<.3:continue
  normal=Vector((delta.y,-delta.x,0)).normalized()*.08
  # Interrupted wall segments with chipped, unequal top heights.
  for start,end in [(0,.42),(.60,.93)]:
   p=a+delta*start;q=a+delta*end;hp=rng.uniform(.5,1.7);hq=rng.uniform(.5,1.7)
   vertices=[tuple(p-normal),tuple(q-normal),tuple(q+normal),tuple(p+normal),tuple(p-normal+Vector((0,0,hp))),tuple(q-normal+Vector((0,0,hq))),tuple(q+normal+Vector((0,0,hq))),tuple(p+normal+Vector((0,0,hp)))]
   mesh(identifier+' broken wall',vertices,[[0,3,2,1],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7]],concrete,parent)
   for t in [.25,.65]:
    position=p.lerp(q,t)+Vector((0,0,hp*(1-t)+hq*t))
    bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.018,depth=.45,location=position+Vector((0,0,.16)))
    o=bpy.context.object;o.name=identifier+' exposed rebar';o.rotation_euler=(rng.uniform(-.35,.35),rng.uniform(-.35,.35),0);o.parent=parent;o.data.materials.append(rust);parts.append(o)
floor=make_material('Original ashfield ground',(.15,.13,.1,1),.05,.9);tex=floor.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'floor.png'));floor.node_tree.links.new(tex.outputs['Color'],floor.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,0,-.025));o=bpy.context.object;o.name='OriginalAshfieldGround';o.scale=(gw/2,gh/2,1);o.data.materials.append(floor);parts.append(o)
world=bpy.data.worlds.new('Ashfield neutral');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.11,.1,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;bpy.context.scene.world=world
for p,power in [((0,0,16),3400),((-10,-8,8),1600)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.data.energy=power;o.data.size=15
bpy.ops.object.camera_add(location=(25,-32,34));o=bpy.context.object;o.data.type='ORTHO';o.data.ortho_scale=49;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler();scene=bpy.context.scene;scene.camera=o
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.filepath=str(OUT/'overview.png');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in scene.objects:o.select_set(o.type=='MESH' or o.name.startswith('Occludable_'))
bpy.context.view_layer.objects.active=parts[0];bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
(OUT/'placements.json').write_text(json.dumps({'map':NAME,'reconstructed_groups':groups,'retained_2d':['wreck_w','wreck_ne','wreck_e'],'tactical_mutation':False,'artistic_status':'FIRST_ASSEMBLY_NOT_FINAL'},indent=2))
bpy.ops.render.render(write_still=True);print('WASTELAND254_EXPORTED',len(groups),'groups',len(parts),'parts')
