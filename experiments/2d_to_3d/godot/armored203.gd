extends "res://medic201.gd"
## Reuse the existing authored armored body, motions and bound pistol.
func load_glb(relative: String,place: Vector3) -> Node3D:
 if not (relative.begins_with("unvanquished_") or relative.begins_with("armored203/")):return super.load_glb(relative,place)
 var doc:=GLTFDocument.new();var state:=GLTFState.new()
 assert(doc.append_from_file(ROOT+relative,state)==OK)
 # Retain static pose channels so imported idle/fire clips reset each other.
 var model:=doc.generate_scene(state,60,false,false) as Node3D
 add_child(model);model.position=place
 return model
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"armored203/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 var old:=actors[4]
 var replacement:=load_glb("armored203/armored_actions.glb",old.position)
 var player:=replacement.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
 for action in ["Idle","Walk","Run","Death","Crouch","Attack","Pistol_Attack_Study"]:assert(player.has_animation(action),action)
 player.get_animation_library("").add_animation("Pistol_Shoot",player.get_animation("Pistol_Attack_Study"))
 player.get_animation_library("").add_animation("Death01",player.get_animation("Death"))
 player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
 actors[4]=replacement;players[4]=player;played[4]=""
 old.visible=false;old.queue_free()
 print("ARMORED203_READY existing armored model, source motions and bound pistol")
func face(index: int,point: Vector3) -> void:
 super.face(index,point)
 # Anatomical audit of this source records forward -Z, unlike the +Z cast.
 if index==4:actors[4].rotate_y(PI)
func muzzle_position(source: int) -> Vector3:
 if source!=4:return super.muzzle_position(source)
 players[4].seek(1.0/15.0,true)
 var rig:=actors[4].find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
 rig.force_update_all_bone_transforms()
 return (rig.global_transform*rig.get_bone_global_pose(bone(rig,"hand.R"))).origin
func _process(delta: float) -> void:
 var t:=time_value
 super._process(delta)
 if actors.size()>=6 and (t<6 or (t>=9 and t<11.7) or t>=12.25):face(4,actors[0].position)
