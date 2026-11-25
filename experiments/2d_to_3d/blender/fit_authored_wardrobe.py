"""Fit an actual licensed garment onto the existing shared rig, not a new avatar."""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb
from wardrobe_skinning import surface_weights

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
folder=root/'wardrobe_fit01';folder.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'rocketbox_hair08/character01/human.blend'),use_scripts=False)
rig=bpy.data.objects['Bip01'];rig.data.pose_position='REST';bpy.context.view_layer.update()
body=bpy.data.objects['sm004_hipoly_81_bones']
graph=bpy.context.evaluated_depsgraph_get();evaluated=body.evaluated_get(graph);mesh=evaluated.to_mesh()
points=[evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
mesh.calc_loop_triangles();triangles=[tuple(triangle.vertices) for triangle in mesh.loop_triangles]
evaluated.to_mesh_clear()
allowed={name for name in rig.data.bones.keys() if any(token in name for token in ['Pelvis','Spine','Neck','Clavicle','UpperArm','Forearm',' Hand'])}
weights=[]
for vertex in body.data.vertices:
    weights.append({body.vertex_groups[g.group].name:g.weight for g in vertex.groups
                    if body.vertex_groups[g.group].name in allowed and g.weight>0})
triangles=[ids for ids in triangles if all(sum(weights[i].values())>.2 for i in ids)
           and (points[ids[1]]-points[ids[0]]).cross(points[ids[2]]-points[ids[0]]).length>1e-9]
surface=BVHTree.FromPolygons(points,triangles,all_triangles=True)
with bpy.data.libraries.load(str(root/'trebejo_leather02/jacket.blend'),link=False) as (available,loaded):
    loaded.objects=['AuthoredLeatherJacket_PBRStudy']
jacket=loaded.objects[0];bpy.context.scene.collection.objects.link(jacket)
neck=rig.matrix_world @ rig.data.bones['Bip01 Neck'].head_local
offset=Vector((0,.015,neck.z-.7+.025))
fit=Matrix.Translation(offset) @ Matrix.Diagonal((1.02,1.15,1.,1.))
jacket.data.transform(fit);jacket.parent=rig;jacket.matrix_world=Matrix.Identity(4)
original_hem=min(vertex.co.z for vertex in jacket.data.vertices)
for vertex in jacket.data.vertices:
    if abs(vertex.co.x)<.35:
        hem_blend=1-max(0.,min(1.,(vertex.co.z-original_hem)/.22))
        vertex.co.z-=.08*hem_blend*hem_blend
    amount=max(0.,min(1.,(abs(vertex.co.x)-.25)/.35))
    amount=amount*amount*(3-2*amount)
    vertex.co.y-=.08*amount
    vertex.co.z-=.04*amount
jacket['modifications']=jacket.get('modifications','')+'; shared-rig rest fit, extended authored hem8cm and cuff alignment, barycentric source skin transfer'
jacket.vertex_groups.clear();groups={name:jacket.vertex_groups.new(name=name) for name in allowed}
modifier=jacket.modifiers.new('SharedAuthoredRigWeights','ARMATURE');modifier.object=rig
max_distance=0.;min_retained=1.;max_influences=0
for vertex in jacket.data.vertices:
    nearest,normal,index,distance=surface.find_nearest(vertex.co)
    assert nearest is not None and distance<.25,('Garment too far from body',vertex.index,distance)
    max_distance=max(max_distance,distance)
    ids=triangles[index]
    transferred,retained=surface_weights(nearest,[points[i] for i in ids],[weights[i] for i in ids])
    min_retained=min(min_retained,retained);assert retained>.95
    for name,value in transferred.items():groups[name].add([vertex.index],value,'REPLACE')
    max_influences=max(max_influences,len(transferred))

# Source character is preserved. Only covered upper uniform/gear surfaces in this
# derivative become invisible; hands/trousers/boots and the authored new head stay.
hidden=bpy.data.materials.new('CoveredOriginalUniform_Transparent');hidden.use_nodes=True
hidden.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=0
hidden.surface_render_method='DITHERED'
hidden_index=len(body.data.materials);body.data.materials.append(hidden)
covered=0
hem=min(vertex.co.z for vertex in jacket.data.vertices)
coverage_z=(rig.matrix_world @ rig.data.bones['Bip01 Pelvis'].head_local).z-.05
for face in body.data.polygons:
    material=body.data.materials[face.material_index]
    if material.name in ['sm004_head','sm004_helmet']:continue
    center=sum((points[i] for i in face.vertices),Vector())/len(face.vertices)
    hand_weight=sum(sum(g.weight for g in body.data.vertices[i].groups if ' Hand' in body.vertex_groups[g.group].name or 'Finger' in body.vertex_groups[g.group].name) for i in face.vertices)/len(face.vertices)
    if center.z>coverage_z and hand_weight<.4:
        face.material_index=hidden_index;covered+=1
assert covered>100
bpy.context.view_layer.update()
evaluated=jacket.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
rest_error=max((evaluated.matrix_world @ vertex.co-jacket.data.vertices[vertex.index].co).length for vertex in mesh.vertices)
evaluated.to_mesh_clear();assert rest_error<1e-5,('Invalid garment rest binding',rest_error)
rig.data.pose_position='POSE'
for obj in bpy.context.scene.objects:obj.select_set(obj in [rig,body,jacket] or obj.name=='AuthoredHeadHair')
bpy.context.view_layer.objects.active=rig
for track in rig.animation_data.nla_tracks:track.mute=False
bpy.ops.export_scene.gltf(filepath=str(folder/'human.glb'),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='NLA_TRACKS',export_frame_range=False,
    export_force_sampling=True,export_try_sparse_sk=True,export_extras=True,
    export_copyright='Microsoft Rocketbox MIT; Quaternius UAL CC0; Trebejo jacket CC BY4; ambientCG leather CC0')
glb=Glb(folder/'human.glb')
for material in glb.doc['materials']:
    if material.get('name')=='m014_opacity':material.update({'alphaMode':'MASK','alphaCutoff':.4,'doubleSided':True})
glb.doc['asset'].setdefault('extras',{}).update({'source_license_notice':(root/'rocketbox_military03/LICENSE.md').read_text(),
    'garment_credits':(root/'trebejo_leather02/CREDITS.txt').read_text(),
    'scope':'First garment fitting/weight-transfer study; not final Rook art'})
glb.save(folder/'human.glb')
reference={};details=json.loads((root/'rocketbox_military03/motion01/retarget_report.json').read_text())['clips']
for clip,info in details.items():
    for track in rig.animation_data.nla_tracks:track.mute=track.name!=clip
    samples=[]
    for step in range(9):
        frame=(info['frames']-1)*step/8
        bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
        evaluated=jacket.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        sample=[list(evaluated.matrix_world @ mesh.vertices[i].co) for i in range(0,len(mesh.vertices),max(1,len(mesh.vertices)//40))]
        evaluated.to_mesh_clear();samples.append({'time_s':frame/30,'points':sample})
    reference[clip]=samples
(folder/'garment_surface_reference.json').write_text(json.dumps(reference),encoding='utf8')
for track in rig.animation_data.nla_tracks:track.mute=track.name!='Idle'
bpy.context.scene.frame_set(0);bpy.ops.file.pack_all()
bpy.data.texts.new('GARMENT_CREDITS').write((root/'trebejo_leather02/CREDITS.txt').read_text())
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human.blend'))
(folder/'fit_report.json').write_text(json.dumps({'garment_vertices':len(jacket.data.vertices),'max_body_surface_distance_m':max_distance,
    'minimum_weight_retained_before_normalization':min_retained,'max_bone_influences':max_influences,
    'rest_binding_error_m':rest_error,'covered_source_polygons':covered,'fit_translation_m':list(offset),
    'authored_hem_extension_m':.08,'cuff_alignment_yz_m':[-.08,-.04],'covered_uniform_height_m':coverage_z,
    'fit_scale':[1.02,1.15,1.],'clips':list(details),
    'limitations':['Covered source upper clothing alpha-hidden, not deleted','First rest fit; animation collisions/cuff/neck seams require review','Inherited head/hair still not artistically accepted','No final character or production changes']},indent=2))
print('AUTHORED_WARDROBE_FITTED',max_distance,min_retained,rest_error,covered,flush=True)
