"""Inspect actual MIT game-head/eye geometry independently of its sunglasses."""
import hashlib
import json
from pathlib import Path
import bpy
import bmesh
from mathutils import Matrix

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'rocketbox_military03'
out=root/'rocketbox_head_review125';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'character_dielectric.blend'),use_scripts=False)
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
rig.data.pose_position='REST';bpy.context.view_layer.update()
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.vertex_groups)
evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh=bpy.data.meshes.new_from_object(evaluated,depsgraph=bpy.context.evaluated_depsgraph_get())
mesh.transform(evaluated.matrix_world)
head_index=next(i for i,m in enumerate(mesh.materials) if m.name=='sm004_head')
head_material=mesh.materials[head_index]
bm=bmesh.new();bm.from_mesh(mesh)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=head_index or min(v.co.z for v in f.verts)<1.48],context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
remaining=set(bm.verts);removed=0;lenses=0
while remaining:
    seed=next(iter(remaining));component={seed};stack=[seed]
    while stack:
        vertex=stack.pop()
        for edge in vertex.link_edges:
            neighbour=edge.other_vert(vertex)
            if neighbour not in component:component.add(neighbour);stack.append(neighbour)
    remaining-=component
    low=[min(v.co[i] for v in component) for i in range(3)]
    high=[max(v.co[i] for v in component) for i in range(3)]
    if high[0]-low[0]>.15 and .02<high[2]-low[2]<.06 and 1.65<(high[2]+low[2])/2<1.72:
        removed+=len({f for v in component for f in v.link_faces})
        bmesh.ops.delete(bm,geom=list(component),context='VERTS')
    elif len({f for v in component for f in v.link_faces})==64 and .05<high[0]-low[0]<.055 and low[1]<-.125 and 1.66<low[2]<1.67:
        # Separate solid sunglass lenses, in front of the smaller actual eyeballs.
        lenses+=64
        bmesh.ops.delete(bm,geom=list(component),context='VERTS')
assert removed==370,('Unexpected sunglasses component',removed)
assert lenses==128,('Unexpected separate lens components',lenses)
for face in bm.faces:face.material_index=0
bm.to_mesh(mesh);bm.free();mesh.materials.clear();mesh.materials.append(head_material)
for original in list(bpy.context.scene.objects):bpy.data.objects.remove(original,do_unlink=True)
head=bpy.data.objects.new('ActualGameHeadAndEyes',mesh);bpy.context.scene.collection.objects.link(head)
head.matrix_world=Matrix.Identity(4)
notice=(source/'LICENSE.md').read_text()+'\nMicrosoft Rocketbox Military Male03: isolated original head/eyes;370frame and128lens faces removed by inspected component bounds. Original photo UV/skin material retained. No Rook fit or facial rig acceptance.\n'
credits=bpy.data.texts.new('MIT_HEAD_CREDITS');credits.write(notice);credits.use_fake_user=True
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.context.view_layer.objects.active=head;head.select_set(True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'head.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'head.glb'),export_format='GLB',use_selection=True,export_animations=False,export_copyright=notice)
mesh.calc_loop_triangles()
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'head_report.json').write_text(json.dumps({'removed_sunglasses_faces':removed,'removed_lens_faces':lenses,'triangles':len(mesh.loop_triangles),'vertices':len(mesh.vertices),'glb_sha256':hashlib.sha256((out/'head.glb').read_bytes()).hexdigest(),'limitations':['Original game head; no new body fit or hair transplant','Eye and skin artistic inspection required']},indent=2),encoding='utf8')
print('ROCKETBOX_UNCOVERED_HEAD_READY',flush=True)
