"""Neutral geometry review of Blender Studio Vincent CC BY source, no rig scripts."""
import sys
from pathlib import Path
import bpy
from mathutils import Vector

output=Path(sys.argv[sys.argv.index('--')+1]).resolve()
if output.drive.upper()!='E:':
    raise ValueError('Keep review on E:')
output.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/sources/blender_studio_vincent/vincent_v1.blend',use_scripts=False)
scene=bpy.context.scene
# Use rest geometry for the first review: old face drivers are not validated.
for rig in [o for o in bpy.data.objects if o.type=='ARMATURE']:
    rig.data.pose_position='REST'
for obj in bpy.data.objects:
    if obj.type=='MESH':
        obj.hide_render=not (obj.name.startswith('GEO-') and 'UV_copy' not in obj.name)
    if obj.type in {'LIGHT','CAMERA'}:
        obj.hide_render=True
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=900
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
scene.world=bpy.data.worlds.new('NeutralReview')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.18,.18,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
for location,energy in [((3,-4,5),600),((-3,-1,4),350)]:
    bpy.ops.object.light_add(type='AREA',location=location)
    bpy.context.object.data.energy=energy
    bpy.context.object.data.size=4
bpy.ops.object.camera_add()
camera=bpy.context.object
camera.data.type='ORTHO'
camera.data.ortho_scale=2.1
scene.camera=camera
for label,location in [('front',(0,-5,.8)),('side',(5,0,.8)),('back',(0,5,.8))]:
    camera.location=location
    camera.rotation_euler=(Vector((0,0,.8))-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(output/f'vincent_{label}.png')
    bpy.ops.render.render(write_still=True)
print('VINCENT_NEUTRAL_REVIEW_RENDERED rest_only_no_rig_acceptance')
