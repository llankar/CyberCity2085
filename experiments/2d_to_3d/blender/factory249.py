"""First industrial map pass: reuse three existing asset families, retain unmatched art."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from library_placement import place
from create_hardsurface_crate import box,make_material
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=Path(__file__).resolve().parents[3]
OUT=LAB/'generated/phase2/factory249';OUT.mkdir(parents=True,exist_ok=True)
NAME='city_industrial_factory_floor';survey=json.loads((ROOT/f'assets/maps/{NAME}.wall-traces.json').read_text())
tactics=json.loads((ROOT/f'assets/maps/{NAME}.walls.json').read_text());gw,gh=tactics['grid'];cw,ch=survey['canvas_size']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
steel=make_material('Factory worn structural steel',(.08,.11,.13,1),.75,.5)
models={'west_generator':LAB/'generated/phase2/generator01/generator.glb'}
# The available compressor has the wrong silhouette/scale for the four corner
# machines. Leave their original art intact until a better model is available.
for identifier in ['north_crates_w','north_crates_m','north_crates_e','south_crates_w','south_crates_e']:
 models[identifier]=LAB/'generated/phase2/crate_procedural/crate_procedural.glb'
used=[];parts=[]
for item in survey['walls']:
 if 'rect' not in item:continue
 x1,y1,x2,y2=item['rect'];w=(x2-x1)*gw/cw;d=(y2-y1)*gh/ch;x=(x1+x2)/2*gw/cw-gw/2;y=gh/2-(y1+y2)/2*gh/ch
 identifier=item['id'];parent=bpy.data.objects.new('Occludable_'+identifier,None);bpy.context.collection.objects.link(parent)
 if 'wall' in identifier:
  o=box(identifier,(x,y,.85),(w/2,d/2,.85),steel,.025);o.parent=parent;parts.append(o)
 elif identifier in models:
  o=box(identifier+' mounting platform',(x,y,.08),(w/2,d/2,.08),steel,.025);o.parent=parent;parts.append(o)
  if 'crates' in identifier:
   nx=max(1,round(w/1.5));ny=max(1,round(d/1.3))
   for ix in range(nx):
    for iy in range(ny):parts+=place(models[identifier],parent,(x-w/2+(ix+.5)*w/nx,y-d/2+(iy+.5)*d/ny,0),(w/nx*.9,d/ny*.9,1.05))
  else:parts+=place(models[identifier],parent,(x,y,0),(w,d,1.6 if 'machine' in identifier else 1.35))
  used.append({'object':identifier,'asset':str(models[identifier]),'position_blender':[x,y,0],'dimensions_blender':[w,d,1.6 if 'machine' in identifier else 1.35]})
 else:bpy.data.objects.remove(parent,do_unlink=True)
floor=bpy.data.materials.new('Retained factory floor');floor.use_nodes=True
tex=floor.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'floor.png'));floor.node_tree.links.new(tex.outputs['Color'],floor.node_tree.nodes['Principled BSDF'].inputs['Base Color']);floor.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.65
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,0,-.025));o=bpy.context.object;o.name='OriginalIndustrialFloor';o.scale=(gw/2,gh/2,1);o.data.materials.append(floor);parts.append(o)
world=bpy.data.worlds.new('Industrial neutral');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.08,.1,.13,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;bpy.context.scene.world=world
for p,power in [((0,0,16),3400),((-10,-8,8),1800)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.data.energy=power;o.data.size=15
bpy.ops.object.camera_add(location=(25,-32,34));o=bpy.context.object;o.data.type='ORTHO';o.data.ortho_scale=49;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler();scene=bpy.context.scene;scene.camera=o
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.filepath=str(OUT/'overview.png')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in scene.objects:o.select_set(o.type=='MESH' or o.name.startswith('Occludable_'))
bpy.context.view_layer.objects.active=parts[0];bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
(OUT/'placements.json').write_text(json.dumps({'map':NAME,'reused_instances':used,'new_generated_assets':0,'unmatched_objects':[r['id'] for r in survey['walls'] if r['id'] not in models and 'wall' not in r['id']],'tactical_mutation':False,'artistic_status':'PARTIAL_RECONSTRUCTION'},indent=2))
bpy.ops.render.render(write_still=True);print('FACTORY249_EXPORTED',len(used),'reused instances')
