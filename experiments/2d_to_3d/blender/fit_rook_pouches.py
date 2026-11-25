"""Mount two genuine MIT equipment meshes on existing actor; no procedural clothes."""
import hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent.parent))
from equipment_mount import front_offset
from wardrobe_skinning import surface_weights

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'rook_normal_strength139';out=root/'rook_pouches140';out.mkdir(exist_ok=True)
accessories=root/'rocketbox_military03/accessories01/accessories.blend'
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST';bpy.context.view_layer.update()
body=bpy.data.objects['char1'];body.data.calc_loop_triangles()
points=[body.matrix_world@v.co for v in body.data.vertices]
triangles=[tuple(t.vertices) for t in body.data.loop_triangles if all(.9<points[i].z<1.3 for i in t.vertices)
    and (points[t.vertices[1]]-points[t.vertices[0]]).cross(points[t.vertices[2]]-points[t.vertices[0]]).length>1e-10]
tree=BVHTree.FromPolygons(points,triangles,all_triangles=True)
weights=[{body.vertex_groups[g.group].name:g.weight for g in v.groups if g.weight>0} for v in body.data.vertices]
protected={o.name:hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],
    [tuple(p.vertices) for p in o.data.polygons],[[tuple(v.uv) for v in uv.data] for uv in o.data.uv_layers])).encode()).hexdigest()
    for o in scene.objects if o.type=='MESH'}
assert 'Hips' in rig.data.bones
with bpy.data.libraries.load(str(accessories),link=False) as (available,loaded):
    loaded.objects=['AuthoredProp_6135','AuthoredProp_5978']
rows=[]
for obj in loaded.objects:
    scene.collection.objects.link(obj);obj.hide_render=False;obj.hide_set(False)
    bpy.context.view_layer.update()
    original_uv=[[tuple(v.uv) for v in uv.data] for uv in obj.data.uv_layers]
    obj.data.transform(obj.matrix_world);obj.matrix_world=Matrix.Identity(4)
    low=[min(v.co[i] for v in obj.data.vertices) for i in range(3)]
    high=[max(v.co[i] for v in obj.data.vertices) for i in range(3)]
    hits=[]
    for x in (.15,.5,.85):
        for z in (.2,.5,.8):
            origin=Vector((low[0]+x*(high[0]-low[0]),-1,low[2]+z*(high[2]-low[2])))
            hit,normal,index,distance=tree.ray_cast(origin,Vector((0,1,0)),2)
            assert hit is not None, ('No torso support',obj.name,origin)
            hits.append(hit.y)
    shift=front_offset(hits,high[1])
    for vertex in obj.data.vertices:vertex.co.y+=shift
    assert original_uv==[[tuple(v.uv) for v in uv.data] for uv in obj.data.uv_layers]
    for group in list(obj.vertex_groups):obj.vertex_groups.remove(group)
    retained=[];used_bones=set()
    for vertex in obj.data.vertices:
        closest,normal,index,distance=tree.find_nearest(vertex.co)
        assert closest is not None and distance<.15
        ids=triangles[index]
        transferred,fraction=surface_weights(closest,[points[i] for i in ids],[weights[i] for i in ids],limit=8)
        assert fraction>.99
        retained.append(fraction)
        for name,weight in transferred.items():
            assert name in rig.data.bones
            group=obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
            group.add([vertex.index],weight,'REPLACE');used_bones.add(name)
    obj.parent=rig;obj.matrix_world=Matrix.Identity(4)
    for modifier in list(obj.modifiers):obj.modifiers.remove(modifier)
    modifier=obj.modifiers.new('ExistingBeltAttachment','ARMATURE');modifier.object=rig
    obj.name='MIT_Pouch_'+obj.name.split('_')[-1]
    rows.append({'object':obj.name,'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),
                 'y_translation_m':shift,'sampled_torso_front_y_range':[min(hits),max(hits)],
                 'rear_plane_front_margin_m':.004,'mount_bones':sorted(used_bones),
                 'minimum_retained_weight_fraction':min(retained),'binding':'actual torso surface weights',
                 'source_photo_uv_exact':True})
assert protected=={o.name:hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],
    [tuple(p.vertices) for p in o.data.polygons],[[tuple(v.uv) for v in uv.data] for uv in o.data.uv_layers])).encode()).hexdigest()
    for o in scene.objects if o.type=='MESH' and o.name in protected}
rig.data.pose_position='POSE'
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text()+'\n140study: two disconnected Microsoft Rocketbox MIT tactical fabric pouches, original UV/materials, translated to torso surface and skinned using actual existing torso weights. Clothing/skeleton unchanged. Contact/art not accepted before review.\n'
bpy.data.texts.new('MIT_POUCH_SOURCE_CREDITS').write(notice)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,
    export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,
    export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,
    export_all_influences=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf-8')
(out/'fit_report.json').write_text(json.dumps({'source_accessories_sha256':hashlib.sha256(accessories.read_bytes()).hexdigest(),
    'source_actor_glb_sha256':hashlib.sha256((source/'human.glb').read_bytes()).hexdigest(),'pouches':rows,
    'protected_meshes':len(protected),'existing_geometry_uv_exact':True,
    'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),
    'limitations':['Candidate only','Nine torso rays are not general animation collision proof','Camo source palette not final Rook styling']},indent=2))
print('MIT_TACTICAL_POUCHES_FITTED',json.dumps(rows),flush=True)
