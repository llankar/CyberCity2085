"""Soften the coat/arm weight boundary, retaining geometry and authored clips."""
from pathlib import Path
import json
import bpy

ROOT=Path('E:/CyberCity2085-3d-lab/generated/phase2')
OUT=ROOT/'rig177';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'rig176/human.blend'),use_scripts=False)
rig=bpy.data.objects['UnarmedRook175']
body=next(obj for obj in bpy.context.scene.objects if obj.type=='MESH' and
          not obj.name.startswith('EquippedNeuralPistol_') and
          any(mod.type=='ARMATURE' and mod.object==rig for mod in obj.modifiers))
neighbors=[set() for vertex in body.data.vertices]
for edge in body.data.edges:
    a,b=edge.vertices;neighbors[a].add(b);neighbors[b].add(a)
region=[vertex.index for vertex in body.data.vertices if .15<abs(vertex.co.x)<.40 and .95<vertex.co.z<1.48]
weights=[{item.group:item.weight for item in vertex.groups if item.weight>0} for vertex in body.data.vertices]
for iteration in range(5):
    updated={}
    for index in region:
        adjacent=neighbors[index]
        if not adjacent:continue
        average={}
        for other in adjacent:
            for group,value in weights[other].items():average[group]=average.get(group,0)+value/len(adjacent)
        mixed={group:.5*weights[index].get(group,0)+.5*average.get(group,0) for group in weights[index].keys()|average.keys()}
        kept=sorted(mixed.items(),key=lambda pair:pair[1],reverse=True)[:4]
        total=sum(value for group,value in kept)
        updated[index]={group:value/total for group,value in kept}
    for index,value in updated.items():weights[index]=value
for index in region:
    for group in [item.group for item in body.data.vertices[index].groups]:body.vertex_groups[group].remove([index])
    for group,value in weights[index].items():body.vertex_groups[group].add([index],value,'REPLACE')
assert all(vertex.groups for vertex in body.data.vertices)
assert all(abs(sum(item.weight for item in body.data.vertices[index].groups)-1)<1e-4 for index in region)
selection=[obj for obj in bpy.context.scene.objects if obj==rig or
           (obj.type=='MESH' and any(mod.type=='ARMATURE' and mod.object==rig for mod in obj.modifiers))]
for obj in bpy.context.scene.objects:obj.select_set(obj in selection)
bpy.context.view_layer.objects.active=rig
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'human.glb'),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False)
report=json.loads((ROOT/'rig176/binding.json').read_text());report['regional_smoothed_vertices']=len(region)
report['scope']='Regional weight continuity trial; identical geometry, material and animation; artistic comparison required'
(OUT/'binding.json').write_text(json.dumps(report,indent=2))
print('NEURAL177_WEIGHT_BOUNDARY_SMOOTHED',len(region),flush=True)
