"""Integrate the authored head/hair with its real weights on the shared game rig."""
import json
import sys
import shutil
from pathlib import Path
import bpy
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb

base=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=base/'rocketbox_military03/motion01'
out=base/'rocketbox_hair08/character01'; out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human_motion.blend'),use_scripts=False)
rig=bpy.data.objects['Bip01']
body=next(obj for obj in bpy.context.scene.objects if obj.type=='MESH')
with bpy.data.libraries.load(str(base/'rocketbox_hair08/fitted_head_hair.blend'),link=False) as (available,loaded):
    loaded.objects=['AuthoredHeadHair']
head=loaded.objects[0]; bpy.context.scene.collection.objects.link(head)
head.parent=rig; head.matrix_world=Matrix.Identity(4)
modifier=head.modifiers.new('AuthoredHeadWeights','ARMATURE'); modifier.object=rig
problems=[{'vertex':v.index,'sum':sum(g.weight for g in v.groups),'groups':[(head.vertex_groups[g.group].name,g.weight) for g in v.groups]} for v in head.data.vertices if not v.groups or abs(sum(g.weight for g in v.groups)-1)>=1e-4]
print('HEAD_WEIGHT_DIAGNOSTIC',len(problems),problems[:8],flush=True)
for vertex in head.data.vertices:
    positive=[group for group in vertex.groups if group.weight>0]
    assert positive and abs(sum(group.weight for group in positive)-1)<1e-4
    assert all(head.vertex_groups[group.group].name in rig.data.bones for group in positive)
for material in body.data.materials:
    if material.name in {'sm004_head','sm004_helmet'}:
        shader=next(node for node in material.node_tree.nodes if node.type=='BSDF_PRINCIPLED')
        shader.inputs['Alpha'].default_value=0
        material.surface_render_method='DITHERED'
for obj in bpy.context.scene.objects: obj.select_set(obj in [rig,body,head])
bpy.context.view_layer.objects.active=rig
for track in rig.animation_data.nla_tracks: track.mute=False
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='NLA_TRACKS',export_frame_range=False,
    export_force_sampling=True,export_try_sparse_sk=True,
    export_copyright='Microsoft Rocketbox MIT; Quaternius UAL CC0')
glb=Glb(out/'human.glb')
for material in glb.doc['materials']:
    if material.get('name')=='m014_opacity':
        material['alphaMode']='MASK'; material['alphaCutoff']=.4; material['doubleSided']=True
glb.doc['asset'].setdefault('extras',{}).update({'source_assets':['Military_Male_03','Male_Adult_08'],
    'source_commit':'0943055db6ec570bcef9f2c8b41c9e5467c808f9','source_license':'MIT',
    'license_notice':(source.parent/'LICENSE.md').read_text(),'motion_license':'CC0 1.0',
    'modifications':'Authored head/hair with original weights transferred by matching Biped names; source head/helmet alpha-hidden; not final Rook art'})
glb.save(out/'human.glb')
details=json.loads((source/'retarget_report.json').read_text())['clips']
reference={}
for clip,info in details.items():
    for track in rig.animation_data.nla_tracks: track.mute=track.name!=clip
    samples=[]
    for step in range(9):
        frame=(info['frames']-1)*step/8
        bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame)); bpy.context.view_layer.update()
        evaluated=head.evaluated_get(bpy.context.evaluated_depsgraph_get()); geometry=evaluated.to_mesh()
        points=[list(evaluated.matrix_world @ geometry.vertices[index].co)
                for index in range(0,len(geometry.vertices),max(1,len(geometry.vertices)//25))]
        evaluated.to_mesh_clear(); samples.append({'time_s':frame/30,'points':points})
    reference[clip]=samples
(out/'head_surface_reference.json').write_text(json.dumps(reference),encoding='utf-8')
for track in rig.animation_data.nla_tracks: track.mute=track.name!='Idle'
bpy.context.scene.frame_set(0); bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
shutil.copyfile(source.parent/'LICENSE.md',out/'LICENSE.md')
(out/'assembly_report.json').write_text(json.dumps({'head_vertices':len(head.data.vertices),
    'head_triangles':3342,'weight_groups':len(head.vertex_groups),'clips':list(details),
    'limitations':['Original body head/helmet remain alpha-hidden, not removed',
        'No facial expressions transferred; new head retains source skin weights on shared rig',
        'Scalp, neck seam, alpha LOD and Rook identity require visible review']},indent=2),encoding='utf-8')
print('ROCKETBOX_WEIGHTED_HEAD_ASSEMBLED',len(head.data.vertices),len(reference),flush=True)
