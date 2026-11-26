"""Replace repeated factory bays on two buildings with retained urban kit meshes."""
from pathlib import Path
import bpy,math,json,numpy as np
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase206';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase199/environment.blend'))
pack=LAB/'sources/environment169/modular_urban_apartments_facade/modular_urban_apartments_facade_1k.gltf'
before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(pack));imported=set(bpy.data.objects)-before
names=['wall_window_centered_double_01','window_centered_double_01'];templates={}
for name in names:
 obj=next(o for o in imported if o.type=='MESH' and o.name==name);mesh=obj.data.copy();mesh.transform(obj.matrix_world)
 lo=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)]);hi=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)]);center=(lo+hi)/2;mesh.transform(Matrix.Translation(-center));templates[name]=[mesh,hi-lo,center]
for name,(mesh,dims,center) in templates.items():
 print('FACADE206_TEMPLATE',name,list(dims),list(center),flush=True)
 if dims.x<dims.y:
  rot=Matrix.Rotation(math.pi/2,4,'Z');mesh.transform(rot);dims.x,dims.y=dims.y,dims.x;center[:]=rot.to_3x3()@center
for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
wall,dims,wall_center=templates[names[0]];window,window_dims,window_center=templates[names[1]]
relative=window_center-wall_center
assert relative.length<3,('Unexpected source module alignment',list(relative))
materials={};images={}
def palette(source,color):
 key=(source.name,color)
 if key in materials:return materials[key]
 mat=source.copy();mat.name='Facade206_'+source.name+'_'+str(len(materials))
 if mat.use_nodes and not any(x in mat.name.lower() for x in ['glass','emiss']):
  shader=mat.node_tree.nodes.get('Principled BSDF')
  if shader:
   shader.inputs['Roughness'].default_value=.8;shader.inputs['Metallic'].default_value=.08
   socket=shader.inputs['Base Color']
   if socket.is_linked:
    tex=socket.links[0].from_node
    if tex.type=='TEX_IMAGE' and tex.image:
     image_key=(tex.image.name,color)
     if image_key not in images:
      img=tex.image.copy();px=np.empty(len(img.pixels),dtype=np.float32);img.pixels.foreach_get(px);px.reshape(-1,4)[:,:3]*=color;img.pixels.foreach_set(px);img.update();img.filepath_raw=str(OUT/('facade_'+str(len(images))+'.png'));img.file_format='PNG';img.save();img.pack();images[image_key]=img
     tex.image=images[image_key]
   else:
    c=list(socket.default_value);socket.default_value=tuple(c[i]*color[i] for i in range(3))+(c[3],)
 materials[key]=mat;return mat
records=[]
for name,color in [('north_building',(.45,.55,.6)),('south_building_w',(.55,.44,.38))]:
 root=bpy.data.objects['Occludable_'+name]
 bays=[o for o in root.children if o.name.startswith('AuthoredFacade_wall_window')]
 for bay in bays:
  old=bay.location.copy()
  points=[bay.matrix_world@v.co for v in bay.data.vertices]
  center=Vector([(min(v[i] for v in points)+max(v[i] for v in points))/2 for i in range(3)])
  normal=bay.matrix_world.to_3x3().inverted().transposed()@max(bay.data.polygons,key=lambda f:f.area).normal
  normal.z=0;normal.normalize()
  body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
  body_points=[body.matrix_world@Vector(v) for v in body.bound_box];body_center=sum(body_points,Vector())/8
  if normal.dot(center-body_center)<0:normal=-normal
  rotation=(-normal).to_track_quat('Y','Z').to_matrix()
  print('FACADE206_WORLD_BAY',name,list(center),list(normal),flush=True)
  for obj in list(root.children):
   if obj.name.startswith('AuthoredFacade_window') and (obj.location-old).length<1.3:bpy.data.objects.remove(obj,do_unlink=True)
  bay.data=wall.copy();bay.name='Facade206 urban wall';scale=Vector((2.98/dims.x,(min(1,.20/dims.y) if dims.y>1e-6 else 1),2.98/dims.z));bay.matrix_world=Matrix.Translation(center)@rotation.to_4x4()@Matrix.Diagonal((*scale,1))
  for slot in bay.material_slots:
   if slot.material:slot.material=palette(slot.material,color)
  insert=bpy.data.objects.new('Facade206 urban window',window.copy());bpy.context.collection.objects.link(insert);insert.parent=root
  window_scale=Vector((scale.x,min(1,.18/max(.001,window_dims.y)),scale.z))
  position=center+rotation@Vector(tuple(relative[i]*window_scale[i] for i in range(3)))+normal*.055
  insert.matrix_world=Matrix.Translation(position)@rotation.to_4x4()@Matrix.Diagonal((*window_scale,1))
  for slot in insert.material_slots:
   if slot.material:slot.material=palette(slot.material,color)
  records.append(name)
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'));bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'facades.json').write_text(json.dumps({'buildings':sorted(set(records)),'replaced_bays':len(records),'source':str(pack),'scope':'cosmetic facade replacement; original map cells and paths retained'},indent=2));print('FACADE206_READY',len(records),flush=True)
