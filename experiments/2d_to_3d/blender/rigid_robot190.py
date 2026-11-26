"""Rigid face ownership and joint housings for the painted mechanical trial."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/robot190';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/robot189/robot_actions.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');body=next(o for o in bpy.data.objects if o.type=='MESH')
group_names=[g.name for g in body.vertex_groups]
old=body.data;verts=[];faces=[];uvs=[];owners=[];materials=[]
for poly in old.polygons:
 scores={}
 for vi in poly.vertices:
  for g in old.vertices[vi].groups:scores[g.group]=scores.get(g.group,0)+g.weight
 owner=max(scores,key=scores.get)
 start=len(verts)
 for li in poly.loop_indices:
  verts.append(old.vertices[old.loops[li].vertex_index].co.copy());uvs.append(old.uv_layers.active.data[li].uv.copy())
 faces.append(tuple(range(start,len(verts))));owners.append(owner);materials.append(poly.material_index)
mesh=bpy.data.meshes.new('RigidPlates190');mesh.from_pydata(verts,[],faces);mesh.update()
for mat in old.materials:mesh.materials.append(mat)
layer=mesh.uv_layers.new(name='UVMap')
for i,uv in enumerate(uvs):layer.data[i].uv=uv
body.data=mesh
for name in group_names:body.vertex_groups.new(name=name)
for poly,owner,mat in zip(mesh.polygons,owners,materials):
 poly.material_index=mat;body.vertex_groups[owner].add(list(poly.vertices),1,'REPLACE')
# A circular mechanical housing covers the intentionally separated hinge seam.
metal=bpy.data.materials.new('Joint housings190');metal.diffuse_color=(.045,.055,.065,1);metal.use_nodes=True
shader=metal.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.045,.055,.065,1);shader.inputs['Metallic'].default_value=.65;shader.inputs['Roughness'].default_value=.5
for side in ['L','R']:
 for stem,radius in [('forearm',.10),('shin',.12)]:
  name=stem+'.'+side;point=rig.data.bones[name].head_local
  bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=.15,location=point,rotation=(0,math.pi/2,0))
  obj=bpy.context.object;obj.name='MechanicalHinge190_'+name
  bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  obj.data.materials.append(metal);obj.vertex_groups.new(name=name).add(list(range(len(obj.data.vertices))),1,'REPLACE')
  obj.parent=rig;mod=obj.modifiers.new('Rigid hinge','ARMATURE');mod.object=rig
for p in rig.pose.bones:p.rotation_euler=(0,0,0);p.location=(0,0,0)
bpy.context.scene.frame_set(1);bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'robot_actions.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'robot_actions.glb'),export_format='GLB',use_selection=True,export_animation_mode='ACTIONS',export_force_sampling=True)
(OUT/'segmentation.json').write_text(json.dumps({'rigid_faces':len(faces),'hinges':4,'scope':'face ownership, same189rig/actions; seam and motion review required'},indent=2))
print('ROBOT190_READY',len(faces),flush=True)
