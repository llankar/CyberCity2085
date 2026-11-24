"""Bake a representative authored robot shell to standard game PBR textures."""
import json
import sys
from pathlib import Path
import bpy

output=Path(sys.argv[sys.argv.index('--')+1]).resolve()
if output.drive.upper()!='E:': raise ValueError('Use E:')
output.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/generated/phase2/security_geometry01/security_geometry.blend',use_scripts=False)
obj=bpy.data.objects['GEO-shell_shin.L_Evaluated']
assert obj.data.uv_layers.active is not None
scene=bpy.data.scenes.new('PBRPieceBake')
scene.collection.objects.link(obj)
bpy.context.window.scene=scene
bpy.context.view_layer.objects.active=obj
obj.select_set(True)
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=1
scene.render.bake.use_clear=True; scene.render.bake.margin=8
originals=[slot.material for slot in obj.material_slots]
copies=[]
for slot in obj.material_slots:
    slot.material=slot.material.copy()
    material=slot.material; tree=material.node_tree
    output_node=next(n for n in tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
    original_surface=output_node.inputs['Surface'].links[0].from_socket
    group=next((n for n in tree.nodes if n.type=='GROUP' and n.node_tree.name.startswith('SH-secbot.Worn surface')),None)
    if group is None: raise ValueError('Representative material interface changed')
    emission=tree.nodes.new('ShaderNodeEmission')
    target=tree.nodes.new('ShaderNodeTexImage')
    copies.append((material,group,output_node,original_surface,emission,target))
images={}
for channel,socket_name in [('BaseColor','Color'),('Roughness','Roughness'),('Metallic','Metallic')]:
    image=bpy.data.images.new('SecurityShell_'+channel,width=512,height=512,alpha=False)
    if channel!='BaseColor': image.colorspace_settings.name='Non-Color'
    for material,group,node,original,emission,target in copies:
        tree=material.node_tree
        tree.links.new(group.outputs[socket_name],emission.inputs['Color'])
        tree.links.new(emission.outputs[0],node.inputs['Surface'])
        target.image=image; tree.nodes.active=target
    bpy.ops.object.bake(type='EMIT')
    image.filepath_raw=str(output/f'{channel}.png'); image.file_format='PNG'; image.save()
    images[channel]=image
    print('PBR_CHANNEL_BAKED',channel,flush=True)
normal=bpy.data.images.new('SecurityShell_Normal',width=512,height=512,alpha=False)
normal.colorspace_settings.name='Non-Color'
for material,group,node,original,emission,target in copies:
    material.node_tree.links.new(original,node.inputs['Surface'])
    target.image=normal; material.node_tree.nodes.active=target
bpy.ops.object.bake(type='NORMAL',normal_space='TANGENT')
normal.filepath_raw=str(output/'Normal.png'); normal.file_format='PNG'; normal.save()
images['Normal']=normal
material=bpy.data.materials.new('BakedSecurityShellPBR'); material.use_nodes=True
tree=material.node_tree; shader=tree.nodes['Principled BSDF']
for channel,socket in [('BaseColor','Base Color'),('Roughness','Roughness'),('Metallic','Metallic')]:
    texture=tree.nodes.new('ShaderNodeTexImage'); texture.image=images[channel]
    tree.links.new(texture.outputs['Color'],shader.inputs[socket])
texture=tree.nodes.new('ShaderNodeTexImage'); texture.image=normal
normal_node=tree.nodes.new('ShaderNodeNormalMap')
tree.links.new(texture.outputs['Color'],normal_node.inputs['Color'])
tree.links.new(normal_node.outputs['Normal'],shader.inputs['Normal'])
for slot in obj.material_slots: slot.material=material
bpy.ops.wm.save_as_mainfile(filepath=str(output/'security_shell_pbr.blend'))
bpy.ops.export_scene.gltf(filepath=str(output/'security_shell_pbr.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False)
report={'source_piece':obj.name,'channels':list(images),'resolution':512,
        'license':'https://creativecommons.org/licenses/by/4.0/',
        'credit':'Security Bot Rig (CC-BY) Blender Foundation | studio.blender.org',
        'scope':'Representative shell only; exported group Color/Metallic/Roughness and tangent normal',
        'limitations':['Film dust/layered shader fidelity not yet accepted','Not whole robot','No rig/actions']}
(output/'bake_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('CHARGE_PBR_PIECE_EXPORTED',flush=True)
