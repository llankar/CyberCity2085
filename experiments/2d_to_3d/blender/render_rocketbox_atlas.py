"""Eight-view/four-frame action sheets from the same licensed animated model."""
import json
import math
import sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).parent.parent))
from atlas_sampling import atlas_sample_frames

robot='--robot-bundle' in sys.argv
cyborg='--cyborg-fire-study' in sys.argv
assert not(robot and cyborg),'Choose one atlas source'
sample_count=int(next((a.split('=',1)[1] for a in sys.argv if a.startswith('--samples=')),'4'))
assert 2<=sample_count<=32,'Choose2..32 samples per direction'
root=Path('E:/CyberCity2085-3d-lab/generated/phase2')/('security_bundle01' if robot else ('cyborg_fire01' if cyborg else 'rocketbox_military03/motion01'))
source_file='robot_actions.blend' if robot else ('human.blend' if cyborg else 'human_motion.blend')
output=root/'atlas'; output.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/source_file),use_scripts=False)
scene=bpy.context.scene
rig=next(o for o in scene.objects if o.type=='ARMATURE') if cyborg else bpy.data.objects['SecurityGameRig' if robot else 'Bip01']
if robot:
    durations=json.loads((root/'bundle_report.json').read_text())['clips']
    details={clip:{'duration_s':duration,'frames':round(duration*30)+1} for clip,duration in durations.items()}
elif cyborg:
    details={track.name:{'duration_s':(track.strips[0].frame_end-track.strips[0].frame_start)/scene.render.fps,'frames':round(track.strips[0].frame_end-track.strips[0].frame_start)+1} for track in rig.animation_data.nla_tracks}
else:details=json.loads((root/'retarget_report.json').read_text())['clips']
requested=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--action=')),None)
if requested is not None and requested not in details:raise ValueError('Requested action is unavailable')
reference_height=1.949875712 if robot else 1.8503574
calibration_height=1.869130611 if robot else 1.8503574
if cyborg:reference_height=calibration_height=1.79992747306824
expected_reference_pixels=62.208*reference_height/calibration_height
owners=[*scene.objects,*[o.data.shape_keys for o in scene.objects if o.type=='MESH' and o.data.shape_keys]]
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
camera.data.ortho_scale=size*calibration_height*math.cos(elevation)/62.208
target=Vector((0,0,.9))
for clip,info in details.items():
    if requested is not None and clip!=requested:continue
    if robot:
        for owner in owners:
            if owner.animation_data:
                owner.animation_data.action=None
                for track in owner.animation_data.nla_tracks:track.mute=track.name!=clip
    else:
        for track in rig.animation_data.nla_tracks:track.mute=track.name!=clip
    loop=clip=='Idle' if robot else clip in {'Idle','Walk','CombatReadyStudy','walk','run'}
    first_frame=0.;last_frame=info['frames']-1
    if robot or cyborg:
        strip=next(t for t in rig.animation_data.nla_tracks if t.name==clip).strips[0]
        first_frame,last_frame=strip.frame_start,strip.frame_end
        assert abs((last_frame-first_frame)/scene.render.fps-info['duration_s'])<.00001
        for owner in (owners if robot else []):
            if owner.animation_data and owner.animation_data.nla_tracks:
                owner_strip=next(t for t in owner.animation_data.nla_tracks if t.name==clip).strips[0]
                assert abs(owner_strip.frame_start-first_frame)<.00001 and abs(owner_strip.frame_end-last_frame)<.00001
    sample_frames=atlas_sample_frames(first_frame,last_frame,loop=loop,count=sample_count)
    root_displacement=Vector((0,0,0))
    if robot:
        rig.location=Vector((0,0,0))
        if clip=='Walk':
            foot_object=bpy.data.objects['GEO-toes.L_Evaluated']
            endpoints=[]
            for frame in [first_frame,last_frame]:
                scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
                evaluated=foot_object.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
                endpoints.append(evaluated.matrix_world @ mesh.vertices[0].co);evaluated.to_mesh_clear()
            root_displacement=endpoints[1]-endpoints[0]
            assert (root_displacement-Vector((0,-.6,0))).length<.00001,('Unexpected authored forward travel',root_displacement)
    sheet=np.zeros((sample_count*size,8*size,4),dtype=np.float32); rows=[]; anchors=[]; heights=[]
    for direction in range(8):
        angle=direction*math.tau/8
        camera.location=target+Vector((8*math.cos(angle),8*math.sin(angle),8*math.tan(elevation)))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        bpy.context.view_layer.update()
        foot=world_to_camera_view(scene,camera,Vector((0,0,0)))
        head=world_to_camera_view(scene,camera,Vector((0,0,reference_height)))
        anchors.append([foot.x,1-foot.y]); heights.append(abs(head.y-foot.y)*size)
        assert abs(heights[-1]-expected_reference_pixels)<.001
        indices=[]
        for sample in range(sample_count):
            frame=sample_frames[sample]
            scene.frame_set(int(frame),subframe=frame-int(frame))
            if robot:rig.location=-root_displacement*(frame-first_frame)/(last_frame-first_frame)
            bpy.context.view_layer.update()
            path=output/f'{clip}_d{direction}_f{sample}.png'
            scene.render.filepath=str(path); bpy.ops.render.render(write_still=True)
            image=bpy.data.images.load(str(path),check_existing=False)
            pixels=np.array(image.pixels[:],dtype=np.float32).reshape(size,size,4)
            index=direction*sample_count+sample; x,y=index%8,index//8
            sheet[(sample_count-1-y)*size:(sample_count-y)*size,x*size:(x+1)*size]=pixels
            bpy.data.images.remove(image); indices.append(index)
        rows.append(indices)
    atlas=bpy.data.images.new(clip+'_atlas',width=8*size,height=sample_count*size,alpha=True)
    atlas.pixels.foreach_set(sheet.reshape(-1)); atlas.filepath_raw=str(output/(clip+'_atlas.png'))
    atlas.file_format='PNG'; atlas.save(); bpy.data.images.remove(atlas)
    (output/(clip+'_atlas.json')).write_text(json.dumps({'texture':clip+'_atlas.png','frame_size':[size,size],
        'animations':{clip.lower():{'rows':rows,'loop':loop,'fps':(sample_count if loop else sample_count-1)/info['duration_s']}},
        'anchors_by_orbit_view':anchors,'reference_height_px':heights,'elevation_radians':elevation,
        'source':'Security Bot, Blender Foundation CC BY4' if robot else ('Grab3D body CC0 + Unvanquished hand CC BY-SA3 + FireWarden pistol CC0; see CREDITS.txt' if cyborg else 'Microsoft Rocketbox MIT + Quaternius UAL CC0'),'status':'Experimental, not accepted final robot art' if robot else 'Experimental, not accepted Rook art',
        'source_strip_frames':[first_frame,last_frame],'sample_scene_frames':sample_frames,'sample_times_s':[(f-first_frame)/scene.render.fps for f in sample_frames],
        'reference_height_m':reference_height,'calibration_human_height_m':calibration_height,'calibration_human_pixels':62.208,
        'walk_root_motion_removed_m':root_displacement.length if robot else 0.,'walk_root_motion_removed_vector_m':list(root_displacement),'source_model_sha256':__import__('hashlib').sha256((root/source_file).read_bytes()).hexdigest(),
        'camera_views':'Eight orbit views; production facing correspondence NOT VERIFIED'},indent=2),encoding='utf-8')
    if cyborg:(output/'CREDITS.txt').write_text((root/'CREDITS.txt').read_text(),encoding='utf8')
    print('ROCKETBOX_ACTION_ATLAS_RENDERED',clip,8*sample_count,flush=True)
print('ACTION_ATLAS_RENDER_COMPLETE',requested or 'all',flush=True)
