"""Adapt genuine authored jacket: remove modular neck guard, retain real inner collar."""
import hashlib,json,sys
from pathlib import Path
import bpy,bmesh
sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb
from game_materials import restore

root=Path('E:/CyberCity2085-3d-lab/generated/phase2');source=root/'amjviz_grip149'
out=root/'amjviz_wardrobe150';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human_actions.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
body=max((o for o in scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
slot=next(i for i,m in enumerate(body.data.materials) if m.name=='Neck')
def protected():
    values=[]
    for face in body.data.polygons:
        if face.material_index==slot:continue
        values.append((face.material_index,tuple(tuple(body.data.vertices[i].co) for i in face.vertices),
                       tuple(tuple(body.data.uv_layers.active.data[i].uv) for i in face.loop_indices)))
    return hashlib.sha256(repr(values).encode()).hexdigest()
before=protected();removed=sum(f.material_index==slot for f in body.data.polygons)
assert removed==364,'Reviewed modular neck guard changed'
bm=bmesh.new();bm.from_mesh(body.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index==slot],context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bm.to_mesh(body.data);bm.free();assert protected()==before
# Real source albedo/normal/roughness maps remain. Tint and metalness are PBR
# material parameters, not a painted replacement model or a geometry substitute.
tint=(.12,.55,.32,1.);metallic=.05
material=next(m for m in body.data.materials if m.name=='Jacket')
nodes=material.node_tree.nodes;links=material.node_tree.links
shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
color=shader.inputs['Base Color']
if color.is_linked:
    original=color.links[0].from_socket
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1.
    mix.inputs[2].default_value=tint;links.new(original,mix.inputs[1]);links.new(mix.outputs[0],color)
else:color.default_value=tuple(a*b for a,b in zip(color.default_value,tint))
metal=shader.inputs['Metallic']
if metal.is_linked:
    original=metal.links[0].from_socket
    multiply=nodes.new('ShaderNodeMath');multiply.operation='MULTIPLY';multiply.inputs[1].default_value=metallic
    links.new(original,multiply.inputs[0]);links.new(multiply.outputs[0],metal)
else:metal.default_value*=metallic
for track in rig.animation_data.nla_tracks:track.mute=track.name!='Hard stand'
rig.animation_data.action=None;scene.frame_set(0);bpy.context.view_layer.update()
notice=(source/'CREDITS.txt').read_text()+ '\n150 derivative:364face modular neck guard removed; genuine inner jacket collar/body/UV/skin retained, original jacket PBR tinted dark green and metalness scaled. Private unaccepted Rook wardrobe study.\n'
bpy.data.texts.new('WARDROBE150_CHANGES').write(notice)
meshes=[o for o in scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
for obj in scene.objects:obj.select_set(obj==rig or obj in meshes)
bpy.context.view_layer.objects.active=rig
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'human_actions.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human_raw.glb'),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_frame_range=False,
    export_rest_position_armature=True,export_optimize_animation_size=False,
    export_optimize_animation_keep_anim_armature=True,export_optimize_animation_keep_anim_object=True,
    export_all_influences=True,export_copyright=notice)
compiled=Glb(out/'human_raw.glb');restore(compiled,Glb(source/'human_actions.glb'))
jacket=next(m for m in compiled.doc['materials'] if m.get('name')=='Jacket')
pbr=jacket['pbrMetallicRoughness'];pbr['baseColorFactor']=list(tint);pbr['metallicFactor']=metallic
compiled.save(out/'human_actions.glb');(out/'CREDITS.txt').write_text(notice)
(out/'wardrobe_fit.json').write_text(json.dumps({'removed_neck_guard_faces':removed,
    'protected_other_faces_geometry_uv_sha256':before,'retained_other_geometry_uv_exact':protected()==before,
    'jacket_base_color_factor':tint,'jacket_metallic_factor':metallic,
    'glb_sha256':hashlib.sha256((out/'human_actions.glb').read_bytes()).hexdigest(),
    'scope':'Real modular accessory removal/PBR adaptation; complete neck/cloth/contact multiview review and native motion checks required'},indent=2))
print('AUTHORED_WARDROBE150_EXPORTED',flush=True)
