"""Restore source-derived dark segmented roof identities on two existing buildings."""
from pathlib import Path
import bpy,sys,math,json
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box,make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/showcase229';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase219/environment.blend'))
dark=make_material('Original229 dark roof panels',(.025,.034,.045,1),.4,.72)
trim=make_material('Original229 weathered roof reinforcement',(.065,.075,.09,1),.55,.68)
shader=dark.node_tree.nodes['Principled BSDF']
for name,socket in [('rough.jpg','Roughness'),('nor_gl.jpg','Normal')]:
 tex=dark.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(LAB/'sources/environment169/blue_metal_plate'/name));tex.image.colorspace_settings.name='Non-Color'
 if socket=='Normal':
  normal=dark.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.3
  dark.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);dark.node_tree.links.new(normal.outputs['Normal'],shader.inputs[socket])
 else:dark.node_tree.links.new(tex.outputs['Color'],shader.inputs[socket])
records=[]
for name in ['south_building_w','south_building_e']:
 root=bpy.data.objects['Occludable_'+name]
 removed=[]
 for old in list(root.children_recursive):
  if old.name.startswith('Roof199'):
   removed.append(old.name);bpy.data.objects.remove(old,do_unlink=True)
 body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
 points=[body.matrix_world@Vector(p) for p in body.bound_box]
 lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
 def part(label,location,half,material):
  obj=box('Original229 '+label,location,half,material,.008)
  world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world
  return obj
 width=hi.x-lo.x-.2;depth=hi.y-lo.y-.2
 nx=max(2,round(width/.85));ny=max(2,round(depth/.8))
 for x in range(nx):
  for y in range(ny):
   px=lo.x+.1+(x+.5)*width/nx;py=lo.y+.1+(y+.5)*depth/ny
   part('segmented roof plate',(px,py,hi.z+.022),(width/nx/2-.012,depth/ny/2-.012,.02),dark)
 for x in [lo.x+.08,hi.x-.08]:part('long roof perimeter',(x,(lo.y+hi.y)/2,hi.z+.045),(.035,depth/2,.035),trim)
 for y in [lo.y+.08,hi.y-.08]:part('short roof perimeter',((lo.x+hi.x)/2,y,hi.z+.045),(width/2,.035,.035),trim)
 if name=='south_building_w':
  # Center derived from the genuine hatch in the stored original context crop.
  cx=-8.6146;cy=-12.2176;z=hi.z+.075
  part('square service hatch',(cx,cy,z),(.53,.49,.025),trim)
  part('recessed hatch lid',(cx,cy,z+.03),(.48,.44,.012),dark)
  for angle in [-math.pi/4,math.pi/4]:
   beam=part('hatch diagonal brace',(cx,cy,z+.055),(.53,.018,.014),trim);beam.rotation_euler.z=angle
 records.append({'building':name,'removed_invented_roof_parts':removed,'panel_grid':[nx,ny],'source_context':'environment-library/references/city_exterior_neon_market_alley__'+name+'.png'})
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'roofs.json').write_text(json.dumps({'roofs':records,'scope':'Source-derived segmented roofs; hidden structural details inferred; no collision edits'},indent=2))
print('ORIGINAL229_ROOFS_EXPORTED',len(records))
