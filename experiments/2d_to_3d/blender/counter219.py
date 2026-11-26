"""Replace blank counter backing with metric worn-metal cladding, same geometry."""
from pathlib import Path
import json
import bpy
from mathutils import Vector
LAB=Path('E:/CyberCity2085-3d-lab')
OUT=LAB/'generated/phase2/showcase219'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase216/environment.blend'))
steel=bpy.data.materials['Kiosk207_WeatheredSteel']
variants=[]
for name,tint in [('medical',(.52,.66,.64)),('repair',(.50,.40,.29)),('salvage',(.42,.45,.53))]:
 material=steel.copy();material.name='Counter219 worn '+name
 shader=material.node_tree.nodes.get('Principled BSDF')
 shader.inputs['Metallic'].default_value=.35
 shader.inputs['Roughness'].default_value=.78
 # Bake tint into a separate image: exported GLB keeps actual worn surface detail.
 node=next(n for n in material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.name.startswith('diff'))
 image=node.image.copy()
 import numpy as np
 pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels)
 pixels.reshape(-1,4)[:,:3]*=np.array(tint,dtype=np.float32)
 image.pixels.foreach_set(pixels);image.update()
 image.filepath_raw=str(OUT/(name+'.png'));image.file_format='PNG';image.save()
 node.image=image
 variants.append(material)
records=[]
for index,name in enumerate(['market_nmid','market_nw','market_ne','market_sw','market_smid','market_se','market_east']):
 root=bpy.data.objects['Occludable_'+name]
 body=next(o for o in root.children_recursive if o.name.startswith('PBR_Facade_'))
 body.data=body.data.copy()
 slot=len(body.data.materials);body.data.materials.append(variants[index%3])
 uv=body.data.uv_layers.active or body.data.uv_layers.new()
 normal_matrix=body.matrix_world.to_3x3().inverted().transposed()
 changed=0
 for polygon in body.data.polygons:
  normal=(normal_matrix@polygon.normal).normalized()
  if abs(normal.z)>.2:continue
  polygon.material_index=slot;changed+=1
  for loop in polygon.loop_indices:
   point=body.matrix_world@body.data.vertices[body.data.loops[loop].vertex_index].co
   uv.data[loop].uv=((point.y if abs(normal.x)>.5 else point.x)/2,point.z/2)
 records.append({'shop':name,'vertical_faces':changed})
bpy.ops.object.select_all(action='SELECT')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'counter.json').write_text(json.dumps(records,indent=2))
print('COUNTER219_EXPORTED',records)
