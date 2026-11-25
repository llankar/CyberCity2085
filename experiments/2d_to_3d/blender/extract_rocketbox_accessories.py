"""Extract only real disconnected authored props; do not invent modular clothes."""
import json
import shutil
from pathlib import Path
import bpy
import bmesh

root=Path('E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03')
out=root/'accessories01'; out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'character_dielectric.blend'),use_scripts=False)
source=next(obj for obj in bpy.context.scene.objects if obj.type=='MESH')
audit=json.loads((root/'component_audit.json').read_text())
selected=[part for part in audit['components'] if part['vertices']>=20 and
    (set(part['materials']) <= {'sm004_equipment','sm004_helmet','sm004_pistol'} or part['component']==7249)]
# Recreate connectivity IDs exactly as the independent source inventory.
parents=list(range(len(source.data.vertices)))
def find(index):
    while parents[index]!=index:
        parents[index]=parents[parents[index]]; index=parents[index]
    return index
for edge in source.data.edges:
    a,b=map(find,edge.vertices)
    if a!=b: parents[b]=a
groups={}
for vertex in source.data.vertices: groups.setdefault(find(vertex.index),set()).add(vertex.index)
objects=[]; results=[]
graph=bpy.context.evaluated_depsgraph_get()
for part in selected:
    geometry=bpy.data.meshes.new_from_object(source.evaluated_get(graph),depsgraph=graph)
    assert len(geometry.vertices)==len(source.data.vertices)
    bm=bmesh.new(); bm.from_mesh(geometry); bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in groups[part['component']]],context='VERTS')
    bm.to_mesh(geometry); bm.free(); geometry.update(); geometry.calc_loop_triangles()
    assert len(geometry.vertices)==part['vertices']
    assert len(geometry.polygons)==part['faces']
    assert geometry.uv_layers.active is not None
    obj=bpy.data.objects.new('AuthoredProp_'+str(part['component']),geometry)
    bpy.context.scene.collection.objects.link(obj); obj.matrix_world=source.matrix_world.copy()
    obj['source_component']=part['component']; obj['suggested_mount_bone']=part['dominant_bones'][0]
    obj['source_license']='Microsoft Rocketbox MIT; static rest-space extraction, not fitted rig'
    objects.append(obj)
    results.append({'object':obj.name,'vertices':len(geometry.vertices),'triangles':len(geometry.loop_triangles),
        'source_component':part['component'],'materials':part['materials'],'suggested_mount_bones':part['dominant_bones']})
for obj in bpy.context.scene.objects:
    obj.select_set(obj in objects)
    if obj not in objects: obj.hide_render=True; obj.hide_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'accessories.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'accessories.glb'),export_format='GLB',use_selection=True,
    export_animations=False,export_extras=True,export_copyright='Copyright (c) 2020 Microsoft; MIT License')
shutil.copyfile(root/'LICENSE.md',out/'LICENSE.md')
(out/'extraction_report.json').write_text(json.dumps({'parts':results,
    'limitations':['Static authored accessories, not new fitted clothing or animations',
                   'Main body/head/clothes/boots/gloves share a connected surface; not automatically modular',
                   'Component semantic names and future fit need inspection'],'source_license':'MIT'},indent=2),encoding='utf-8')
print('ROCKETBOX_AUTHORED_ACCESSORIES_EXTRACTED',len(results),sum(p['triangles'] for p in results),flush=True)
