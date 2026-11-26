"""Retain the heavy painted robot; add metal response and texture-aligned sensors."""
from pathlib import Path
import bpy,json,numpy as np
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/robot210';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/robot193/robot_actions.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');bones=len(rig.data.bones)
changes=[]
for index,mat in enumerate(list(bpy.data.materials)):
 if not mat.use_nodes:continue
 shader=mat.node_tree.nodes.get('Principled BSDF')
 if not shader or not shader.inputs['Base Color'].is_linked:continue
 source=shader.inputs['Base Color'].links[0].from_node
 if source.type!='TEX_IMAGE' or not source.image:continue
 image=source.image;pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels)
 rgba=pixels.reshape(-1,4);rgb=rgba[:,:3]
 mask=(rgb[:,0]>.18)&(rgb[:,0]>rgb[:,1]*1.8)&(rgb[:,0]>rgb[:,2]*1.8)
 emission=rgba.copy();emission[:,:3]*=mask[:,None];emission[:,3]=1
 output=bpy.data.images.new('Robot210 sensor emission',width=image.size[0],height=image.size[1],alpha=True)
 output.pixels.foreach_set(emission.ravel());output.filepath_raw=str(OUT/('sensors_'+str(index)+'.png'));output.file_format='PNG';output.save();output.pack()
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=output
 mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Emission Color'])
 shader.inputs['Emission Strength'].default_value=2.2
 shader.inputs['Metallic'].default_value=.55;shader.inputs['Roughness'].default_value=.58
 changes.append({'material':mat.name,'sensor_pixels':int(mask.sum()),'texture_pixels':len(rgba)})
assert changes,'No painted robot texture found'
assert len(rig.data.bones)==bones
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'robot_actions.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'robot_actions.glb'),export_format='GLB',use_selection=True,export_animation_mode='ACTIONS',export_force_sampling=True)
(OUT/'finish.json').write_text(json.dumps({'materials':changes,'retained_bones':bones,'scope':'source geometry, UVs, painted albedo, cannon sockets and motions retained; emission aligned to existing red sensor pixels'},indent=2))
print('ROBOT210_READY',changes,flush=True)
