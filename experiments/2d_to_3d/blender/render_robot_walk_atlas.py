"""Render an authored robot walk into eight-view transparent experimental atlas."""
import json
import math
import sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

output = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
if output.drive.upper() != 'E:':
    raise ValueError('Experimental atlas must remain on E:')
output.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/generated/phase2/george_tactical/george_tactical.blend')
scene=bpy.context.scene
rig=next(o for o in scene.objects if o.type=='ARMATURE')
for track in rig.animation_data.nla_tracks:
    track.mute=True
action=bpy.data.actions['Walk']
rig.animation_data.action=action
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=scene.render.resolution_y=128
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=True
scene.world=bpy.data.worlds.new('NeutralAtlasWorld')
scene.world.color=(.18,.18,.18)
for position,energy in [((4,-4,7),1100),((-4,3,5),800)]:
    bpy.ops.object.light_add(type='AREA',location=position)
    bpy.context.object.data.energy=energy
    bpy.context.object.data.size=5
bpy.ops.object.camera_add()
camera=bpy.context.object
camera.data.type='ORTHO'
camera.data.ortho_scale=3.6
scene.camera=camera
target=Vector((0,0,1.25))
sheet=np.zeros((4*128,8*128,4),dtype=np.float32)
rows=[]
first,last=action.frame_range
for direction in range(8):
    angle=direction*math.tau/8
    camera.location=target+Vector((math.cos(angle)*8,math.sin(angle)*8,5))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    indices=[]
    for sample in range(4):
        frame=first+(last-first)*sample/4
        scene.frame_set(int(frame),subframe=frame-int(frame))
        path=output/f'walk_d{direction}_f{sample}.png'
        scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        image=bpy.data.images.load(str(path),check_existing=False)
        pixels=np.array(image.pixels[:],dtype=np.float32).reshape(128,128,4)
        index=direction*4+sample
        x,y=index%8,index//8
        # Blender image pixel storage is bottom-up; manifest rows are top-down.
        sheet[(3-y)*128:(4-y)*128,x*128:(x+1)*128]=pixels
        bpy.data.images.remove(image)
        indices.append(index)
    rows.append(indices)
atlas=bpy.data.images.new('robot_walk_atlas',width=1024,height=512,alpha=True)
atlas.pixels.foreach_set(sheet.reshape(-1))
atlas.filepath_raw=str(output/'robot_walk_atlas.png')
atlas.file_format='PNG'
atlas.save()
manifest={'texture':'robot_walk_atlas.png','frame_size':[128,128],
          'animations':{'walk':{'rows':rows,'fps':4/(max(.001,(last-first)/scene.render.fps)), 'loop':True}},
          'camera_views':'Eight orbit viewpoints, mapping to production facing NOT VERIFIED',
          'source_action':'Walk','source':'Quaternius George, CC0',
          'status':'Experimental alternative pipeline proof, not production animation asset'}
(output/'robot_walk_atlas.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('ANIMATED_ATLAS_RENDERED directions=8 frames_per_direction=4 total=32')
