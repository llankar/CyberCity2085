"""Source-derived cloth and real recessed display trays on one original shop."""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase235';OUT.mkdir(exist_ok=True)
ASSET=LAB/'environment-library/assets/market_southeast_display'
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase234/environment.blend'))
root=bpy.data.objects['Occludable_market_se'];body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
points=[body.matrix_world@Vector(p) for p in body.bound_box]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
cx=(lo.x+hi.x)/2;cy=(lo.y+hi.y)/2;width=min(hi.x-lo.x-.3,5.5);depth=min(hi.y-lo.y-.3,3.4);front=cy-depth/2
removed=[]
for old in list(root.children_recursive):
 if old.name.startswith(('Industry216 salvaged','Kiosk207_ArmoredCap','Kiosk207_LuminousValance','Store197 sealed components','Store197 rear stock')) or (old.name.startswith('Kiosk207_AuthoredServicePart') and old.matrix_world.translation.z>2.5):
  removed.append(old.name);bpy.data.objects.remove(old,do_unlink=True)
steel=bpy.data.materials['Kiosk207_WeatheredSteel']
for label in root.children_recursive:
 if label.type=='FONT' and label.name.startswith('Store197 shop identifier'):
  label.data=label.data.copy();label.data.body='TRADER // EXCHANGE'
def part(name,position,half,material):
 obj=box('Original235 '+name,position,half,material,.008);world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world;return obj
def source_material(name):
 mat=bpy.data.materials.new('Original235 '+name);mat.use_nodes=True
 shader=mat.node_tree.nodes['Principled BSDF'];shader.inputs['Roughness'].default_value=.91
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ASSET/(name+'.png')))
 mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color']);return mat
# Shallow trays have bottom, raised rim and corner feet, not freestanding textured planes.
tray_w=min(.56,(width-.3)/4);tray_d=.62
for index in range(4):
 x=cx+(index-1.5)*(tray_w+.075);y=front+.40;z=.87
 part('tray shell',(x,y,z),(tray_w/2,tray_d/2,.045),steel)
 for side in [-1,1]:
  part('tray side',(x+side*(tray_w/2-.018),y,z+.085),(.018,tray_d/2,.055),steel)
  part('tray end',(x,y+side*(tray_d/2-.018),z+.085),(tray_w/2,.018,.055),steel)
 obj=part('source contents',(x,y,z+.052),(tray_w/2-.038,tray_d/2-.038,.012),source_material('tray'+str(index)))
 # Top mapping of the genuine source interior; hidden content sides interpreted.
 uv=obj.data.uv_layers.active or obj.data.uv_layers.new()
 for poly in obj.data.polygons:
  for loop in poly.loop_indices:
   co=obj.data.vertices[obj.data.loops[loop].vertex_index].co
   uv.data[loop].uv=(co.x/(tray_w-.076)+.5,co.y/(tray_d-.076)+.5)
# Blue draped cover above the rear of the existing footprint, leaving trays readable.
material=source_material('cloth');vertices=[];faces=[];nx=24;ny=12;d=1.25
for x in [cx-width/2,cx+width/2]:
 part('rear canopy post',(x,front+.65+d,1.63),(.022,.022,.90),steel)
 part('canopy side rail',(x,front+.65+d/2,2.49),(.022,d/2,.022),steel)
for i in range(nx+1):
 u=i/nx
 for j in range(ny+1):
  v=j/ny;vertices.append((cx-width/2+width*u,front+.65+d*v,2.47+.06*v-.14*math.sin(math.pi*u)*math.sin(math.pi*v)))
for i in range(nx):
 for j in range(ny):
  a=i*(ny+1)+j;faces.append((a,a+ny+1,a+ny+2,a+1))
mesh=bpy.data.meshes.new('Original235 blue canopy');mesh.from_pydata(vertices,[],faces);mesh.materials.append(material);uv=mesh.uv_layers.new()
for poly in mesh.polygons:
 poly.use_smooth=True
 for loop in poly.loop_indices:
  idx=mesh.loops[loop].vertex_index;uv.data[loop].uv=(idx//(ny+1)/nx,idx%(ny+1)/ny)
obj=bpy.data.objects.new('Original235 blue drape',mesh);bpy.context.collection.objects.link(obj);obj.parent=root;obj.matrix_world=Matrix.Identity(4);solid=obj.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.008
assert len(faces)==288
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for obj in root.children_recursive:obj.select_set(True)
root.location-=Vector((cx,cy,0));bpy.ops.export_scene.gltf(filepath=str(ASSET/'shop.glb'),export_format='GLB',use_selection=True);root.location+=Vector((cx,cy,0))
(ASSET/'model.json').write_text(json.dumps({'source_object':'market_se','map_position':[cx,0,-cy],'blender_source':str(OUT/'environment.blend'),'source_root':root.name,'tray_count':4,'cloth_quads':288,'removed':removed,'tactical_changes':False,'scope':'Original RGB cloth/tray interiors; unseen tray side/depth and frame inferred; inherited lower counter retained'},indent=2))
print('SOURCE_DISPLAY235_EXPORTED',cx,cy)
