"""Measure existing rig/garment landmarks before fitting or deleting geometry."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
folder=root/'wardrobe_fit01';folder.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'rocketbox_hair08/character01/human.blend'),use_scripts=False)
rig=bpy.data.objects['Bip01'];rig.data.pose_position='REST';bpy.context.view_layer.update()
graph=bpy.context.evaluated_depsgraph_get()
report={'bones':{},'meshes':[]}
for bone in rig.data.bones:
    if any(token in bone.name.lower() for token in ['spine','pelvis','neck','upperarm','forearm','hand']):
        report['bones'][bone.name]={'head':list(rig.matrix_world @ bone.head_local),
                                   'tail':list(rig.matrix_world @ bone.tail_local)}
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
    points=[evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    report['meshes'].append({'name':obj.name,'vertices':len(points),
                            'bounds':[[min(p[i] for p in points) for i in range(3)],
                                      [max(p[i] for p in points) for i in range(3)]],
                            'materials':[slot.material.name for slot in obj.material_slots]})
    evaluated.to_mesh_clear()
(folder/'landmark_audit.json').write_text(json.dumps(report,indent=2))
print('WARDROBE_LANDMARK_AUDIT',json.dumps(report),flush=True)
