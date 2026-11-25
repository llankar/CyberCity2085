"""Neutral clay skin diagnostic: isolate texture artifacts from actual neck geometry."""
import json
from pathlib import Path
import bpy
import bmesh

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'rook_neck_diagnostic138';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_undercut133/human.blend'),use_scripts=False)
scene=bpy.context.scene
head=bpy.data.objects['MIT_HeadFitStudy'];body=bpy.data.objects['char1']
skin=head.data.materials[0]
selected=[p for p in body.data.polygons if body.data.materials[p.material_index]==skin]
assert len(selected)==196
points=[body.matrix_world@body.data.vertices[i].co for p in selected for i in p.vertices]
report={'skin_faces':len(selected),'smooth_skin_faces':sum(p.use_smooth for p in selected),
        'head_faces':len(head.data.polygons),'smooth_head_faces':sum(p.use_smooth for p in head.data.polygons),
        'skin_rest_bounds':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)],
        'scope':'Diagnostic neutral skin only, no candidate art and no geometry changes'}
head_points=[head.matrix_world@v.co for v in head.data.vertices]
report['head_rest_bounds']=[[min(p[i] for p in head_points),max(p[i] for p in head_points)] for i in range(3)]
tree=skin.node_tree;tree.nodes.clear()
shader=tree.nodes.new('ShaderNodeBsdfPrincipled');shader.inputs['Base Color'].default_value=(.4,.4,.4,1)
shader.inputs['Roughness'].default_value=.7
output=tree.nodes.new('ShaderNodeOutputMaterial');tree.links.new(shader.outputs[0],output.inputs['Surface'])
rig=next(o for o in scene.objects if o.type=='ARMATURE')
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
helpers={bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,
    export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,
    export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True)
bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[p.index] for p in selected],context='FACES')
bm.to_mesh(body.data);bm.free()
bpy.ops.export_scene.gltf(filepath=str(out/'without_body_skin.glb'),export_format='GLB',use_selection=True,
    export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,
    export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True)
report['additional_diagnostic']='without_body_skin removes196retained body skin faces for ownership comparison only; not an accepted topology change'
(out/'diagnostic.json').write_text(json.dumps(report,indent=2))
print('ROOK_NECK_CLAY_DIAGNOSTIC',json.dumps(report),flush=True)
