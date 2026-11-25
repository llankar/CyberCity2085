"""Audit the partial licensed source before extracting any head/hair geometry."""
import json
from pathlib import Path
import bpy
source=Path('E:/CyberCity2085-3d-lab/sources/rocketbox/Male_Adult_08')
out=Path('E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_hair08'); out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(source/'Export/Male_Adult_08.fbx'),use_anim=False)
report={'images':[],'materials':[],'meshes':[],'partial_source':True}
for image in bpy.data.images:
    target=source/'Textures'/Path(image.filepath.replace('\\','/')).name
    report['images'].append({'name':image.name,'source':image.filepath,'acquired':target.exists()})
    if target.exists(): image.filepath=str(target); image.reload()
for material in bpy.data.materials:
    report['materials'].append({'name':material.name,'textures':[{'image':node.image.name if node.image else None,
        'outputs':[(link.from_socket.name,link.to_socket.name) for output in node.outputs for link in output.links]}
        for node in material.node_tree.nodes if node.type=='TEX_IMAGE']})
for obj in bpy.context.scene.objects:
    if obj.type!='MESH': continue
    obj.data.calc_loop_triangles()
    per_material=[]
    for index,slot in enumerate(obj.material_slots):
        used={vertex for face in obj.data.polygons if face.material_index==index for vertex in face.vertices}
        points=[obj.matrix_world @ obj.data.vertices[index].co for index in used]
        per_material.append({'name':slot.material.name,'vertices':len(used),
            'bounds':[[min(p[axis] for p in points) for axis in range(3)],[max(p[axis] for p in points) for axis in range(3)]] if points else None})
    report['meshes'].append({'name':obj.name,'vertices':len(obj.data.vertices),'triangles':len(obj.data.loop_triangles),'materials':per_material})
(out/'import_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ROCKETBOX_HAIR_SOURCE_AUDIT',json.dumps(report),flush=True)
