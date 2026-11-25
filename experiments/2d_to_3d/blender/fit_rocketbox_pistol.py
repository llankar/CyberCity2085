"""Fit the existing CC0 prop from actual curled-finger landmarks, not primitives."""
import json
import sys
import shutil
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from grip_geometry import circle_center,grip_frame
from glb_document import Glb

base=Path('E:/CyberCity2085-3d-lab/generated/phase2')
root=base/'rocketbox_military03/motion01'
out=root/'pistol_fit01'; out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'human_motion.blend'),use_scripts=False)
rig=bpy.data.objects['Bip01']; scene=bpy.context.scene
for track in rig.animation_data.nla_tracks: track.mute=track.name!='Pistol_Shoot'
scene.frame_set(9); bpy.context.view_layer.update()
def position(name): return rig.matrix_world @ rig.pose.bones[name].matrix.translation
centers=[circle_center([list(position('Bip01 R Finger'+str(digit)+suffix)) for suffix in ['', '1','2']]) for digit in [2,3,4]]
grip,basis=grip_frame(centers,position('Bip01 R Forearm'),position('Bip01 R Hand'))
anchor=Vector((0,-.012,.052))
placement=Matrix(basis.tolist()).to_4x4(); placement.translation=Vector(grip)-placement.to_3x3()@anchor
relative=(rig.matrix_world @ rig.pose.bones['Bip01 R Hand'].matrix).inverted() @ placement
conversion=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
relative_yup=conversion @ relative @ conversion.inverted()
placement_yup=conversion @ placement @ conversion.inverted()
with bpy.data.libraries.load(str(base/'firewarden_pistol01/pistol.blend'),link=False) as (available,loaded):
    loaded.objects=[name for name in available.objects if name in {'Pistol','trigger','barrel','hammer','magazine (loaded)','9mm.001','9mm','slide','night sights'}]
props=list(loaded.objects)
for prop in props: scene.collection.objects.link(prop)
bpy.context.view_layer.update()
reference=[]
for sample in range(9):
    frame=19*sample/8; scene.frame_set(int(frame),subframe=frame-int(frame)); bpy.context.view_layer.update()
    current=rig.matrix_world @ rig.pose.bones['Bip01 R Hand'].matrix @ relative
    points={}
    for prop in props:
        points[prop.name]=[list(current @ prop.matrix_world @ v.co) for v in prop.data.vertices]
    reference.append({'time_s':frame/30,'parts':points})
metadata={'bone':'Bip01 R Hand','relative_yup':[list(row) for row in relative_yup],
    'world_placement_yup':[list(row) for row in placement_yup],'reference_time_s':9/30,
    'grip_world':list(grip),'finger_circle_centers':[list(c) for c in centers],
    'source_prop':'FireWarden Lowpoly Pistol, CC0','source_url':'https://opengameart.org/content/lowpoly-pistol',
    'limitations':['Circle centers use bone landmarks, not a contact solver','Trigger and support-hand contact need visual review','Not final Rook art']}
(out/'fit_report.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
(out/'weapon_surface_reference.json').write_text(json.dumps(reference),encoding='utf-8')
# Keep a genuine editable/portable equipped source, not only runtime placement.
scene.frame_set(9); bpy.context.view_layer.update()
bind=(rig.matrix_world @ rig.data.bones['Bip01 R Hand'].matrix_local) @ relative
graph=bpy.context.evaluated_depsgraph_get(); equipped=[]
for prop in props:
    geometry=bpy.data.meshes.new_from_object(prop.evaluated_get(graph),depsgraph=graph)
    geometry.transform(bind @ prop.matrix_world)
    obj=bpy.data.objects.new('EquippedPistol_'+prop.name,geometry); scene.collection.objects.link(obj)
    obj.parent=rig; obj.matrix_world=Matrix.Identity(4)
    group=obj.vertex_groups.new(name='Bip01 R Hand'); group.add(list(range(len(geometry.vertices))),1,'REPLACE')
    modifier=obj.modifiers.new('MeasuredWristBinding','ARMATURE'); modifier.object=rig
    equipped.append(obj)
for prop in props: scene.collection.objects.unlink(prop)
selection=[rig,*equipped,*[obj for obj in scene.objects if obj.type=='MESH' and obj.name=='sm004_hipoly_81_bones']]
assert len(selection)==11
for obj in scene.objects: obj.select_set(obj in selection)
bpy.context.view_layer.objects.active=rig
scene.frame_start=0; scene.frame_end=19; scene.name='Pistol_Shoot'
bpy.data.texts.new('WEAPON_SOURCE_CC0').write('FireWarden Lowpoly Pistol; CC0 1.0\nhttps://opengameart.org/content/lowpoly-pistol\nMeasured wrist fit is experimental, not final contact acceptance.')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human_pistol.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'human_pistol.glb'),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='SCENE',export_frame_range=True,
    export_anim_scene_split_object=False,export_anim_single_armature=False,export_force_sampling=True,
    export_try_sparse_sk=True,export_copyright='Microsoft Rocketbox MIT; Quaternius UAL CC0; FireWarden Pistol CC0')
portable=Glb(out/'human_pistol.glb')
portable.doc['asset'].setdefault('extras',{}).update({'source_license':'MIT',
    'source_commit':'0943055db6ec570bcef9f2c8b41c9e5467c808f9',
    'license_notice':(root.parent/'LICENSE.md').read_text(),'motion_license':'CC0 1.0',
    'weapon_license':'CC0 1.0','weapon_source':metadata['source_url'],'fit_artistic_acceptance':False})
portable.save(out/'human_pistol.glb')
shutil.copyfile(root.parent/'LICENSE.md',out/'LICENSE.md')
print('ROCKETBOX_MEASURED_PISTOL_FIT',list(grip),len(props),flush=True)
