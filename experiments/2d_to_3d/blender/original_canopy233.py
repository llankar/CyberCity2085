"""One original-derived sagging cloth canopy, retaining all tactical geometry."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase233';OUT.mkdir(exist_ok=True)
ASSET=LAB/'environment-library/assets/market_green_canopy'
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase232/environment.blend'))
root=bpy.data.objects['Occludable_market_nw']
body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
pts=[body.matrix_world@Vector(p) for p in body.bound_box]
lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
cx=(lo.x+hi.x)/2;cy=(lo.y+hi.y)/2
width=min(hi.x-lo.x-.3,5.5);depth=min(hi.y-lo.y-.3,3.4);front=cy-depth/2
removed=[]
for obj in list(root.children_recursive):
 if obj.name.startswith(('Kiosk207_ArmoredCap','Kiosk207_LuminousValance')) or (obj.name.startswith('Kiosk207_AuthoredServicePart') and obj.matrix_world.translation.z>2.5):
  removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
# Keep supports and shop contents; draped surface replaces the rigid repeated cap.
mat=bpy.data.materials.new('Original233 green cloth');mat.use_nodes=True
shader=mat.node_tree.nodes['Principled BSDF'];shader.inputs['Roughness'].default_value=.94
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ASSET/'source_cloth.png'))
mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
verts=[];faces=[];nx=32;ny=12;d=1.55
for i in range(nx+1):
 u=i/nx
 for j in range(ny+1):
  v=j/ny
  # Weighted cloth settles between edge rails; small uneven folds catch light.
  z=2.48+.09*v-.17*math.sin(math.pi*u)*math.sin(math.pi*v)+.017*math.sin(u*math.pi*9)*math.sin(math.pi*v)
  verts.append((cx-width/2+u*width,front+v*d,z))
for i in range(nx):
 for j in range(ny):
  a=i*(ny+1)+j;faces.append((a,a+ny+1,a+ny+2,a+1))
mesh=bpy.data.meshes.new('Original233 draped cloth');mesh.from_pydata(verts,[],faces);mesh.materials.append(mat)
uv=mesh.uv_layers.new()
for poly in mesh.polygons:
 poly.use_smooth=True
 for loop in poly.loop_indices:
  idx=mesh.loops[loop].vertex_index;uv.data[loop].uv=(idx//(ny+1)/nx,idx%(ny+1)/ny)
obj=bpy.data.objects.new('Original233 source-derived green canopy',mesh);bpy.context.collection.objects.link(obj);obj.parent=root;obj.matrix_world=Matrix.Identity(4)
solid=obj.modifiers.new('Real cloth thickness','SOLIDIFY');solid.thickness=.008
assert len(mesh.polygons)==384 and removed
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'canopy.json').write_text(json.dumps({'source_object':'market_nw','removed':removed,'cloth_quads':384,'dimensions':[width,d],'source_texture':str(ASSET/'source_cloth.png'),'geometry':'Draped surface with thickness; supports and lower machinery retained','tactical_changes':False,'limits':'Source RGB includes baked lighting; unseen depth and drape inferred; not whole-shop reconstruction'},indent=2))
print('CANOPY233_EXPORTED')
