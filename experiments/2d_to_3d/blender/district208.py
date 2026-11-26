"""Industrial facade finishes and actual illustrated advertising, same map."""
from pathlib import Path
import bpy,json
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase208';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase207/environment.blend'))
steel=bpy.data.materials['Kiosk207_WeatheredSteel']
changed=[];ads=[]
image=bpy.data.images.load(str(LAB/'generated/phase2/showcase207/medical_hologram.png'))
mat=bpy.data.materials.new('District208 clinic advertising');mat.use_nodes=True
shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.45
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image
for socket in ['Base Color','Emission Color']:mat.node_tree.links.new(tex.outputs['Color'],shader.inputs[socket])
shader.inputs['Emission Strength'].default_value=.65
for name in ['north_building','south_building_w','east_building']:
 root=bpy.data.objects['Occludable_'+name]
 body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
 assert len(body.data.materials)>1,name
 body.data=body.data.copy()
 # Derive wall slots from actual world normals: slot1 is the roof in this mesh.
 normal_matrix=body.matrix_world.to_3x3().inverted().transposed()
 slots={poly.material_index for poly in body.data.polygons if abs((normal_matrix@poly.normal).normalized().z)<.2}
 assert slots,name
 for slot in slots:body.data.materials[slot]=steel
 changed.append(name)
 windows=[o for o in root.children_recursive if o.type=='MESH' and o.name.startswith(('Facade206 urban window','AuthoredFacade_window'))]
 if not windows:continue
 # Use the existing fitted window frame; put a screen just ahead of its glazing.
 window=windows[len(windows)//2]
 points=[window.matrix_world@Vector(p) for p in window.bound_box]
 center=sum(points,Vector())/8
 normal=window.matrix_world.to_3x3().inverted().transposed()@max(window.data.polygons,key=lambda p:p.area).normal
 normal.z=0;normal.normalize()
 bp=[body.matrix_world@Vector(p) for p in body.bound_box];bc=sum(bp,Vector())/8
 if normal.dot(center-bc)<0:normal=-normal
 right=Vector((normal.y,-normal.x,0));center+=normal*.25
 mesh=bpy.data.meshes.new('District208 medical advertising')
 mesh.from_pydata([center+right*x+Vector((0,0,z)) for x,z in [(-.55,-1),(.55,-1),(.55,1),(-.55,1)]],[],[(0,1,2,3)])
 uv=mesh.uv_layers.new()
 for i,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=p
 mesh.materials.append(mat)
 obj=bpy.data.objects.new('District208 illuminated clinic advertisement',mesh);bpy.context.collection.objects.link(obj)
 obj.parent=root
 # Vertices were constructed in world space, so cancel inherited root transform.
 obj.matrix_world=Matrix.Identity(4)
 ads.append(name)
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'district.json').write_text(json.dumps({'metal_cladding':changed,'medical_advertising':ads,'scope':'cosmetic finish of existing map; no tactical or production change'},indent=2))
print('DISTRICT208_READY',changed,ads,flush=True)
