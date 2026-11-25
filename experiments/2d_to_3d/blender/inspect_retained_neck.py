"""Render an explicit neck-skin selection diagnostic before any destructive edit."""
import json
import hashlib
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'neck_selection128';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'rook_hair127/human.blend'),use_scripts=False)
scene=bpy.context.scene;body=bpy.data.objects['char1']
rig=next(o for o in scene.objects if o.type=='ARMATURE');rig.data.pose_position='REST';bpy.context.view_layer.update()
image=next(n.image for n in body.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.name.startswith('RookBodyBaseColor'))
width,height=image.size;pixels=np.empty(width*height*4,dtype=np.float32);image.pixels.foreach_get(pixels);pixels=pixels.reshape(height,width,4)
material=bpy.data.materials.new('SELECTION_DIAGNOSTIC_ONLY');material.use_nodes=True
tree=material.node_tree;output=tree.nodes['Material Output'];emission=tree.nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value=(1,0,1,1);tree.links.new(emission.outputs[0],output.inputs['Surface'])
body.data.materials.append(material);selected=[];candidates=[]
for face in body.data.polygons:
    coords=[body.matrix_world@body.data.vertices[i].co for i in face.vertices]
    center=sum(coords,Vector())/len(coords)
    if not(1.42<center.z<1.58 and abs(center.x)<.10 and center.y<.10):continue
    uv=sum((body.data.uv_layers.active.data[i].uv for i in face.loop_indices),Vector((0,0)))/len(face.loop_indices)
    r,g,b=pixels[int(uv.y*height)%height,int(uv.x*width)%width,:3]
    skin=r>.3 and g>.12 and b>.07 and r>g*1.15 and b<r*.9
    record={'face':face.index,'center':list(center),'minimum_z':min(p.z for p in coords),'maximum_z':max(p.z for p in coords),'rgb':[float(r),float(g),float(b)],'skin':bool(skin)}
    candidates.append(record)
    if skin:
        selected.append(face.index);face.material_index=len(body.data.materials)-1
helpers={b.custom_shape for b in rig.pose.bones if b.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(out/'diagnostic.glb'),export_format='GLB',use_selection=True,export_animations=False)
(out/'selection.json').write_text(json.dumps({'source_glb_sha256':hashlib.sha256((root/'rook_hair127/human.glb').read_bytes()).hexdigest(),'selected':selected,'candidates':candidates,'scope':'Magenta skin mask diagnostic only; no final material or model'},indent=2))
print('RETAINED_NECK_SELECTION_READY',len(selected),len(candidates),flush=True)
