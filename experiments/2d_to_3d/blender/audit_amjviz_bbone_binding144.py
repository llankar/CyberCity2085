"""Assess an actual segmented-bone bake without changing the source mesh or rig."""
import json
from pathlib import Path
import bpy
from mathutils import Matrix

root=Path('E:/CyberCity2085-3d-lab')
bpy.ops.wm.open_mainfile(filepath=str(root/'sources/blenderkit_cyberpunk143/source.blend'),use_scripts=False)
rig=bpy.data.objects['rig'];body=bpy.data.objects['Character']
for track in rig.animation_data.nla_tracks:track.mute=True
rig.animation_data.action=None
for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
evaluated=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
counts=[];lost=[];weighted=set()
for vertex in body.data.vertices:
    weights={}
    point=rig.matrix_world.inverted()@body.matrix_world@vertex.co
    for group in vertex.groups:
        if group.weight<=0:continue
        name=body.vertex_groups[group.group].name
        if name not in rig.data.bones or not rig.data.bones[name].use_deform:continue
        weighted.add(name);bone=rig.data.bones[name]
        if bone.bbone_segments<=1:weights[(name,0)]=group.weight;continue
        index,blend=evaluated.pose.bones[name].bbone_segment_index(bone.matrix_local.inverted()@point)
        for key,fraction in [((name,index),1-blend),((name,index+1),blend)]:
            if fraction>0:weights[key]=weights.get(key,0)+group.weight*fraction
    assert abs(sum(weights.values())-1)<1e-5
    ordered=sorted(weights.values(),reverse=True);counts.append(len(ordered));lost.append(sum(ordered[8:]))
report={'vertices':len(counts),'weighted_source_bones':len(weighted),
        'expanded_segment_joints':sum(rig.data.bones[n].bbone_segments+1 if rig.data.bones[n].bbone_segments>1 else 1 for n in weighted),
        'maximum_expanded_vertex_influences':max(counts),'vertices_over_eight':sum(c>8 for c in counts),
        'maximum_weight_mass_beyond_eight':max(lost),
        'segment_api_documentation':evaluated.pose.bones[0].bbone_segment_index.__doc__,
        'scope':'Rest-space split-weight feasibility only; no baked mesh, pose or artistic acceptance'}
out=root/'generated/phase2/amjviz_runtime144/bbone_binding_audit.json'
out.write_text(json.dumps(report,indent=2));print('AMJVIZ_SEGMENT_BINDING_AUDIT',json.dumps(report),flush=True)
