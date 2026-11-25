extends Node3D
## Native full skin vs sampled Blender surface, including action reset.
func _ready() -> void:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03/motion01/"
	var head_study := "--head-study" in OS.get_cmdline_user_args()
	var wardrobe_study := "--wardrobe-study" in OS.get_cmdline_user_args()
	assert(not (head_study and wardrobe_study))
	if head_study: root = "E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_hair08/character01/"
	if wardrobe_study: root = "E:/CyberCity2085-3d-lab/generated/phase2/wardrobe_fit01/"
	var reference_file := "garment_surface_reference.json" if wardrobe_study else ("head_surface_reference.json" if head_study else "surface_reference.json")
	var reference = JSON.parse_string(FileAccess.get_file_as_string(root + reference_file))
	assert(reference is Dictionary and reference.size() == 5)
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var filename := "human.glb" if head_study or wardrobe_study else "human_motion.glb"
	assert(doc.append_from_file(root + filename, state) == OK)
	var model := doc.generate_scene(state, 30, false, false)
	add_child(model)
	var rig := model.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var mesh_name := "AuthoredLeatherJacket_PBRStudy" if wardrobe_study else ("AuthoredHeadHair" if head_study else "*")
	var mesh := model.find_children(mesh_name, "MeshInstance3D", true, false)[0] as MeshInstance3D
	var player := model.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	assert(rig.get_bone_count() == 80 and mesh.mesh.get_blend_shape_count() == (0 if head_study or wardrobe_study else 175))
	var probe := preload("res://skin_motion_check.gd").new()
	var evidence := {}
	var neutral := PackedVector3Array()
	for clip in reference:
		assert(player.has_animation(clip))
		player.play(clip)
		var worst := 0.0
		for sample in reference[clip]:
			player.seek(float(sample.time_s), true)
			rig.force_update_all_bone_transforms()
			var points := probe.skinned_points(mesh, rig, 1)
			for source in sample.points:
				var expected := Vector3(source[0], source[2], -source[1])
				var nearest := INF
				for point in points: nearest = minf(nearest, point.distance_to(expected))
				worst = maxf(worst, nearest)
		print("ROCKETBOX_NATIVE_MOTION_SURFACE ", clip, " ", worst)
		assert(worst < 0.001, "Native motion differs from Blender surface")
		evidence[clip] = {"samples":9,"max_nearest_surface_error_m":worst,"duration_s":player.get_animation(clip).length}
	player.play("Idle"); player.seek(0, true); rig.force_update_all_bone_transforms()
	neutral = probe.skinned_points(mesh, rig, 1)
	player.play("Death01"); player.seek(player.get_animation("Death01").length, true)
	player.play("Idle"); player.seek(0, true); rig.force_update_all_bone_transforms()
	var reset := probe.skinned_points(mesh, rig, 1)
	var error := 0.0
	for index in range(neutral.size()): error = maxf(error, neutral[index].distance_to(reset[index]))
	assert(error < 0.00001)
	probe.free()
	var file := FileAccess.open(root + "native_motion_check.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({"sha256":FileAccess.get_sha256(root+filename),"clips":evidence,"death_idle_reset_m":error,"artistic_acceptance":false},"  "))
	print("AUTHORED_WARDROBE_NATIVE_MOTIONS_OK" if wardrobe_study else ("ROCKETBOX_NATIVE_HEAD_MOTIONS_OK" if head_study else "ROCKETBOX_NATIVE_FIVE_MOTIONS_OK"))
	get_tree().quit(0)
