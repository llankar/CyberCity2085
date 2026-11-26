extends "res://painted192.gd"
## Actual cannon sockets drive both the pose and the shot origin.
var cannon_tip: Node3D
var cannon_axis: Node3D
var cannon_rig: Skeleton3D
var cannon_bone := -1
var cannon_aiming := false
var cannon_target := 0
func load_glb(relative: String,place: Vector3) -> Node3D:
	if relative=="security_opaque137/robot_actions.glb":relative="robot193/robot_actions.glb"
	return super.load_glb(relative,place)
func _ready() -> void:
	super._ready()
	delivery_folder=ROOT+"cannon193/";DirAccess.make_dir_recursive_absolute(delivery_folder)
	cannon_tip=actors[2].find_children("CannonMuzzle193","Node3D",true,false)[0]
	cannon_axis=actors[2].find_children("CannonAxis193","Node3D",true,false)[0]
	cannon_rig=actors[2].find_children("*","Skeleton3D",true,false)[0]
	cannon_bone=cannon_rig.find_bone("upper_arm.R")
	if cannon_bone<0:cannon_bone=cannon_rig.find_bone("upper_arm_R")
	assert(cannon_bone>=0)
	print("CANNON193_READY geometry sockets and carrying bone")
func update_sockets() -> void:
	cannon_rig.force_update_all_bone_transforms()
	for attachment in cannon_rig.find_children("*","BoneAttachment3D",true,false):attachment.on_skeleton_update()
func face(index: int,point: Vector3) -> void:
	super.face(index,point)
	if index!=2 or not cannon_aiming or cannon_tip==null:return
	update_sockets()
	var axis:=cannon_axis.global_position-cannon_tip.global_position;axis.y=0
	var desired:=point-cannon_tip.global_position;desired.y=0
	actors[2].rotate_y(axis.signed_angle_to(desired,Vector3.UP))
func aim_cannon() -> void:
	var target:=actors[cannon_target].position+Vector3(0,.65 if cannon_target==0 and played[0]=="CoverStudy" else 1.1,0)
	for iteration in 2:
		update_sockets()
		var axis:Vector3=(cannon_axis.global_position-cannon_tip.global_position).normalized()
		var desired:Vector3=(target-cannon_tip.global_position).normalized()
		var world_basis:=cannon_rig.global_basis*cannon_rig.get_bone_global_pose(cannon_bone).basis
		var delta:=Quaternion((world_basis.inverse()*axis).normalized(),(world_basis.inverse()*desired).normalized())
		cannon_rig.set_bone_pose_rotation(cannon_bone,cannon_rig.get_bone_pose_rotation(cannon_bone)*delta)
	update_sockets()
func muzzle_clearance(source: int) -> float:
	return 0.0 if source==2 else super.muzzle_clearance(source)
func muzzle_position(source: int) -> Vector3:
	if source!=2:return super.muzzle_position(source)
	aim_cannon()
	var desired:Vector3=actors[cannon_target].position+Vector3(0,.65 if played[0]=="CoverStudy" else 1.1,0)-cannon_tip.global_position
	var error:=rad_to_deg((cannon_axis.global_position-cannon_tip.global_position).angle_to(desired))
	FileAccess.open(delivery_folder+"cannon_shot.json",FileAccess.WRITE).store_string(JSON.stringify({"time":time_value,"muzzle":cannon_tip.global_position,"axis_error_degrees":error,"scope":"one actual shot; geometry sockets, not a whole-clip precision gate"}))
	print("CANNON193_SHOT axis_error_degrees=",error)
	return cannon_tip.global_position
func clip(index: int,name_value: String,loop := true) -> void:
	super.clip(index,"Idle" if index==2 and cannon_aiming and name_value=="Melee" else name_value,loop)
func fire(source: int,target_index: int) -> void:
	if source==2:cannon_aiming=true;cannon_target=target_index
	super.fire(source,target_index)
	cannon_aiming=false
func after_unit_animations(t: float) -> void:
	super.after_unit_animations(t)
	if t>=4.2 and t<5.4:
		cannon_aiming=true;face(2,actors[0].position);aim_cannon();cannon_aiming=false
func capture() -> void:
	super.capture()
	if OS.has_feature("movie") and frame in [145,146,147]:get_viewport().get_texture().get_image().save_png(delivery_folder+"cannon_%04d.png"%frame)
