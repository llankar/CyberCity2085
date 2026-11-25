"""First real CC0 quiff fit on the intact authored head; private art diagnostic."""
import hashlib,json,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb
from game_materials import restore

root=Path('E:/CyberCity2085-3d-lab/generated/phase2');out=root/'amjviz_hair148';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'amjviz_actions146/human_actions.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST';bpy.context.view_layer.update()
body=max((o for o in scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
hair_slot=next(i for i,m in enumerate(body.data.materials) if m.name=='Hair2')
old_hair_faces=sum(f.material_index==hair_slot for f in body.data.polygons)
def protected(obj):
    values=[]
    for f in obj.data.polygons:
        if f.material_index==hair_slot:continue
        values.append((f.material_index,tuple(tuple(obj.data.vertices[i].co) for i in f.vertices),
                       tuple(tuple(obj.data.uv_layers.active.data[i].uv) for i in f.loop_indices)))
    return hashlib.sha256(repr(values).encode()).hexdigest()
before=protected(body)
bm=bmesh.new();bm.from_mesh(body.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index==hair_slot],context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bm.to_mesh(body.data);bm.free();assert protected(body)==before
# Use only the real upper scalp surface, never a primitive cap or replacement neck.
body.data.calc_loop_triangles();points=[body.matrix_world@v.co for v in body.data.vertices]
triangles=[tuple(t.vertices) for t in body.data.loop_triangles if min(points[i].z for i in t.vertices)>1.70]
tree=BVHTree.FromPolygons(points,triangles,all_triangles=True)
with bpy.data.libraries.load(str(root/'rook_undercut133/human.blend'),link=False) as (_,data):data.objects=['ActualCopperQuiff']
hair=data.objects[0];source_world=hair.matrix_world.copy();hair.data=hair.data.copy()
scene.collection.objects.link(hair);hair.name='ActualCopperQuiff148'
world_points=[source_world@v.co for v in hair.data.vertices]
center=Vector((-.002,.032,1.70658684));target=Vector((.001,.036,1.735))
fit_offsets=[]
for vertex,point in zip(hair.data.vertices,world_points):
    p=target+Vector(((point.x-center.x)*1.06,(point.y-center.y)*1.10,(point.z-center.z)*1.16))
    band=point.z-center.z
    if band<.025:
        nearest,normal,index,distance=tree.find_nearest(p)
        if index is not None and distance<.045:
            blend=max(0.,min(1.,1-band/.025));blend=blend*blend*(3-2*blend)
            new=p.lerp(nearest+normal*.0015,blend);fit_offsets.append((new-p).length);p=new
    vertex.co=rig.matrix_world.inverted()@p
hair.parent=rig;hair.matrix_parent_inverse=Matrix.Identity(4);hair.matrix_basis=Matrix.Identity(4)
for group in list(hair.vertex_groups):hair.vertex_groups.remove(group)
hair.vertex_groups.new(name='DEF-spine.006').add(list(range(len(hair.data.vertices))),1.,'REPLACE')
for modifier in list(hair.modifiers):hair.modifiers.remove(modifier)
hair.modifiers.new('VerifiedGameSkeleton','ARMATURE').object=rig
rig.data.pose_position='POSE';scene.frame_set(38);bpy.context.view_layer.update()
notice=(root/'amjviz_actions146/CREDITS_equipped.txt').read_text()+ '\nCC0 actual quiff mesh/material from rook_undercut133; only Hair2 faces removed from AmJViZ body. Private148fit diagnostic, art/contact NOT accepted.\n'
notice+='\nHair source: Grab3D Cyborg, CC0 1.0, https://grab3d.com/models/characters/cyborg/ ; https://creativecommons.org/publicdomain/zero/1.0/legalcode . Publisher discloses AI-assisted Meshy base mesh/textures with Blender cleanup. Only the isolated quiff/UV/material is reused, not previous replacement heads or hands.\n'
(out/'CREDITS.txt').write_text(notice)
for obj in scene.objects:obj.select_set(obj==rig or obj.type=='MESH')
bpy.context.view_layer.objects.active=rig
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human_raw.glb'),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,
    export_rest_position_armature=True,export_optimize_animation_size=False,
    export_optimize_animation_keep_anim_armature=True,export_optimize_animation_keep_anim_object=True,
    export_all_influences=True,export_copyright=notice)
compiled=Glb(out/'human_raw.glb');materials=restore(compiled,Glb(root/'amjviz_actions146/human_actions.glb'));compiled.save(out/'human.glb')
(out/'hair_fit.json').write_text(json.dumps({'removed_hair_faces':old_hair_faces,'replacement_faces':len(hair.data.polygons),
    'protected_body_geometry_uv_hash':before,'retained_nonhair_body_geometry_uv_exact':protected(body)==before,
    'maximum_root_conform_m':max(fit_offsets,default=0.),'root_fit_vertices':len(fit_offsets),
    'materials':materials,'scope':'First genuine licensed hair fit; neutral profile/front/back and native deformation checks still required'},indent=2))
print('AMJVIZ_REAL_QUIFF_FIT_EXPORTED',flush=True)
