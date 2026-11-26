extends "res://combat169.gd"
## Isolated treatment staging; retained animation supplies the kneeling motion.
var treatment_ik: SkeletonIK3D
var medic_rig: Skeleton3D
var patient_rig: Skeleton3D
var patient_arm := -1
var wrist := -1
var contact_error := 0.0

func bone(rig: Skeleton3D, name_value: String) -> int:
	var index := rig.find_bone(name_value)
	if index < 0:index=rig.find_bone(name_value.replace(".","_"))
	assert(index>=0,name_value)
	return index

func _ready() -> void:
	super._ready()
	delivery_folder=ROOT+("contact173/" if "--contact-preview" in OS.get_cmdline_user_args() else "city174/" if "--city-details" in OS.get_cmdline_user_args() else "contact173_final/")
	DirAccess.make_dir_recursive_absolute(delivery_folder)
	medic_rig=actors[3].find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	patient_rig=actors[0].find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	wrist=bone(medic_rig,"DEF-hand.R")
	patient_arm=bone(patient_rig,"DEF-upper_arm.L")
	treatment_ik=SkeletonIK3D.new()
	treatment_ik.root_bone=medic_rig.get_bone_name(bone(medic_rig,"DEF-upper_arm.R"))
	treatment_ik.tip_bone=medic_rig.get_bone_name(wrist)
	treatment_ik.override_tip_basis=false
	treatment_ik.max_iterations=12
	medic_rig.add_child(treatment_ik)
	if "--contact-preview" in OS.get_cmdline_user_args():time_value=22

func _process(delta: float) -> void:
	super._process(delta)
	if treatment_ik==null:return
	if time_value>=20 and "--painted192" not in OS.get_cmdline_user_args():
		# Authored Death alone leaves this thin bot upright. Topple its real body,
		# then ground the transformed bounds; the wreck persists after the sparks.
		# A PSI impulse carries the wreck out from behind the crate during the fall.
		if "--fall181" in OS.get_cmdline_user_args():
			actors[2].position.z=-.2+1.25*smoothstep(20,21.1,time_value)
		actors[2].rotation.z=-PI*.5*smoothstep(20,21.1,time_value)
		var base_y := INF
		for mesh in actors[2].find_children("*","MeshInstance3D",true,false):
			var bounds: AABB=mesh.global_transform*mesh.get_aabb()
			base_y=minf(base_y,bounds.position.y)
		if is_finite(base_y):actors[2].position.y+=.025-base_y
	if time_value>=22:
		# Follow the real patient's arm, rather than a detached world-space marker.
		var target := patient_rig.global_transform*patient_rig.get_bone_global_pose(patient_arm)
		target.origin+=Vector3(0,-.09,0)
		treatment_ik.target=target
		treatment_ik.start(true)
		var hand := medic_rig.global_transform*medic_rig.get_bone_global_pose(wrist)
		contact_error=hand.origin.distance_to(target.origin)
	if "--contact-preview" in OS.get_cmdline_user_args():
		camera.position=Vector3(2.5,2.7,5)
		camera.look_at(Vector3(0,.65,1.6));camera.size=4.8

func capture() -> void:
	if "--contact-preview" not in OS.get_cmdline_user_args():
		super.capture();return
	if frame==75:
		get_viewport().get_texture().get_image().save_png(delivery_folder+"treatment.png")
		FileAccess.open(delivery_folder+"contact.json",FileAccess.WRITE).store_string(JSON.stringify({"wrist_target_distance_m":contact_error,"scope":"One medical staging pose, not full animation acceptance"}))
		print("TREATMENT173_CAPTURED distance=",contact_error)
		get_tree().quit()
