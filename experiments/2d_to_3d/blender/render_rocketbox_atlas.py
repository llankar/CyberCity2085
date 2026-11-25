"""Eight-view/four-frame action sheets from the same licensed animated model."""
import json
import math
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

root=Path('E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03/motion01')
output=root/'atlas'; output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'human_motion.blend'),use_scripts=False)
scene=bpy.context.scene; rig=bpy.data.objects['Bip01']
details=json.loads((root/'retarget_report.json').read_text())['clips']
scene.render.engine='BLENDER_EEVEE_NEXT'
size=192 # wider transparent padding for the fallen body; pixel density unchanged
scene.render.resolution_x=scene.render.resolution_y=size
scene.render.resolution_percentage=100
scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'
scene.world=bpy.data.worlds.new('NeutralAtlas'); scene.world.color=(.18,.18,.18)
for location,power in [((4,-4,7),1100),((-4,3,5),800)]:
    bpy.ops.object.light_add(type='AREA',location=location)
    bpy.context.object.data.energy=power; bpy.context.object.data.size=5
bpy.ops.object.camera_add(); camera=bpy.context.object; scene.camera=camera
camera.data.type='ORTHO'; elevation=.6
camera.data.ortho_scale=size*1.8503574*math.cos(elevation)/62.208
target=Vector((0,0,.9))
for clip,info in details.items():
    for track in rig.animation_data.nla_tracks: track.mute=track.name!=clip
    loop=clip in {'Idle','Walk'}
    sheet=np.zeros((4*size,8*size,4),dtype=np.float32); rows=[]; anchors=[]; heights=[]
    for direction in range(8):
        angle=direction*math.tau/8
        camera.location=target+Vector((8*math.cos(angle),8*math.sin(angle),8*math.tan(elevation)))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        bpy.context.view_layer.update()
        foot=world_to_camera_view(scene,camera,Vector((0,0,0)))
        head=world_to_camera_view(scene,camera,Vector((0,0,1.8503574)))
        anchors.append([foot.x,1-foot.y]); heights.append(abs(head.y-foot.y)*size)
        assert abs(heights[-1]-62.208)<.001
        indices=[]
        for sample in range(4):
            frame=(info['frames']-1)*sample/(4 if loop else 3)
            scene.frame_set(int(frame),subframe=frame-int(frame))
            path=output/f'{clip}_d{direction}_f{sample}.png'
            scene.render.filepath=str(path); bpy.ops.render.render(write_still=True)
            image=bpy.data.images.load(str(path),check_existing=False)
            pixels=np.array(image.pixels[:],dtype=np.float32).reshape(size,size,4)
            index=direction*4+sample; x,y=index%8,index//8
            sheet[(3-y)*size:(4-y)*size,x*size:(x+1)*size]=pixels
            bpy.data.images.remove(image); indices.append(index)
        rows.append(indices)
    atlas=bpy.data.images.new(clip+'_atlas',width=8*size,height=4*size,alpha=True)
    atlas.pixels.foreach_set(sheet.reshape(-1)); atlas.filepath_raw=str(output/(clip+'_atlas.png'))
    atlas.file_format='PNG'; atlas.save(); bpy.data.images.remove(atlas)
    (output/(clip+'_atlas.json')).write_text(json.dumps({'texture':clip+'_atlas.png','frame_size':[size,size],
        'animations':{clip.lower():{'rows':rows,'loop':loop,'fps':(4 if loop else 3)/info['duration_s']}},
        'anchors_by_orbit_view':anchors,'reference_height_px':heights,'elevation_radians':elevation,
        'source':'Microsoft Rocketbox MIT + Quaternius UAL CC0','status':'Experimental, not accepted Rook art',
        'camera_views':'Eight orbit views; production facing correspondence NOT VERIFIED'},indent=2),encoding='utf-8')
    print('ROCKETBOX_ACTION_ATLAS_RENDERED',clip,32,flush=True)
print('ROCKETBOX_FIVE_ATLASES_RENDERED',160,flush=True)
