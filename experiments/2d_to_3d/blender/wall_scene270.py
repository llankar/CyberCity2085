"""Apply one reusable dimensioned wall family to two compatible experimental maps."""
from pathlib import Path
import bpy,sys,json,math,argparse
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from modular_wall269 import build_wall
from create_hardsurface_crate import make_material
from track_ends272 import extend_track_ends
LAB=Path('E:/CyberCity2085-3d-lab')
parser=argparse.ArgumentParser();parser.add_argument('--map',choices=['factory','metro'],required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
source='factory266' if args.map=='factory' else 'metro264';OUT=LAB/'generated/phase2'/(args.map+'270');OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2'/source/'environment.blend'));bpy.context.preferences.filepaths.save_version=0
metal=make_material('Wall269 worn steel PBR',(.08,.10,.12,1),.8,.6)
for filename,socket in [('diff.jpg','Base Color'),('rough.jpg','Roughness')]:
 node=metal.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(LAB/'sources/environment169/blue_metal_plate'/filename))
 if socket!='Base Color':node.image.colorspace_settings.name='Non-Color'
 metal.node_tree.links.new(node.outputs['Color'],metal.node_tree.nodes['Principled BSDF'].inputs[socket])
dark=make_material('Wall269 recessed backing',(.018,.025,.03,1),.45,.85)
trim=make_material('Wall269 oxidized service fittings',(.16,.105,.055,1),.7,.65)
colour=(.9,.38,.06,1) if args.map=='factory' else (.02,.4,.65,1)
lamp=make_material('Wall269 integrated '+args.map+' light',colour,.15,.4,1.8)
materials=[metal,dark,trim,lamp];records=[];lights=[]
roots=[o for o in bpy.data.objects if o.name.startswith('Occludable_') and 'wall' in o.name.lower()]
for root in roots:
 meshes=[o for o in root.children_recursive if o.type=='MESH']
 points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
 if not points:continue
 lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);size=hi-lo
 center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));angle=0 if size.x>=size.y else math.pi/2
 length=max(size.x,size.y);depth=min(size.x,size.y)
 for o in list(root.children_recursive):bpy.data.objects.remove(o,do_unlink=True)
 opening=None;lamp_center=center;actual_bays=0
 if args.map=='metro' and root.name in ['Occludable_west_wall','Occludable_east_wall']:
  # Railway exits must remain physically open. The source boundary footprint
  # is retained as tactical data, but is not a continuous visual wall here.
  opening=[14-304*28/540-.20,14-236*28/540+.20]
  for lower,upper in [(lo.y,min(hi.y,opening[0])),(max(lo.y,opening[1]),hi.y)]:
   if upper-lower<=.1:continue
   middle=Vector((center.x,(lower+upper)/2,center.z))
   build_wall(root,middle,upper-lower,depth,size.z,math.pi/2,materials)
   actual_bays+=math.ceil((upper-lower)/2)
   if lamp_center==center:lamp_center=middle
 else:
  build_wall(root,center,length,depth,size.z,angle,materials)
  actual_bays=math.ceil(length/2)
 records.append({'root':root.name,'source_bounds':[list(lo),list(hi)],'rail_exit_opening_blender_y':opening,'module_bays':actual_bays,'family':'service_wall269','material_variant':args.map})
 if len(lights)<2:
  normal=Vector((-math.sin(angle),math.cos(angle),0));side=-1 if normal.dot(center)>0 else 1
  data=bpy.data.lights.new('Wall270 local lamp','POINT');data.energy=2.5;data.color=colour[:3];data.cutoff_distance=3;data.use_custom_distance=True
  light=bpy.data.objects.new('Wall270LocalLight',data);bpy.context.collection.objects.link(light);light.location=lamp_center+normal*side*(depth/2+.4)+Vector((0,0,size.z*.84));light.parent=root;lights.append(light)
if args.map=='metro':
 extend_track_ends()
 floor=bpy.data.materials['Original subway floor with recessed stair openings']
 next(n for n in floor.node_tree.nodes if n.type=='TEX_IMAGE').image=bpy.data.images.load(str(OUT/'floor.png'))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH' or o.name.startswith('Occludable_') or o.name=='Track263VisualOnly' or o in lights)
bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True,export_lights=True)
(OUT/'walls.json').write_text(json.dumps({'source':source,'family':'service_wall269','variant':args.map,'walls':records,'tactical_change':False,'artistic_status':'NEEDS_NATIVE_REVIEW'},indent=2))
# Save a true standalone, reusable two-metre module after preserving the map.
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
prototype=bpy.data.objects.new('ServiceWall269_'+args.map,None);bpy.context.collection.objects.link(prototype)
build_wall(prototype,(0,0,0),2,.30,1.7,0,materials)
bpy.ops.outliner.orphans_purge(do_recursive=True)
asset=LAB/'environment-library/assets'/('service_wall269_'+args.map);asset.mkdir(parents=True,exist_ok=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(asset/'source.blend'))
for o in bpy.context.scene.objects:o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(asset/'model.glb'),export_format='GLB',use_selection=True,export_apply=True)
(asset/'asset.json').write_text(json.dumps({'id':asset.name,'family':'Architecture','models':{'blend':str(asset/'source.blend'),'glb':str(asset/'model.glb')},'anchor':'center_ground_normalized','orientation':'glTF Y up; length X','dimensions_nominal':[2,1.7,.3],'provenance':'Precise modular architecture guided by original map proportions and service fixtures; existing worn-metal PBR; unseen side construction inferred','variant':args.map,'used_in':[str(OUT/'environment.glb')],'artistic_status':'NEEDS_NATIVE_REVIEW'},indent=2))
print('MODULAR_WALL270_EXPORTED',args.map,len(records),'source walls',sum(r['module_bays'] for r in records),'bays')
