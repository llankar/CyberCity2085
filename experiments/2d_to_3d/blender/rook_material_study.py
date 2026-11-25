"""Traditional DCC material adaptation of the real cyberpunk asset; no primitives."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from rook_material_regions import region

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'cyborg_actions01'
out=root/'rook_material01'
out.mkdir(exist_ok=True)
reference=Path(__file__).resolve().parents[3]/'assets/ui/portraits/agent_male_14.png'
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene
rig=next(o for o in scene.objects if o.type=='ARMATURE')
body=bpy.data.objects['char1']
geometry=[tuple(v.co) for v in body.data.vertices]
uvs=[tuple(v.uv) for v in body.data.uv_layers.active.data]
rig.data.pose_position='REST'
bpy.context.view_layer.update()
original=body.data.materials[0]
shader=next(node for node in original.node_tree.nodes if node.type=='BSDF_PRINCIPLED')
texture=shader.inputs['Base Color'].links[0].from_node
assert texture.type=='TEX_IMAGE'
image=texture.image
width,height=image.size
pixels=np.empty(width*height*4,dtype=np.float32)
image.pixels.foreach_get(pixels)
pixels=pixels.reshape(height,width,4)
hair=original.copy();hair.name='RookCopperHair'
jacket=original.copy();jacket.name='RookFieldJacket'
body.data.materials.append(hair);body.data.materials.append(jacket)
counts={'hair':0,'jacket':0}
for face in body.data.polygons:
    point=sum((body.matrix_world@body.data.vertices[i].co for i in face.vertices),Vector())/len(face.vertices)
    uv=sum((body.data.uv_layers.active.data[i].uv for i in face.loop_indices),Vector((0,0)))/len(face.loop_indices)
    color=pixels[int(uv.y*height)%height,int(uv.x*width)%width,:3]
    selected=region(point,color)
    face.material_index=selected
    if selected:counts['hair' if selected==1 else 'jacket']+=1
assert counts['hair']>30 and counts['jacket']>500,counts
palettes={hair:[(0,(.012,.002,.0005,1)),(.03,(.14,.018,.002,1)),(.12,(.52,.10,.008,1)),(.35,(1.,.38,.035,1)),(1.,(1.,.72,.25,1))],
          jacket:[(0,(.001,.004,.002,1)),(.04,(.009,.045,.022,1)),(.16,(.035,.18,.075,1)),(.5,(.17,.45,.22,1)),(1.,(.5,.75,.45,1))]}
baked=bpy.data.images.new('RookBodyBaseColor',width=width,height=height,alpha=True)
baked.colorspace_settings.name='sRGB'
restore=[]
for material in [original,hair,jacket]:
    tree=material.node_tree
    bsdf=next(node for node in tree.nodes if node.type=='BSDF_PRINCIPLED')
    base_socket=bsdf.inputs['Base Color'].links[0].from_socket
    if material in palettes:
        value=tree.nodes.new('ShaderNodeRGBToBW');tree.links.new(base_socket,value.inputs[0])
        ramp=tree.nodes.new('ShaderNodeValToRGB')
        for old in list(ramp.color_ramp.elements)[1:]:ramp.color_ramp.elements.remove(old)
        for index,(position,color) in enumerate(palettes[material]):
            entry=ramp.color_ramp.elements[0] if index==0 else ramp.color_ramp.elements.new(position)
            entry.position=position;entry.color=color
        tree.links.new(value.outputs[0],ramp.inputs[0]);base_socket=ramp.outputs['Color']
    output=next(node for node in tree.nodes if node.type=='OUTPUT_MATERIAL' and node.is_active_output)
    emission=tree.nodes.new('ShaderNodeEmission');tree.links.new(base_socket,emission.inputs['Color'])
    tree.links.new(emission.outputs[0],output.inputs['Surface'])
    target=tree.nodes.new('ShaderNodeTexImage');target.image=baked
    tree.nodes.active=target
    restore.append((tree,bsdf,output,emission,target))
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1
for obj in scene.objects:obj.select_set(obj==body)
bpy.context.view_layer.objects.active=body
bpy.ops.object.bake(type='EMIT',margin=8,use_clear=True)
baked.filepath_raw=str(out/'rook_body_basecolor.png');baked.file_format='PNG';baked.save()
for tree,bsdf,output,emission,target in restore:
    tree.links.new(bsdf.outputs[0],output.inputs['Surface'])
    tree.links.new(target.outputs['Color'],bsdf.inputs['Base Color'])
    tree.nodes.remove(emission)
assert geometry==[tuple(v.co) for v in body.data.vertices]
assert uvs==[tuple(v.uv) for v in body.data.uv_layers.active.data]
rig.data.pose_position='POSE'
for track in rig.animation_data.nla_tracks:track.mute=track.name!='CombatReadyStudy'
scene.frame_set(0);bpy.context.view_layer.update()
helpers={bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
for obj in scene.objects:obj.select_set(obj==rig or (obj.type=='MESH' and obj not in helpers))
bpy.context.view_layer.objects.active=rig
notice=(source/'CREDITS.txt').read_text()+'\nRook material study: existing game portrait agent_male_14.png used as art reference; copper hair and green jacket baked through Blender emission. Original mesh/UV/normal/roughness maps retained. No face/groom likeness or final art approval.\n'
credits=bpy.data.texts.new('ROOK_MATERIAL_STUDY');credits.write(notice);credits.use_fake_user=True
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_armature=True,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
shutil.copyfile(source/'native_reference.json',out/'native_reference.json')
(out/'material_report.json').write_text(json.dumps({'assigned_faces':counts,'geometry_unchanged':True,'uvs_unchanged':True,'portrait_reference':str(reference),'portrait_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),'source_glb_sha256':hashlib.sha256((source/'human.glb').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'limitations':['Geometric/color material masks need visual review','No facial likeness or source hair geometry adaptation','No final Rook art acceptance']},indent=2),encoding='utf8')
print('ROOK_MATERIAL_STUDY_EXPORTED',counts,flush=True)
