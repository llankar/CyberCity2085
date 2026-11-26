"""Recover the three original cloth colors/proportions and export a reusable shop."""
from pathlib import Path
import bpy,math,json,sys
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase234';OUT.mkdir(exist_ok=True)
ASSET=LAB/'environment-library/assets/market_three_canopies';ASSET.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase233/environment.blend'))
root=bpy.data.objects['Occludable_market_nw']
body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
pts=[body.matrix_world@Vector(p) for p in body.bound_box]
lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
cx=(lo.x+hi.x)/2;cy=(lo.y+hi.y)/2;width=min(hi.x-lo.x-.3,5.5);depth=min(hi.y-lo.y-.3,1.8)
for obj in list(root.children_recursive):
 if obj.name.startswith('Original233 '):bpy.data.objects.remove(obj,do_unlink=True)
frame=bpy.data.materials['Kiosk207_WeatheredSteel'];count=0
# Relative source composition: two green covers at left, plum cloth at right.
patches=[('sage',.02,.57,.34,.94),('plum',.61,.98,.22,.98),('green',.02,.57,.02,.28)]
for name,u0,u1,v0,v1 in patches:
 mat=bpy.data.materials.new('Original234 '+name+' canvas');mat.use_nodes=True
 shader=mat.node_tree.nodes['Principled BSDF'];shader.inputs['Roughness'].default_value=.97
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ASSET/(name+'.png')))
 mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
 x0=cx-width/2+u0*width;y0=cy-depth/2+v0*depth;w=(u1-u0)*width;d=(v1-v0)*depth
 nx=20;ny=10;vertices=[];faces=[]
 for i in range(nx+1):
  u=i/nx
  for j in range(ny+1):
   v=j/ny;z=2.49+.05*v-.13*math.sin(math.pi*u)*math.sin(math.pi*v)+.012*math.sin(u*math.pi*7)*math.sin(math.pi*v)
   vertices.append((x0+w*u,y0+d*v,z))
 for i in range(nx):
  for j in range(ny):
   a=i*(ny+1)+j;faces.append((a,a+ny+1,a+ny+2,a+1))
 mesh=bpy.data.meshes.new('Original234 '+name);mesh.from_pydata(vertices,[],faces);mesh.materials.append(mat);uv=mesh.uv_layers.new()
 for poly in mesh.polygons:
  poly.use_smooth=True
  for loop in poly.loop_indices:
   idx=mesh.loops[loop].vertex_index;uv.data[loop].uv=(idx//(ny+1)/nx,idx%(ny+1)/ny)
 obj=bpy.data.objects.new('Original234 '+name+' drape',mesh);bpy.context.collection.objects.link(obj);obj.parent=root;obj.matrix_world=Matrix.Identity(4)
 solid=obj.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.008;count+=len(faces)
 for x in [x0,x0+w]:
  for y in [y0,y0+d]:
   obj=box('Original234 canopy corner post',(x,y,1.61),(.018,.018,.87),frame,.004);world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world
assert count==600
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
# Standalone shop, ground anchor; export actual complete root, no floor or neighbors.
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for obj in root.children_recursive:obj.select_set(True)
root.location-=Vector((cx,cy,0))
bpy.ops.export_scene.gltf(filepath=str(ASSET/'shop.glb'),export_format='GLB',use_selection=True)
root.location+=Vector((cx,cy,0))
(ASSET/'model.json').write_text(json.dumps({'source_object':'market_nw','anchor':'bottom_center','map_position':[cx,0,-cy],'blender_source':str(OUT/'environment.blend'),'source_root':root.name,'cloth_quads':count,'patches':patches,'scope':'Original cloth RGB/layout; inherited acquired machinery and interpreted counter/supports; one true view; no tactical mutation'},indent=2))
print('THREE_CANOPIES234_EXPORTED',cx,cy,count)
