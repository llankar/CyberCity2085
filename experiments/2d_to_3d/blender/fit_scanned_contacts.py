"""Measured contact study on the existing candidate; never edit upstream files."""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from two_bone_ik import elbow_target

root = Path('E:/CyberCity2085-3d-lab/generated/phase2')
source = root/'scanned_armor_shoot01'
out = root/'scanned_armor_contact01'
out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human_actions.blend'), use_scripts=False)
scene = bpy.data.scenes['AuthoredGameActions']
bpy.context.window.scene = scene
rig = bpy.data.objects['AuthoredGameRig']
shoot = next(t for t in rig.animation_data.nla_tracks if t.name == 'Shoot')
for track in rig.animation_data.nla_tracks:
    track.mute = track != shoot
fit = json.loads((source/'pistol_fit01/fit_report.json').read_text())
relative = Matrix(fit['relative_blender'])
landmarks = json.loads((source/'grip_landmarks.json').read_text())
trigger = landmarks['pistol_parts']['EquippedPistol_trigger']
trigger_touch = Vector((trigger['max'][0]+.004, trigger['center'][1], trigger['center'][2]))
trigger_local = Matrix(fit['world_placement_blender']).inverted() @ trigger_touch
poses = []
for frame in range(0,17,2):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    poses.append({bone.name: bone.matrix.copy() for bone in rig.pose.bones})
rig.animation_data.nla_tracks.remove(shoot)
rig.animation_data.action = bpy.data.actions.new('Measured_Firing_Contact_Study')


def point(name, tail=False):
    bone = rig.pose.bones[name]
    return rig.matrix_world @ (bone.tail if tail else bone.head)


def ccd(chain, endpoint, target, tail=False):
    for _ in range(256):
        if (point(endpoint,tail)-target).length < .0005:
            break
        for name in chain:
            pivot = point(name)
            current = point(endpoint,tail)-pivot
            desired = target-pivot
            if min(current.length,desired.length) < 1e-8:
                continue
            rotation = current.rotation_difference(desired)
            if rotation.angle > math.radians(20):
                rotation.angle = math.radians(20)
            bone = rig.pose.bones[name]
            world = rig.matrix_world @ bone.matrix
            world = Matrix.Translation(pivot) @ rotation.to_matrix().to_4x4() @ Matrix.Translation(-pivot) @ world
            bone.matrix = rig.matrix_world.inverted() @ world
            bpy.context.view_layer.update()
    return (point(endpoint,tail)-target).length


def rotate_joint(name, desired, endpoint):
    pivot = point(name)
    rotation = (point(endpoint)-pivot).rotation_difference(desired-pivot)
    bone = rig.pose.bones[name]
    world = rig.matrix_world @ bone.matrix
    bone.matrix = rig.matrix_world.inverted() @ Matrix.Translation(pivot) @ rotation.to_matrix().to_4x4() @ Matrix.Translation(-pivot) @ world
    bpy.context.view_layer.update()


def solve_arm(side,target):
    upper, lower, hand = ['upper_arm.'+side,'forearm.'+side,'hand.'+side]
    shoulder = point(upper)
    original_hand = rig.matrix_world @ rig.pose.bones[hand].matrix
    upper_length = (point(lower)-shoulder).length
    lower_length = (point(hand)-point(lower)).length
    elbow = Vector(elbow_target(shoulder,target,[0,0,-1],upper_length,lower_length))
    rotate_joint(upper,elbow,lower)
    rotate_joint(lower,target,hand)
    original_hand.translation = point(hand)
    rig.pose.bones[hand].matrix = rig.matrix_world.inverted() @ original_hand
    bpy.context.view_layer.update()
    return (point(hand)-target).length


errors = []
previous = {}
for frame, pose in zip(range(0,17,2), poses):
    scene.frame_set(frame)
    for bone in rig.pose.bones:
        args = dict(matrix=pose[bone.name],matrix_local=bone.bone.matrix_local,invert=True)
        if bone.parent:
            args.update(parent_matrix=pose[bone.parent.name],parent_matrix_local=bone.parent.bone.matrix_local)
        bone.matrix_basis = bone.bone.convert_local_to_pose(**args)
    bpy.context.view_layer.update()
    # Source firing arm is almost locked straight. Bend it to bring the weapon
    # 65mm closer; both hands can then reach without stretching either arm.
    nominal_prop = rig.matrix_world @ rig.pose.bones['hand.R'].matrix @ relative
    backward = nominal_prop.to_3x3().col[1].normalized()
    right_error = solve_arm('R',point('hand.R')+backward*.065)
    prop = rig.matrix_world @ rig.pose.bones['hand.R'].matrix @ relative
    target = prop @ trigger_local
    trigger_error = ccd(['finger_index.03.R','finger_index.02.R','finger_index.01.R'], 'finger_index.03.R', target, True)
    # Move the offhand palm towards the outside of the actual grip, retaining
    # its source orientation. This is a fit study, not a collision solver.
    hand = rig.pose.bones['hand.L']
    original_hand = rig.matrix_world @ hand.matrix
    palm = sum((point('finger_'+digit+'.01.L') for digit in ['index','middle','ring','pinky']), Vector())/4
    grip = prop @ Vector((0,-.012,.052))
    right = prop.to_3x3().col[0].normalized()
    up = prop.to_3x3().col[2].normalized()
    desired_palm = grip-right*.03-up*.01
    wrist_target = point('hand.L') + desired_palm-palm
    lengths_before = [(point('forearm.L')-point('upper_arm.L')).length,
                      (point('hand.L')-point('forearm.L')).length]
    target_distance = (wrist_target-point('upper_arm.L')).length
    wrist_error = solve_arm('L',wrist_target)
    measured_palm = sum((point('finger_'+digit+'.01.L') for digit in ['index','middle','ring','pinky']), Vector())/4
    lengths_after = [(point('forearm.L')-point('upper_arm.L')).length,
                     (point('hand.L')-point('forearm.L')).length]
    length_error = max(abs(a-b) for a,b in zip(lengths_before,lengths_after))
    assert length_error < .00001, ('Arm stretched',frame,length_error)
    errors.append({'frame':frame,'index_tip_to_trigger_target_m':trigger_error,
                   'wrist_target_error_m':wrist_error,'palm_target_error_m':(measured_palm-desired_palm).length,
                   'arm_segment_length_error_m':length_error,'target_distance_m':target_distance,
                   'arm_max_reach_m':sum(lengths_before),'right_wrist_target_error_m':right_error})
    for bone in rig.pose.bones:
        q = bone.rotation_quaternion.copy()
        if bone.name in previous and q.dot(previous[bone.name]) < 0:
            q.negate()
            bone.rotation_quaternion = q
        previous[bone.name] = q.copy()
        for path in ('location','rotation_quaternion','scale'):
            bone.keyframe_insert(path,frame=frame)
action = rig.animation_data.action
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for curve in bag.fcurves:
                for key in curve.keyframe_points:
                    key.interpolation = 'LINEAR'
track = rig.animation_data.nla_tracks.new()
track.name = 'Shoot'
track.strips.new('Shoot',0,action)
rig.animation_data.action = None
for track in rig.animation_data.nla_tracks:
    track.mute = False
for obj in scene.objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = rig
notice = (source/'CREDITS.txt').read_text()+'\nMeasured firing finger/offhand CCD fit study; no joint-limit, trigger pressure or mesh collision acceptance.\n'
bpy.ops.export_scene.gltf(filepath=str(out/'human_actions.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_keep_anim_armature=True,export_extras=True,export_copyright=notice)
references = {}
meshes = [obj for obj in scene.objects if obj.type == 'MESH']
assert len(meshes) == 18
for selected in rig.animation_data.nla_tracks:
    for other in rig.animation_data.nla_tracks:
        other.mute = other != selected
    duration = selected.strips[0].frame_end/120
    samples = []
    count = 17 if selected.name == 'Shoot' else 9
    for index in range(count):
        time = duration*index/(count-1)
        frame = time*120
        scene.frame_set(int(frame),subframe=frame-int(frame))
        bpy.context.view_layer.update()
        graph = bpy.context.evaluated_depsgraph_get()
        geometry = {}
        for obj in meshes:
            evaluated = obj.evaluated_get(graph)
            data = evaluated.to_mesh()
            geometry[obj.name] = [list(evaluated.matrix_world @ data.vertices[i].co) for i in range(0,len(data.vertices),max(1,len(data.vertices)//12))]
            evaluated.to_mesh_clear()
        samples.append({'time_s':time,'meshes':geometry})
    references[selected.name] = samples
(out/'source_surface_reference.json').write_text(json.dumps(references))
for track in rig.animation_data.nla_tracks:
    track.mute = track.name != 'Idle'
scene.frame_set(0)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human_actions.blend'))
(out/'contact_report.json').write_text(json.dumps({'samples':errors,'contact_art_accepted':False,'limitations':['Bone targets are not mesh-surface contact or anatomical joint-limit validation']},indent=2))
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
print('SCANNED_CONTACT_STUDY_EXPORTED',json.dumps(errors),flush=True)
