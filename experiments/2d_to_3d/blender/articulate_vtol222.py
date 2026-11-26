"""Inspect retained generated aircraft from above before fan articulation."""
from pathlib import Path
import bpy
import bmesh
import math
import json
from mathutils import Matrix
from mathutils import Vector
LAB=Path('E:/CyberCity2085-3d-lab')
OUT=LAB/'generated/phase2/vtol222'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/paint220/stealth_vtol/review/model.blend'))
scene=bpy.context.scene
scene.camera.location=(0,0,3)
scene.camera.rotation_euler=(0,0,0)
scene.camera.data.ortho_scale=1.2
scene.render.filepath=str(OUT/'top.png')
bpy.ops.render.render(write_still=True)
for obj in scene.objects:
 if obj.type=='MESH':
  points=[obj.matrix_world@v.co for v in obj.data.vertices]
  print('AIRCRAFT222_BOUNDS',obj.name,[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)])
body=next(o for o in scene.objects if o.type=='MESH')
body.data.transform(body.matrix_world)
body.parent=None;body.matrix_world=Matrix.Identity(4)
parts=[body];records=[]
for side,y in [('port',.329),('starboard',-.329)]:
 center=Vector((.155,y,0))
 selected={p.index for p in body.data.polygons if (p.center.x-center.x)**2+(p.center.y-center.y)**2<.095**2}
 # Copy actual triangles and their UV/material data. No replacement primitives.
 mesh=body.data.copy();bm=bmesh.new();bm.from_mesh(mesh)
 bm.faces.ensure_lookup_table()
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index not in selected],context='FACES')
 bm.to_mesh(mesh);bm.free()
 rotor=bpy.data.objects.new('GeneratedFan_'+side,mesh);bpy.context.collection.objects.link(rotor)
 pivot=bpy.data.objects.new('FanPivot_'+side,None);bpy.context.collection.objects.link(pivot)
 pivot.location=center;rotor.parent=pivot;rotor.matrix_parent_inverse=pivot.matrix_world.inverted()
 # Parent matrix is set explicitly because depsgraph evaluation is deferred.
 rotor.matrix_basis=Matrix.Translation(-center)
 bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table()
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index in selected],context='FACES')
 bm.to_mesh(body.data);bm.free()
 for frame,angle in [(0,0),(15,2*math.pi)]:
  pivot.rotation_euler.z=angle;pivot.keyframe_insert(data_path='rotation_euler',frame=frame)
 action=pivot.animation_data.action;action.name='Fan222_'+side
 for curve in action.fcurves:
  for key in curve.keyframe_points:key.interpolation='LINEAR'
 track=pivot.animation_data.nla_tracks.new();track.name='Rotor_Spin'
 track.strips.new('Rotor_Spin',0,action);pivot.animation_data.action=None
 parts.extend([rotor,pivot]);records.append({'side':side,'center':list(center),'faces':len(mesh.polygons)})
for material in body.data.materials:
 if material and material.use_nodes:
  shader=material.node_tree.nodes.get('Principled BSDF')
  shader.inputs['Metallic'].default_value=.4
  shader.inputs['Roughness'].default_value=.55
scene.render.fps=30
scene.frame_set(0)
for obj in scene.objects:obj.select_set(obj in parts)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'vtol_actions.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'vtol_actions.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True)
scene.frame_set(4)
scene.render.filepath=str(OUT/'top_rotated.png');bpy.ops.render.render(write_still=True)
(OUT/'articulation.json').write_text(json.dumps({'fans':records,'scope':'Actual generated inner-fan triangles separated radially; cut-edge visual review required. No gear transfer.'},indent=2))
