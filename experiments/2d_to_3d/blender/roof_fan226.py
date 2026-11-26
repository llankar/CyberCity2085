"""Original-map twin roof extractor: physical housing, recesses, fans and fixings."""
from pathlib import Path
import bpy,math,json,sys
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from create_hardsurface_crate import box,make_material
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'environment-library/assets/roof_twin_fan'
source=json.loads((OUT/'source.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
metal=make_material('Worn charcoal painted housing',(.045,.055,.065,1),.55,.7)
black=make_material('Dark recessed machinery',(.008,.011,.014,1),.35,.7)
rim=make_material('Exposed fan edges',(.11,.13,.14,1),.65,.55)
shader=metal.node_tree.nodes['Principled BSDF']
for filename,socket in [('rough.jpg','Roughness'),('nor_gl.jpg','Normal')]:
 image=bpy.data.images.load(str(LAB/'sources/environment169/blue_metal_plate'/filename));image.colorspace_settings.name='Non-Color'
 tex=metal.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image
 if socket=='Normal':
  normal=metal.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.35
  metal.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);metal.node_tree.links.new(normal.outputs['Normal'],shader.inputs[socket])
 else:metal.node_tree.links.new(tex.outputs['Color'],shader.inputs[socket])
parts=[box('Folded weatherproof housing',(0,0,.16),(.65,.55,.14),metal,.025)]
for x in [-.63,.63]:parts.append(box('Raised side frame',(x,0,.31),(.025,.54,.035),rim,.008))
for y in [-.53,.53]:parts.append(box('Raised end frame',(0,y,.31),(.63,.025,.035),rim,.008))
def cylinder(name,location,radius,depth,material,vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=location)
 obj=bpy.context.object;obj.name=name;obj.data.materials.append(material);parts.append(obj)
 return obj
for x in [-.31,.31]:
 cylinder('Recess beneath fan',(x,0,.305),.265,.012,black)
 bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=8,location=(x,0,.34),major_radius=.252,minor_radius=.018)
 ring=bpy.context.object;ring.name='Rolled fan surround';ring.data.materials.append(rim);parts.append(ring)
 cylinder('Fan motor',(x,0,.345),.065,.08,rim)
 for i in range(7):
  angle=i*math.tau/7
  # Swept, pitched blades are real 3D mesh surfaces inside the recessed housing.
  points=[]
  for radius,offset,z in [(.06,-.2,.34),(.23,-.12,.33),(.22,.22,.36),(.07,.3,.37)]:
   points.append((x+radius*math.cos(angle+offset),radius*math.sin(angle+offset),z))
  mesh=bpy.data.meshes.new('Swept blade');mesh.from_pydata(points,[],[(0,1,2,3)])
  obj=bpy.data.objects.new('Extractor blade',mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(metal)
  solid=obj.modifiers.new('Blade thickness','SOLIDIFY');solid.thickness=.008;parts.append(obj)
 for y in [-.4,.4]:cylinder('Frame fastener',(x,y,.32),.018,.015,rim,6)
for i in range(7):parts.append(box('Side inlet louvre',(-.43+i*.14,-.554,.15),(.045,.009,.07),black,.003))
for x in [-.5,.5]:
 for y in [-.4,.4]:parts.append(box('Roof mounting foot',(x,y,.02),(.065,.065,.02),black,.005))
for o in bpy.context.scene.objects:o.select_set(o in parts)
bpy.ops.file.pack_all()
bpy.ops.export_scene.gltf(filepath=str(OUT/'optimized.glb'),export_format='GLB',use_selection=True,export_apply=True)
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Neutral226');scene.world.color=(.2,.2,.2)
for position,energy in [((2,-3,4),500),((-2,2,3),350)]:
 bpy.ops.object.light_add(type='AREA',location=position);lamp=bpy.context.object;lamp.data.energy=energy;lamp.data.size=4
 lamp.rotation_euler=(Vector((0,0,.2))-lamp.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2,-3,2.7));scene.camera=bpy.context.object
scene.camera.rotation_euler=(Vector((0,0,.2))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=2.5
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.filepath=str(OUT/'neutral.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'source.blend'))
source.update(models={'blend':str(OUT/'source.blend'),'glb':str(OUT/'optimized.glb')},dimensions=[1.3,1.1,.39],anchor='bottom_center',artistic_status='BLENDER_REVIEW_PENDING_GODOT',method='Blender reconstruction from one genuine roof reference; hidden sides and mechanical details inferred, not recovered multi-view')
(OUT/'source.json').write_text(json.dumps(source,indent=2))
catalog=LAB/'environment-library/library.json'
data=json.loads(catalog.read_text(encoding='utf8'))
data['assets']=[source if a['id']==source['id'] else a for a in data['assets']]
catalog.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
print('ROOF_FAN226_EXPORTED',len(parts))
