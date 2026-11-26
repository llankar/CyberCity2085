"""Normalize painted Hunyuan arm at its pedestal and attach inferred PBR maps."""
from pathlib import Path
import bpy,sys,json,argparse,math
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab')
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,default=LAB/'generated/phase2/arm256/paint/mesh.glb')
parser.add_argument('--output',type=Path,default=LAB/'environment-library/assets/industrial_arm256')
parser.add_argument('--asset-id',default='industrial_arm256')
parser.add_argument('--source-object',default='west_assembly')
parser.add_argument('--height',type=float,default=2.1)
parser.add_argument('--high-definition',type=Path,default=LAB/'generated/phase2/arm256/shape/mesh.glb')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
SOURCE=args.source.resolve();OUT=args.output.resolve()
if not all(p.is_relative_to(LAB.resolve()) for p in [SOURCE,OUT,args.high_definition.resolve()]):raise ValueError('Experimental meshes must stay on E: lab')
if not math.isfinite(args.height) or not .1<=args.height<=20:raise ValueError('Invalid nominal asset height')
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
bpy.ops.import_scene.gltf(filepath=str(SOURCE));objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
base=[p for p in points if p.z<lo.z+(hi.z-lo.z)*.035]
anchor=Vector(((min(p.x for p in base)+max(p.x for p in base))/2,(min(p.y for p in base)+max(p.y for p in base))/2,lo.z));factor=args.height/(hi.z-lo.z)
for o in objects:
 transform=Matrix.Scale(factor,4)@Matrix.Translation(-anchor)@o.matrix_world
 o.parent=None;o.data.transform(transform);o.matrix_world=Matrix.Identity(4)
 for material in o.data.materials:
  shader=material.node_tree.nodes.get('Principled BSDF')
  for name,socket in [('albedo.png','Base Color'),('roughness.png','Roughness'),('metallic.png','Metallic')]:
   tex=material.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/name))
   if socket!='Base Color':tex.image.colorspace_settings.name='Non-Color'
   material.node_tree.links.new(tex.outputs['Color'],shader.inputs[socket])
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'source.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.export_scene.gltf(filepath=str(OUT/'model.glb'),export_format='GLB',use_selection=True,export_apply=True)
points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
(OUT/'asset.json').write_text(json.dumps({'id':args.asset_id,'family':'Industry','models':{'blend':str(OUT/'source.blend'),'glb':str(OUT/'model.glb'),'high_definition':str(args.high_definition)},'source_map':'city_industrial_factory_floor','source_object_id':args.source_object,'dimensions':[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],'anchor':'pedestal_ground_normalized','orientation':'glTF Y up','provenance':'Original map -> imagegen inferred oblique reference -> Hunyuan2mini -> Hunyuan paint -> Blender; side/back geometry inferred','authentic_views':1,'generated_views':1,'textures':[str(OUT/'albedo.png'),str(OUT/'roughness.png'),str(OUT/'metallic.png')],'pbr_note':'Roughness and metallic masks are artistic estimates derived from colour, not measured material scans','artistic_status':'NEEDS_NATIVE_REVIEW'},indent=2))
print('INDUSTRIAL_ARM256_FINISHED',len(objects),'meshes',list(hi-lo))
