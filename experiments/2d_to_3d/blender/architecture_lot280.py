"""Shared concrete UV/PBR repair and acquired facade reuse; review whole maps later."""
from pathlib import Path
import bpy,json,sys,math
from mathutils import Vector,Matrix
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import make_material
LAB=Path('E:/CyberCity2085-3d-lab');ROOT=Path(__file__).resolve().parents[3]

def physical_uv(mesh,face):
 normal=face.normal;horizontal=Vector((-normal.y,normal.x,0))
 if horizontal.length<.001:horizontal=Vector((1,0,0))
 horizontal.normalize();uv=mesh.uv_layers.active or mesh.uv_layers.new(name='UVMap')
 for index in face.loop_indices:
  p=mesh.vertices[mesh.loops[index].vertex_index].co
  uv.data[index].uv=(p.dot(horizontal)/1.5,p.z/1.5)

def concrete_material(material):
 for node in material.node_tree.nodes:
  if node.type=='TEX_IMAGE':
   node.projection='FLAT'
   for link in list(node.inputs['Vector'].links):material.node_tree.links.remove(link)
 shader=material.node_tree.nodes.get('Principled BSDF')
 tex=material.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(LAB/'sources/environment169/concrete_wall_001/nor_gl.jpg'));tex.image.colorspace_settings.name='Non-Color'
 normal=material.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.45
 material.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);material.node_tree.links.new(normal.outputs['Normal'],shader.inputs['Normal'])

def pipe(root,x,y,height,material):
 vertices=[];faces=[];radius=.032
 for z in [.10,height-.08]:
  for j in range(12):vertices.append((x+radius*math.cos(j*math.tau/12),y+radius*math.sin(j*math.tau/12),z))
 for j in range(12):faces.append((j,(j+1)%12,(j+1)%12+12,j+12))
 faces.extend([tuple(reversed(range(12))),tuple(range(12,24))])
 data=bpy.data.meshes.new('Facade280 vertical service pipe');data.from_pydata(vertices,[],faces);data.materials.append(material)
 uv=data.uv_layers.new(name='UVMap')
 for face in data.polygons:
  face.use_smooth=face.index<12
  for index in face.loop_indices:
   p=data.vertices[data.loops[index].vertex_index].co;uv.data[index].uv=(math.atan2(p.y-y,p.x-x)/math.tau,p.z/1.5)
 obj=bpy.data.objects.new('Facade280 vertical service pipe',data);bpy.context.collection.objects.link(obj);obj.parent=root

for source,folder,name in [('residential278','residential280','city_district_apartment_block'),('wasteland254','wasteland280','wasteland_outdoor_02_ashfield_ruins')]:
 out=LAB/'generated/phase2'/folder;out.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2'/source/'environment.blend'));bpy.context.preferences.filepaths.save_version=0
 count=0;fixtures=0
 if folder=='residential280':
  concrete=bpy.data.materials['Residential weathered concrete'];concrete_material(concrete)
  # Keep genuine roof UVs; each vertical face gets its own physical tangent.
  shells=[o for o in bpy.data.objects if o.type=='MESH' and o.name.endswith(' shell')]
  trim=bpy.data.materials.get('Residential dark service trim') or make_material('Residential dark service trim',(.035,.06,.075,1),.7,.55)
  for shell in shells:
   shell.data.update()
   for face in shell.data.polygons:
    if face.material_index==0 and abs(face.normal.z)<.55:physical_uv(shell.data,face);count+=1
   bottom=min(v.co.z for v in shell.data.vertices);height=max(v.co.z for v in shell.data.vertices)-bottom
   # Attached round services sit against existing corners, not across streets.
   points=[v.co.copy() for v in shell.data.vertices if abs(v.co.z-bottom)<.001]
   for p in points[::2]:pipe(shell.parent,p.x,p.y,height,trim);fixtures+=1
  texture_folder=out/'materials';texture_folder.mkdir(exist_ok=True)
  for material in bpy.data.materials:
   if not material.name.startswith('modular_urban_apartments_facade'):continue
   tint=(.22,.40,.58) if 'glass' in material.name else (.38,.44,.49) if 'trim' in material.name else (.68,.72,.76)
   for index,node in enumerate(material.node_tree.nodes if material.use_nodes else []):
    if node.type!='TEX_IMAGE' or not node.image or node.image.colorspace_settings.name=='Non-Color':continue
    width,pixel_height=node.image.size
    pixels=np.empty(width*pixel_height*4,dtype=np.float32);node.image.pixels.foreach_get(pixels);pixels=pixels.reshape((-1,4))
    pixels[:,:3]*=np.array(tint,dtype=np.float32)**2.2
    target=texture_folder/(material.name.replace('.','_')+'_'+str(index)+'.png')
    image=bpy.data.images.new(target.stem,width=width,height=pixel_height,alpha=True);image.colorspace_settings.name='sRGB';image.pixels.foreach_set(pixels.ravel());image.filepath_raw=str(target);image.file_format='PNG';image.save();node.image=image
  # Reuse genuine acquired door/window geometry; do not replace it with boxes.
  subset=[]
  for label in ['window','entrance']:
   original=next(o for o in bpy.data.objects if o.type=='MESH' and (' '+label) in o.name)
   subset.append((label,original.data.copy(),original.matrix_world.copy()))
 else:
  concrete=bpy.data.materials['Ruin weathered concrete'];concrete_material(concrete)
  for obj in [o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name.startswith('Occludable_')]:
   if not any(m and m.name in ['Ruin weathered concrete','Original ashfield slab surface'] for m in obj.data.materials):continue
   if concrete.name not in {m.name for m in obj.data.materials if m}:obj.data.materials.append(concrete)
   slot=next(i for i,m in enumerate(obj.data.materials) if m==concrete)
   obj.data.update()
   for face in obj.data.polygons:
    if abs(face.normal.z)<.55:
     face.material_index=slot;physical_uv(obj.data,face);count+=1
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'environment.blend'))
 for obj in bpy.context.scene.objects:obj.select_set(obj.type=='MESH' or obj.name.startswith('Occludable_'))
 bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH')
 bpy.ops.export_scene.gltf(filepath=str(out/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
 (out/'architecture.json').write_text(json.dumps({'source':source,'map':name,'vertical_faces_repaired':count,'attached_service_pipes':fixtures,'source_roofs_preserved':True,'tactical_mutation':False,'artistic_status':'NEEDS_ENSEMBLE_REVIEW'},indent=2))
 if folder=='residential280':
  # Save the two acquired, retinted modular parts once, rather than duplicating
  # the full scene into each library source file. No per-part render pass.
  for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
  library=LAB/'environment-library/assets/urban_facade280';library.mkdir(parents=True,exist_ok=True);parts=[]
  for label,data,transform in subset:
   data.transform(Matrix.Diagonal(Vector((*transform.to_scale(),1))));lo=Vector([min(v.co[i] for v in data.vertices) for i in range(3)]);hi=Vector([max(v.co[i] for v in data.vertices) for i in range(3)])
   data.transform(Matrix.Translation(Vector((-(lo.x+hi.x)/2,-(lo.y+hi.y)/2,-lo.z))))
   obj=bpy.data.objects.new('Urban280 '+label,data);bpy.context.collection.objects.link(obj);parts.append(obj)
   for other in bpy.context.scene.objects:other.select_set(other==obj)
   bpy.context.view_layer.objects.active=obj;bpy.ops.export_scene.gltf(filepath=str(library/(label+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
   obj.location.x=4*len(parts)
  bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(library/'source.blend'))
  (library/'asset.json').write_text(json.dumps({'id':'urban_facade280','family':'Architecture','models':{'blend':str(library/'source.blend'),'window':str(library/'window.glb'),'door':str(library/'entrance.glb')},'provenance':'Retained acquired modular_urban_apartments_facade meshes, retinted for original night palette; no new IA inference','used_in':[str(out/'environment.glb')],'artistic_status':'NEEDS_ENSEMBLE_REVIEW'},indent=2))
 print('ARCHITECTURE280_BATCH_EXPORTED',folder,count,'physical-UV faces',fixtures,'services',flush=True)
