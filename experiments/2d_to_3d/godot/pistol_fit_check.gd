extends Node3D
## Attachment/axis/near-surface gate, not a complete artistic grip acceptance.

func _ready() -> void:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/einar_pistol_fit01/"
	if "--surface-corrections" in OS.get_cmdline_user_args(): root = root.trim_suffix("/") + "_surfaces/"
	var metadata = JSON.parse_string(FileAccess.get_file_as_string(root + "fit_report.json"))
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(root + "human_pistol.glb", state) == OK)
	var model := document.generate_scene(state)
	add_child(model)
	var skeleton := model.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var player := model.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var barrels := model.find_children("*EquippedPistol_barrel*", "MeshInstance3D", true, false)
	var gloves := model.find_children("*einar_glove*", "MeshInstance3D", true, false)
	assert(barrels.size() == 1 and gloves.size() == 1 and skeleton.get_bone_count() == 222)
	var barrel := barrels[0] as MeshInstance3D
	var arrays := barrel.mesh.surface_get_arrays(0)
	var binds: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
	var bind := binds[0]
	var bone := barrel.skin.get_bind_bone(bind)
	if bone < 0: bone = skeleton.find_bone(barrel.skin.get_bind_name(bind))
	assert(bone >= 0 and str(skeleton.get_bone_name(bone)).begins_with(str(metadata.joint).get_slice("_", 0)))
	var rest_grip := Vector3(metadata.rest_grip_world[0], metadata.rest_grip_world[2], -metadata.rest_grip_world[1])
	var forward := Vector3(metadata.weapon_forward_rest[0], metadata.weapon_forward_rest[2], -metadata.weapon_forward_rest[1])
	var up := Vector3(metadata.weapon_up_rest[0], metadata.weapon_up_rest[2], -metadata.weapon_up_rest[1])
	var probe := preload("res://skin_motion_check.gd").new()
	var evidence := []
	var max_distance := 0.0
	player.play("Pistol_Shoot")
	for fraction in [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]:
		player.seek(player.get_animation("Pistol_Shoot").length * fraction, true)
		skeleton.force_update_all_bone_transforms()
		var delta := skeleton.global_transform * skeleton.get_bone_global_pose(bone) * barrel.skin.get_bind_pose(bind)
		var grip := delta * rest_grip
		var aim := (delta.basis * forward).normalized()
		var vertical := (delta.basis * up).normalized()
		var nearest := INF
		for point in probe.skinned_points(gloves[0], skeleton): nearest = minf(nearest, grip.distance_to(point))
		max_distance = maxf(max_distance, nearest)
		print("PISTOL_GRIP_PROBE t=", fraction, " nearest=", nearest, " forward=", aim.z, " up=", vertical.y)
		assert(grip.is_finite() and nearest < 0.04 and aim.z > 0.5 and vertical.y > 0.5)
		evidence.append({"fraction": fraction, "nearest_sampled_glove_m": nearest, "forward_z": aim.z, "up_y": vertical.y})
	probe.free()
	var report := {"glb_sha256": FileAccess.get_sha256(root + "human_pistol.glb"),
		"primary_wrist_joint": str(skeleton.get_bone_name(bone)), "samples": evidence,
		"max_nearest_sampled_glove_m": max_distance,
		"scope": "Primary attachment, broad orientation and sampled surface proximity only",
		"remaining": "Mechanical support hand, exact trigger grip and artistic acceptance"}
	var output := FileAccess.open(root + "native_fit_check.json", FileAccess.WRITE)
	assert(output != null)
	output.store_string(JSON.stringify(report, "  "))
	print("EINAR_PISTOL_FIT_GATE_OK ", max_distance)
	get_tree().quit(0)
