"""Transfer licensed UAL global rotation deltas onto authored Einar FK controls.

The original rig still evaluates all mechanical/corrective relationships. This
is a retarget study, not automatic artistic acceptance or a weapon-grip solver.
"""
import math
from pathlib import Path
import bpy
from mathutils import Matrix


class UALMotion:
    def __init__(self,target,clip):
        library=Path('E:/CyberCity2085-3d-lab/sources/quaternius_ual_standard/animation_library.blend')
        with bpy.data.libraries.load(str(library),link=False) as (available,loaded):
            loaded.objects=['Armature']
        self.source=loaded.objects[0]
        bpy.context.scene.collection.objects.link(self.source)
        actions={track.name:strip.action for track in self.source.animation_data.nla_tracks for strip in track.strips}
        if clip not in actions: raise ValueError('Clip not in licensed free library: '+clip)
        for track in self.source.animation_data.nla_tracks: track.mute=True
        action=actions[clip]
        self.source.animation_data.action=action
        if action.slots: self.source.animation_data.action_slot=action.slots[0]
        self.first,self.last=action.frame_range
        self.duration=(self.last-self.first)/24.0
        self.target=target
        for key in ['ik_left_upperarm','ik_right_upperarm','ik_left_thigh','ik_right_thigh']:
            target.pose.bones['Properties'][key]=0.0
        target.update_tag(refresh={'OBJECT'}); bpy.context.view_layer.update()
        levels=[ [('MSTR-Spine_Torso','pelvis')], [('FK-Spine','spine_01')],
                 [('MSTR-Spine_Chest','spine_03')], [('FK-Neck','neck_01')], [('FK-Head','Head')],
                 [('FK-Shoulder.L','clavicle_l'),('FK-Shoulder.R','clavicle_r')],
                 [('FK-UpperArm.L','upperarm_l'),('FK-UpperArm.R','upperarm_r')],
                 [('FK-Forearm.L','lowerarm_l'),('FK-Forearm.R','lowerarm_r')],
                 [('FK-Wrist.L','hand_l'),('FK-Wrist.R','hand_r')],
                 [('FK-Thigh.L','thigh_l'),('FK-Thigh.R','thigh_r')],
                 [('FK-Knee.L','calf_l'),('FK-Knee.R','calf_r')],
                 [('FK-Foot.L','foot_l'),('FK-Foot.R','foot_r')],
                 [('FK-Toes.L','ball_l'),('FK-Toes.R','ball_r')] ]
        for joint in range(1,4):
            levels.append([(f'FK-Finger_{finger}{joint}.{side}',f'{source}_{joint:02d}_{side.lower()}')
                           for side in ['L','R'] for finger,source in
                           [('Thumb','thumb'),('Index','index'),('Middle','middle'),('Ring','ring'),('Pinky','pinky')]])
        self.unmapped=[(a,b) for level in levels for a,b in level if a not in target.pose.bones or b not in self.source.pose.bones]
        self.levels=[[(a,b) for a,b in level if a in target.pose.bones and b in self.source.pose.bones] for level in levels]
        self.rest={name:target.pose.bones[name].matrix.copy() for level in self.levels for name,other in level}
        self.basis={name:target.pose.bones[name].matrix_basis.copy() for name in self.rest}
        self.source_rest={other:(self.source.matrix_world @ self.source.data.bones[other].matrix_local)
                          for level in self.levels for name,other in level}
        self.scale=self.rest['MSTR-Spine_Torso'].translation.z/self.source_rest['pelvis'].translation.z
        self.max_rotation_error=0.0
        self.control_errors={}

    def apply_fraction(self,fraction):
        sample=self.first+(self.last-self.first)*fraction
        bpy.context.scene.frame_set(math.floor(sample),subframe=sample-math.floor(sample))
        for name,basis in self.basis.items(): self.target.pose.bones[name].matrix_basis=basis
        self.target.update_tag(refresh={'OBJECT'}); bpy.context.view_layer.update()
        for level in self.levels:
            for name,source_name in level:
                source_matrix=self.source.matrix_world @ self.source.pose.bones[source_name].matrix
                if name=='FK-Spine':
                    # This authored control is limited and receives chest rotation.
                    # Feed only source lumbar motion relative to its pelvis.
                    parent=self.source.pose.bones[source_name].parent
                    current_local=parent.matrix.inverted() @ self.source.pose.bones[source_name].matrix
                    parent_rest=self.source.matrix_world @ parent.bone.matrix_local
                    rest_local=parent_rest.inverted() @ self.source_rest[source_name]
                    local_delta=current_local.to_quaternion() @ rest_local.to_quaternion().inverted()
                    world_delta=parent_rest.to_quaternion() @ local_delta @ parent_rest.to_quaternion().inverted()
                    target_delta=self.rest[name].to_quaternion().inverted() @ world_delta @ self.rest[name].to_quaternion()
                    self.target.pose.bones[name].matrix_basis=self.basis[name] @ target_delta.to_matrix().to_4x4()
                    continue
                delta=source_matrix.to_quaternion() @ self.source_rest[source_name].to_quaternion().inverted()
                desired=(delta @ self.rest[name].to_quaternion()).to_matrix().to_4x4()
                pose=self.target.pose.bones[name]
                desired.translation=pose.matrix.translation
                if name=='MSTR-Spine_Torso':
                    desired.translation=self.rest[name].translation+(source_matrix.translation-self.source_rest[source_name].translation)*self.scale
                armature_constraint=any(c.type=='ARMATURE' and not c.mute and c.influence>0 for c in pose.constraints)
                if armature_constraint:
                    arguments={} if pose.parent is None else {'parent_matrix':pose.parent.matrix,'parent_matrix_local':pose.parent.bone.matrix_local}
                    unconstrained=pose.bone.convert_local_to_pose(pose.matrix_basis,pose.bone.matrix_local,**arguments)
                    effect=pose.matrix @ unconstrained.inverted()
                    pose.matrix_basis=pose.bone.convert_local_to_pose(effect.inverted() @ desired,pose.bone.matrix_local,invert=True,**arguments)
                else: pose.matrix=desired
            self.target.update_tag(refresh={'OBJECT'}); bpy.context.view_layer.update()
        for level in self.levels:
            for name,source_name in level:
                if name=='FK-Spine': continue
                source_matrix=self.source.matrix_world @ self.source.pose.bones[source_name].matrix
                wanted=source_matrix.to_quaternion() @ self.source_rest[source_name].to_quaternion().inverted() @ self.rest[name].to_quaternion()
                angle=self.target.pose.bones[name].matrix.to_quaternion().rotation_difference(wanted).angle
                error=min(angle,abs(math.tau-angle))
                self.max_rotation_error=max(self.max_rotation_error,error)
                self.control_errors[name]=max(self.control_errors.get(name,0),error)

    def report(self):
        return {'author':'Quaternius','license':'CC0 1.0','duration_s':self.duration,
                'mapped_controls':[list(pair) for level in self.levels for pair in level],
                'unmapped_controls':[list(pair) for pair in self.unmapped],
                'pelvis_translation_scale':self.scale,'max_control_rotation_error_radians':self.max_rotation_error,
                'control_rotation_errors_radians':self.control_errors,
                'constrained_local_controls':['FK-Spine'],
                'limitations':['Global delta retarget; no automatic grip/foot-contact correction',
                               'Mechanical hand has four digits; missing ring control intentionally skipped']}
