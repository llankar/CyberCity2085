"""Fit licensed authored jacket to professional scan using measured rig segments."""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent.parent))
from wardrobe_skinning import surface_weights
from garment_alignment import segment_transform
root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'nathan_wardrobe01';out.mkdir(exist_ok=True)
# Read the previous real garment's bind geometry and actual weighted joint frames.
bpy.ops.wm.open_mainfile(filepath=str(root/'wardrobe_fit01/human.blend'),use_scripts=False)
oldrig=bpy.data.objects['Bip01'];oldrig.data.pose_position='REST';bpy.context.view_layer.update()
cloth=bpy.data.objects['AuthoredLeatherJacket_PBRStudy']
oldpoints=[cloth.matrix_world @ v.co for v in cloth.data.vertices]
oldweights=[{cloth.vertex_groups[g.group].name:g.weight for g in v.groups if g.weight>0} for v in cloth.data.vertices]
oldheads={b.name:oldrig.matrix_world @ b.head_local for b in oldrig.data.bones}
bpy.ops.wm.open_mainfile(filepath=str(root/'renderpeople_nathan01/human.blend'),use_scripts=False)
# open_mainfile replaces all datablocks, so append original authored mesh again.
with bpy.data.libraries.load(str(root/'wardrobe_fit01/human.blend'),link=False) as (available,loaded):loaded.objects=['AuthoredLeatherJacket_PBRStudy']
jacket=loaded.objects[0];bpy.context.scene.collection.objects.link(jacket)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST';bpy.context.view_layer.update()
body=bpy.data.objects['Object_96']
def target(token):
    matches=[b for b in rig.data.bones if '_walking_'+token+'_' in b.name]
    assert len(matches)==1,(token,[b.name for b in matches])
    return matches[0].name
mapping={'Bip01 Pelvis':target('hip'),'Bip01 Spine':target('spine_01'),'Bip01 Spine1':target('spine_02'),'Bip01 Spine2':target('spine_03'),'Bip01 Neck':target('neck')}
for oldside,newside in [('L','l'),('R','r')]:
    for oldpart,newpart in [('Clavicle','shoulder'),('UpperArm','upperarm'),('Forearm','lowerarm'),('Hand','hand')]:
        mapping['Bip01 '+oldside+' '+oldpart]=target(newpart+'_'+newside)
newheads={old:rig.matrix_world @ rig.data.bones[new].head_local for old,new in mapping.items()}
transforms={}
for old,new in mapping.items():
    if any(p in old for p in ['Clavicle','UpperArm','Forearm']):
        nextpart={'Clavicle':'UpperArm','UpperArm':'Forearm','Forearm':'Hand'}[old.split()[-1]]
        child=old.rsplit(' ',1)[0]+' '+nextpart
        transforms[old]=Matrix(segment_transform(oldheads[old],oldheads[child],newheads[old],newheads[child]))
    else:
        transforms[old]=Matrix.Translation(newheads[old]-oldheads[old])
assert set(k for weights in oldweights for k in weights)<=set(transforms),set(k for w in oldweights for k in w)-set(transforms)
jacket.parent=None;jacket.matrix_world=Matrix.Identity(4);jacket.modifiers.clear();jacket.vertex_groups.clear()
for vertex,point,weights in zip(jacket.data.vertices,oldpoints,oldweights):
    vertex.co=sum(((transforms[name] @ point)*weight for name,weight in weights.items()),Vector())
# Bind to existing source skin by barycentric nearest-surface transfer.
points=[body.matrix_world @ v.co for v in body.data.vertices]
body.data.calc_loop_triangles()
allowed=set(mapping.values())|{b.name for b in rig.data.bones if '_twist_' in b.name}
weights=[{body.vertex_groups[g.group].name:g.weight for g in v.groups if body.vertex_groups[g.group].name in allowed and g.weight>0} for v in body.data.vertices]
triangles=[tuple(t.vertices) for t in body.data.loop_triangles if all(sum(weights[i].values())>.2 for i in t.vertices) and (points[t.vertices[1]]-points[t.vertices[0]]).cross(points[t.vertices[2]]-points[t.vertices[0]]).length>1e-9]
surface=BVHTree.FromPolygons(points,triangles,all_triangles=True)
groups={n:jacket.vertex_groups.new(name=n) for n in allowed}
maxgap=0.;retained=1.;pushed=0;maxpush=0.
for v in jacket.data.vertices:
    near,normal,index,gap=surface.find_nearest(v.co);assert near is not None and gap<.25,(v.index,gap)
    maxgap=max(maxgap,gap);ids=triangles[index]
    signed=(v.co-near).dot(normal)
    if signed<.014:
        shift=.014-signed;v.co+=normal*shift;pushed+=1;maxpush=max(maxpush,shift)
    values,kept=surface_weights(near,[points[i] for i in ids],[weights[i] for i in ids]);retained=min(retained,kept)
    for n,w in values.items():groups[n].add([v.index],w,'REPLACE')
# Custom corner normals belonged to the old A-pose; reset after actual geometry fit.
jacket.data.normals_split_custom_set([(0.,0.,0.)]*len(jacket.data.loops))
for face in jacket.data.polygons:face.use_smooth=True
jacket.parent=rig;jacket.matrix_world=Matrix.Identity(4)
modifier=jacket.modifiers.new('ProfessionalSourceSkin','ARMATURE');modifier.object=rig
jacket['source_fit']='Measured Rocketbox A-rest to Nathan T-rest segment fit; real authored garment, no primitive clothing'
jacket['source_credits']=(root/'trebejo_leather02/CREDITS.txt').read_text()
bpy.context.view_layer.update()
evaluated=jacket.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
error=max((evaluated.matrix_world @ v.co-jacket.data.vertices[v.index].co).length for v in mesh.vertices)
evaluated.to_mesh_clear();assert error<1e-5,error
rig.data.pose_position='POSE';scene=bpy.context.scene;scene.frame_set(0)
control_shapes={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in scene.objects:obj.select_set(obj not in control_shapes)
bpy.context.view_layer.objects.active=rig
notice=(root/'renderpeople_nathan01/CREDITS.txt').read_text()+'\n'+(root/'trebejo_leather02/CREDITS.txt').read_text()
bpy.data.texts.new('COMBINED_WARDROBE_CREDITS').write(notice)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,export_extras=True,export_animations=True,export_animation_mode='SCENE',export_anim_scene_split_object=False,export_anim_single_armature=False,export_anim_slide_to_zero=True,export_copyright=notice)
reference=[]
for step in range(9):
    frame=67*step/8;scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update()
    evaluated=jacket.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    reference.append({'time_s':frame/30,'points':[list(evaluated.matrix_world @ mesh.vertices[i].co) for i in range(0,len(mesh.vertices),max(1,len(mesh.vertices)//40))]});evaluated.to_mesh_clear()
(out/'surface_reference.json').write_text(json.dumps({jacket.name:reference}))
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'fit_report.json').write_text(json.dumps({'joint_mapping':mapping,'maximum_projection_gap_m':maxgap,'minimum_retained_weight':retained,'rest_binding_error_m':error,'garment_vertices':len(jacket.data.vertices),'projected_clearance_m':.014,'clearance_adjusted_vertices':pushed,'maximum_clearance_adjustment_m':maxpush,'limitations':['Source Tshirt retained; fit/penetration needs visible review','One original Walk only','No accepted Rook identity']},indent=2))
print('NATHAN_AUTHORED_GARMENT_BOUND',maxgap,retained,error,flush=True)
