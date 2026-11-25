"""Inspect genuine MIT disconnected equipment components before fitting them."""
import json,hashlib
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'rocketbox_military03/accessories01/accessories.blend'
out=root/'rook_equipment140';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
rows=[]
for component in (6135,5978,5661,5834):
    obj=bpy.data.objects['AuthoredProp_'+str(component)]
    obj.hide_render=False;obj.hide_set(False)
    for item in bpy.context.scene.objects:item.select_set(item==obj)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.gltf(filepath=str(out/('component_'+str(component)+'.glb')),export_format='GLB',
        use_selection=True,export_animations=False,export_copyright='Copyright(c)2020 Microsoft; MIT License')
    rows.append({'component':component,'source_object':obj.name,'vertices':len(obj.data.vertices),
                 'faces':len(obj.data.polygons),'source_uv_retained':True})
(out/'component_review.json').write_text(json.dumps({'source_blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'parts':rows,'scope':'Actual isolated source equipment; semantic/art review before fitting'},indent=2))
(out/'CREDITS.txt').write_text((root/'rocketbox_military03/LICENSE.md').read_text()+
    '\nMicrosoft Rocketbox Military Male03 isolated equipment components, original UV/materials; MIT source component numbers in component_review.json.\n',encoding='utf-8')
print('AUTHORED_EQUIPMENT_REVIEW_EXPORTED',len(rows),flush=True)
