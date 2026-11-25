"""Bake short-range groom/head occlusion into a separate source-derived palette."""
import json
from pathlib import Path
import bpy
import numpy as np

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'einar_groom_full02_layered'; folder=root/'einar_groom_occlusion03'
folder.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'authored_groom.blend'),use_scripts=False)
scene=bpy.context.scene; objects=[obj for obj in scene.objects if obj.type=='MESH']
assert len(objects)==4
with bpy.data.libraries.load(str(root/'einar_pbr01/human_pbr.blend'),link=False) as (available,loaded):
    loaded.objects=['GEO-einar_head_GameStudy']
head=loaded.objects[0]; scene.collection.objects.link(head)
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=1
scene.render.bake.target='VERTEX_COLORS'
statistics={}
for obj in objects:
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
    mesh=obj.data; color=mesh.color_attributes['GameHairColor']
    ao_colors=mesh.color_attributes.new(name='GameHairOcclusion',type='FLOAT_COLOR',domain='CORNER')
    mesh.color_attributes.active_color_index=len(mesh.color_attributes)-1
    material=obj.data.materials[0]; tree=material.node_tree
    output=tree.nodes['Material Output']; original=output.inputs['Surface'].links[0].from_socket
    ao=tree.nodes.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value=.015; ao.samples=16
    emission=tree.nodes.new('ShaderNodeEmission'); tree.links.new(ao.outputs['Color'],emission.inputs['Color'])
    tree.links.new(emission.outputs[0],output.inputs['Surface'])
    bpy.ops.object.bake(type='EMIT')
    tree.links.new(original,output.inputs['Surface'])
    # Adding/baking a custom-data layer can invalidate cached RNA wrappers.
    color=mesh.color_attributes['GameHairColor']
    ao_colors=mesh.color_attributes['GameHairOcclusion']
    assert len(color.data)==len(ao_colors.data)>0
    colors=np.empty(len(color.data)*4,dtype=np.float32); color.data.foreach_get('color',colors)
    occlusion=np.empty(len(ao_colors.data)*4,dtype=np.float32); ao_colors.data.foreach_get('color',occlusion)
    colors=colors.reshape(-1,4); values=occlusion.reshape(-1,4)[:,0]
    assert np.isfinite(values).all() and np.min(values)>=0 and np.max(values)<=1.00001
    colors[:,:3]*=values[:,None]
    color.data.foreach_set('color',colors.reshape(-1))
    mesh.color_attributes.active_color_index=list(mesh.color_attributes).index(color)
    mesh.color_attributes.render_color_index=mesh.color_attributes.active_color_index
    statistics[obj.name]={'min':float(values.min()),'mean':float(values.mean()),'max':float(values.max())}
    print('GROOM_OCCLUSION_BAKED',obj.name,statistics[obj.name],flush=True)
head.hide_render=True; head.hide_set(True)
for obj in objects: obj.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'authored_groom.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'authored_groom.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False)
report=json.loads((source/'groom_report.json').read_text())
report['occlusion']={'distance_m':.015,'samples':16,'geometry':'Full authored groom and original converted head','parts':statistics}
report['limitations'].append('Short-range occlusion baked into color for independent runtime rendering; not full film transport')
(folder/'groom_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('GROOM_OCCLUSION_STUDY_EXPORTED',flush=True)
