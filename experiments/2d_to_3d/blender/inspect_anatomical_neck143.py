"""Read-only source anatomy inventory at the actual target neckline."""
import json
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
report={}
for folder,filename in [('rocketbox_military03','character_dielectric.blend'),('diesel_candidate01','human.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(root/folder/filename),use_scripts=False)
    for rig in [o for o in bpy.context.scene.objects if o.type=='ARMATURE']:rig.data.pose_position='REST'
    bpy.context.view_layer.update();items=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH' or not obj.vertex_groups:continue
        evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        world=[evaluated.matrix_world@v.co for v in mesh.vertices]
        for index,material in enumerate(mesh.materials):
            faces=[p for p in mesh.polygons if p.material_index==index and all(abs(world[i].x)<.18 and 1.38<world[i].z<1.85 for i in p.vertices)]
            if not faces:continue
            points=[world[i] for p in faces for i in p.vertices]
            items.append({'object':obj.name,'material':material.name,'faces':len(faces),
                          'bounds':[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]})
        evaluated.to_mesh_clear()
    report[folder]=items
out=root/'rook_anatomy143';out.mkdir(exist_ok=True)
(out/'source_inventory.json').write_text(json.dumps(report,indent=2))
print('ANATOMICAL_SOURCE_INVENTORY',json.dumps(report),flush=True)
