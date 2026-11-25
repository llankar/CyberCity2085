extends RefCounted
## Actual licensed prop, mounted with a measured source-wrist local transform.
static func attach(model: Node3D,scanned_shoot: bool=false,contact_study: bool=false) -> Node3D:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/"
	var folder := "scanned_armor_shoot01/" if scanned_shoot else "rocketbox_military03/motion01/"
	if contact_study:folder="scanned_armor_contact01/"
	var metadata = JSON.parse_string(FileAccess.get_file_as_string(root+folder+"pistol_fit01/fit_report.json"))
	assert(metadata is Dictionary)
	var skeleton := model.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var bone := skeleton.find_bone(metadata.bone)
	if bone<0:bone=skeleton.find_bone(str(metadata.bone).replace(".","_"))
	assert(bone >= 0)
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	assert(doc.append_from_file(root+"firewarden_pistol01/pistol.glb",state) == OK)
	var prop := doc.generate_scene(state) as Node3D
	var rows: Array = metadata.world_placement_yup
	var basis := Basis(Vector3(rows[0][0],rows[1][0],rows[2][0]),Vector3(rows[0][1],rows[1][1],rows[2][1]),Vector3(rows[0][2],rows[1][2],rows[2][2]))
	var placement := Transform3D(basis,Vector3(rows[0][3],rows[1][3],rows[2][3]))
	# GLTFDocument may choose different bone-local axes from Blender's FBX rig.
	# Calibrate the local mount in the actual imported reference pose, then keep
	# that single constant transform for every subsequent frame.
	var player := model.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var previous := player.current_animation
	var previous_time := 0.0 if previous.is_empty() else player.current_animation_position
	player.play("Shoot" if scanned_shoot else "Pistol_Shoot"); player.seek(float(metadata.reference_time_s),true)
	skeleton.force_update_all_bone_transforms()
	var local_mount := (skeleton.global_transform*skeleton.get_bone_global_pose(bone)).affine_inverse()*model.global_transform*placement
	var attachment := BoneAttachment3D.new()
	attachment.name = "MeasuredScannedWrist" if scanned_shoot else "MeasuredRocketboxWrist"
	attachment.bone_name = skeleton.get_bone_name(bone)
	skeleton.add_child(attachment)
	attachment.add_child(prop)
	prop.transform = local_mount
	if previous.is_empty():
		player.stop(); skeleton.reset_bone_poses()
	else:
		player.play(previous); player.seek(previous_time,true)
	skeleton.force_update_all_bone_transforms()
	attachment.on_skeleton_update()
	return prop
