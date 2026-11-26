"""Replace flat lab instrumentation with modular screens, specimens and wall services."""
from pathlib import Path
import bpy,sys,math,json
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box,make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/lab248'
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/lab247/environment.blend'))
bpy.context.preferences.filepaths.save_version=0
steel=bpy.data.materials['Lab brushed steel'];dark=bpy.data.materials['Lab recessed service panels'];cyan=bpy.data.materials['Lab cyan instrumentation']
ceramic=bpy.data.materials['Lab clinical ceramic'];ceramic.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.13,.20,.24,1)
glass=bpy.data.materials['Lab containment blue glass'];added=[]
nodes=steel.node_tree.nodes;links=steel.node_tree.links;shader=nodes.get('Principled BSDF')
coords=nodes.new('ShaderNodeTexCoord')
for filename,socket in [('diff.jpg','Base Color'),('rough.jpg','Roughness'),('nor_gl.jpg','Normal')]:
 tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(LAB/'sources/environment169/blue_metal_plate'/filename))
 tex.projection='BOX';tex.projection_blend=.15;links.new(coords.outputs['Generated'],tex.inputs['Vector'])
 if socket=='Normal':
  tex.image.colorspace_settings.name='Non-Color';normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.3;links.new(tex.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],shader.inputs['Normal'])
 else:
  if socket=='Roughness':tex.image.colorspace_settings.name='Non-Color'
  links.new(tex.outputs['Color'],shader.inputs[socket])
def part(name,p,size,material,parent):
 o=box('Detail248 '+name,p,size,material,.015);o.parent=parent;added.append(o);return o
screen=make_material('Scientific display source colour',(.02,.2,.3,1),.3,.3)
nodes=screen.node_tree.nodes;shader=nodes.get('Principled BSDF');tex=nodes.new('ShaderNodeTexImage')
tex.image=bpy.data.images.load(str(LAB/'environment-library/references/city_interior_research_lab__north_console_e.png'))
screen.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
screen.node_tree.links.new(tex.outputs['Color'],shader.inputs['Emission Color']);shader.inputs['Emission Strength'].default_value=.5
for root in [o for o in bpy.data.objects if o.name.startswith('Occludable_')]:
 worktop=next((o for o in root.children_recursive if o.name.endswith('source worktop')),None)
 if worktop is None:continue
 identifier=root.name.removeprefix('Occludable_')
 # Retain the illustrated instrument detail; the separate raised displays and
 # specimens add real volume without replacing rich source art by blank steel.
 if 'crate' in identifier or 'rack' in identifier:continue
 x,y,z=worktop.location;w=worktop.scale.x*2;d=worktop.scale.y*2
 if 'greenhouse' in identifier:
  for j in range(4):
   part('sample tray divider',(x-w*.3+j*w*.2,y,z+.08),(.012,d*.37,.025),steel,root)
  continue
 # Displays are separate angled 3D assemblies, not the full overhead desk art.
 for side in [-1,1] if w>3 else [0]:
  px=x+side*w*.26;py=y+d*.22
  part('display foot',(px,py,z+.07),(.25,.15,.05),dark,root)
  part('display neck',(px,py,z+.32),(.035,.035,.25),steel,root)
  frame=part('display casing',(px,py,z+.63),(.43,.055,.27),dark,root);frame.rotation_euler.x=math.radians(15)
  bpy.ops.mesh.primitive_plane_add(size=2,location=(px,py-.062,z+.63));o=bpy.context.object;o.name='Detail248 source display';o.scale=(.39,.23,1);o.rotation_euler=(math.radians(75),0,0);o.data.materials.append(screen);o.parent=root;added.append(o)
  part('keyboard',(px,py-.42,z+.045),(.31,.13,.025),dark,root)
  part('keyboard backlight',(px,py-.43,z+.073),(.26,.08,.007),cyan,root)
 for j in range(3):
  px=x-w*.28+j*.2;py=y-d*.2
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.065,depth=.24,location=(px,py,z+.15));o=bpy.context.object;o.name='Detail248 sample vial';o.data.materials.append(glass);o.parent=root;added.append(o)
  part('specimen cap',(px,py,z+.28),(.065,.065,.025),steel,root)
# Add restrained service strips to the plain clinical partitions.
for o in list(bpy.data.objects):
 if 'partition' not in o.name or o.type!='MESH':continue
 center=o.location;size=o.dimensions
 if size.z<1:continue
 length=max(size.x,size.y)
 # Local dimensions preserve rotated segments; details share their parent.
 local=o.data.vertices
 extent=max(v.co.x for v in local)-min(v.co.x for v in local)
 for offset in [-.14,.14]:
  trim=part('partition conduit',(center.x,center.y,.35),(max(.05,extent/2-.05),.035,.065),dark,o.parent)
  trim.rotation_euler.z=o.rotation_euler.z
  trim.location.x-=math.sin(o.rotation_euler.z)*offset;trim.location.y+=math.cos(o.rotation_euler.z)*offset
floor=bpy.data.materials['Original laboratory floor']
next(n for n in floor.node_tree.nodes if n.type=='TEX_IMAGE').image=bpy.data.images.load(str(OUT/'floor.png'))
scene=bpy.context.scene;scene.camera.data.ortho_scale=49
scene.render.filepath=str(OUT/'overview.png');bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
for o in scene.objects:o.select_set(o.type=='MESH' or o.name.startswith('Occludable_'))
bpy.context.view_layer.objects.active=next(o for o in scene.objects if o.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.render.render(write_still=True)
print('LAB248_DETAIL_EXPORTED',len(added),'new meshes; first art pass, not final')
