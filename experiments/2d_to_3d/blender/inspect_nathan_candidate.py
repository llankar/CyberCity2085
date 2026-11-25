"""Import one licensed professional scan; retain source motion and real texture."""
import json
import math
from pathlib import Path
import bpy
from mathutils import Matrix

source=Path('E:/CyberCity2085-3d-lab/sources/renderpeople_nathan')
folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/renderpeople_nathan01');folder.mkdir(exist_ok=True)
acquisition=json.loads((source/'acquisition.json').read_text())
assert acquisition['license']=='CC-BY-4.0' and acquisition['source_author']=='Renderpeople'
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.fps=30;scene.name='Walk'
bpy.ops.import_scene.gltf(filepath=str(source/'scene.gltf'))
rigs=[obj for obj in scene.objects if obj.type=='ARMATURE']
control_shapes={bone.custom_shape for armature in rigs for bone in armature.pose.bones if bone.custom_shape}
meshes=[obj for obj in scene.objects if obj.type=='MESH' and obj not in control_shapes]
print('NATHAN_IMPORTED_CONTROL_SHAPES',[obj.name for obj in control_shapes],flush=True)
assert len(meshes)==len(rigs)==1
body=meshes[0];rig=rigs[0]
body.data.calc_loop_triangles();assert len(body.data.loop_triangles)==21506
rig.data.pose_position='REST';bpy.context.view_layer.update()
def geometry():
    graph=bpy.context.evaluated_depsgraph_get();evaluated=body.evaluated_get(graph);mesh=evaluated.to_mesh()
    try:return [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    finally:evaluated.to_mesh_clear()
points=geometry();height=max(p.z for p in points)-min(p.z for p in points)
assert 1<height<3 or 100<height<300,('Unreviewed source unit range',height)
scale=.01 if height>100 else 1.
roots=[obj for obj in scene.objects if obj.parent is None and obj not in control_shapes]
for obj in roots:obj.matrix_world=Matrix.Scale(scale,4) @ obj.matrix_world
bpy.context.view_layer.update();points=geometry();ground=min(p.z for p in points)
for obj in roots:obj.matrix_world=Matrix.Translation((0,0,-ground)) @ obj.matrix_world
bpy.context.view_layer.update();points=geometry()
rest_height=max(p.z for p in points)-min(p.z for p in points)
assert 1.4<rest_height<2.2
images=[image for image in bpy.data.images if image.source=='FILE']
assert len(images)==1 and tuple(images[0].size)==(8192,8192)
rig.data.pose_position='POSE'
actions=list(bpy.data.actions)
assert actions
start=min(action.frame_range[0] for action in actions);end=max(action.frame_range[1] for action in actions)
assert abs(start-round(start))<.001 and abs(end-round(end))<.001,('Source timing not on 30Hz frame grid',start,end)
scene.frame_start=round(start);scene.frame_end=round(end)
scene.frame_set(scene.frame_start)
for obj in scene.objects:obj.select_set(obj not in control_shapes)
bpy.context.view_layer.objects.active=rig
notice=(source/'license.txt').read_text();bpy.data.texts.new('SOURCE_CC_BY_4_NOTICE').write(notice)
body['source_author']='Renderpeople';body['source_license']='CC BY 4.0'
body['source_url']='https://sketchfab.com/3d-models/nathan-animated-003-walking-3d-man-143a2b1ea5eb4385ae90a73657aca3bc'
body['modifications']='Unit/ground normalization; source mocap and original8K diffuse retained; no artistically accepted Rook conversion'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'human.glb'),export_format='GLB',use_selection=True,
    use_active_scene=True,export_extras=True,export_animations=True,export_animation_mode='SCENE',
    export_anim_scene_split_object=False,export_anim_single_armature=False,export_anim_slide_to_zero=True,
    export_copyright=notice)
reference=[]
for step in range(9):
    frame=start+(end-start)*step/8
    scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update()
    points=geometry()
    reference.append({'time_s':(frame-start)/30,'points':[list(points[i]) for i in range(0,len(points),max(1,len(points)//40))]})
(folder/'surface_reference.json').write_text(json.dumps({body.name:reference}),encoding='utf8')
report={'source_acquisition':acquisition,'mesh_name':body.name,'vertices':len(body.data.vertices),
        'triangles':21506,'bones':len(rig.data.bones),'source_raw_rest_height':height,
        'unit_scale':scale,'ground_offset_m':-ground,'normalized_rest_height_m':rest_height,
        'source_action_frames':[start,end],'duration_s':(end-start)/30,
        'source_actions':[action.name for action in actions],
        'images':[{'name':image.name,'dimensions':list(image.size),'packed':bool(image.packed_file)} for image in images],
        'limitations':['One source-authored walk, no new action set or retargeting claim',
                       '8K baseColor only; original normal/roughness maps not present in public replica',
                       'Neutral multi-angle and actual combat-scale review still required',
                       'Not fitted cyberpunk clothing or accepted Rook/Raider art']}
(folder/'import_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
(folder/'CREDITS.txt').write_text(notice,encoding='utf8')
print('NATHAN_PROFESSIONAL_SOURCE_IMPORTED',rest_height,len(rig.data.bones),end-start,flush=True)
