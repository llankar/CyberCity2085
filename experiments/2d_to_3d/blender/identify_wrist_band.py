"""Identify retained-body versus glove pixels without changing anatomy."""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

root=Path('E:/CyberCity2085-3d-lab/generated/phase2');out=root/'rook_wrist132'
whole='--whole-owner' in sys.argv
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_run129/human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
for t in rig.animation_data.nla_tracks:t.mute=t.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
body=bpy.data.objects['char1'];graph=bpy.context.evaluated_depsgraph_get()
ev=body.evaluated_get(graph);mesh=ev.to_mesh()
points=[ev.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear()
wrist=rig.matrix_world@rig.pose.bones['RightHand'].matrix.translation
axis=(rig.matrix_world@rig.pose.bones['RightForeArm'].matrix.translation-wrist).normalized()
groups={g.index for g in body.vertex_groups if g.name in ('RightForeArm','RightHand')}
weight=[sum(g.weight for g in v.groups if g.group in groups) for v in body.data.vertices]
mat=bpy.data.materials.new('BODY_OWNERSHIP_DIAGNOSTIC');mat.use_nodes=True
tree=mat.node_tree;emission=tree.nodes.new('ShaderNodeEmission');emission.inputs['Color'].default_value=(1,0,1,1)
tree.links.new(emission.outputs[0],tree.nodes['Material Output'].inputs['Surface']);body.data.materials.append(mat)
selected=[]
for face in body.data.polygons:
    center=sum((points[i] for i in face.vertices),Vector())/len(face.vertices)
    if whole or (all(weight[i]>.5 for i in face.vertices) and (center-wrist).length<.09 and -.04<(center-wrist).dot(axis)<.03):
        face.material_index=len(body.data.materials)-1;selected.append(face.index)
if whole:
    glove=bpy.data.objects['AuthoredGlove_Game_body']
    cyan=mat.copy();cyan.name='GLOVE_OWNERSHIP_DIAGNOSTIC'
    next(n for n in cyan.node_tree.nodes if n.type=='EMISSION').inputs['Color'].default_value=(0,1,1,1)
    glove.data.materials.clear();glove.data.materials.append(cyan)
    for face in glove.data.polygons:face.material_index=0
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
name='mesh_owner_all' if whole else 'mesh_owner'
bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True)
(out/(name+'.json')).write_text(json.dumps({'whole_body_magenta_glove_cyan':whole,'marked_body_faces':selected,'scope':'Mesh ownership diagnostic only; no final material or contact proof'},indent=2))
print('WRIST_BODY_OWNERSHIP_DIAGNOSTIC',len(selected),flush=True)
