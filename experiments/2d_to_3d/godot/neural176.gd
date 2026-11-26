extends "res://contact173.gd"
## Scene-level comparison, preserving the existing cast and staged encounter.
var neural_rig: Skeleton3D
var neural_hand := -1
var neural_shots := 0

func _ready() -> void:
	super._ready()
	delivery_folder=ROOT+("vehicle178/" if "--vtol178" in OS.get_cmdline_user_args() else "neural177/" if "--weights177" in OS.get_cmdline_user_args() else "neural176/")
	DirAccess.make_dir_recursive_absolute(delivery_folder)
	var model:=actor(("rig177/" if "--weights177" in OS.get_cmdline_user_args() else "rig176/")+"human.glb",Vector3(-6,0,2.5))
	players[5].get_animation_library("").add_animation("Pistol_Shoot",players[5].get_animation("Shoot"))
	played.append("");health.append(100)
	var ring:=rings[0].duplicate() as MeshInstance3D;add_child(ring);rings.append(ring)
	var bar:=bars[0].duplicate() as MeshInstance3D;add_child(bar);bars.append(bar)
	neural_rig=model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	neural_hand=neural_rig.find_bone("hand_r");assert(neural_hand>=0)
	print("NEURAL176_READY six actors; actual neural mesh and existing wrist prop")

func muzzle_position(source: int) -> Vector3:
	if source!=5:return super.muzzle_position(source)
	neural_rig.force_update_all_bone_transforms()
	return (neural_rig.global_transform*neural_rig.get_bone_global_pose(neural_hand)).origin

func _process(delta: float) -> void:
	var t:=time_value
	super._process(delta)
	if actors.size()<6:return
	travel(5,Vector3(-6,0,2.5),Vector3(-3.8,0,2.5),2,4.3,"Walk",t)
	if t<2 or (t>=4.3 and t<8.8) or (t>=12 and t<21):clip(5,"Idle")
	if t>=8.8 and t<12:face(5,actors[4].position)
	if neural_shots==0 and t>=8.8:
		fire(5,4);neural_shots=1
	if neural_shots==1 and t>=10.8:
		fire(5,4);neural_shots=2
	if t>=21:
		travel(5,Vector3(-3.8,0,2.5),Vector3(-1.3,0,2.1),21,24,"Walk",t)
		if t>=24:clip(5,"Idle");face(5,actors[4].position)
	# Base animation advancement is shared; refresh markers after this path update.
	rings[5].position=actors[5].position+Vector3(0,.025,0)
	bars[5].position=actors[5].position+Vector3(0,2.05,0)
