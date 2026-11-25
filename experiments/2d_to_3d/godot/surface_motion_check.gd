extends Node3D
## Compare authored source surface samples with native morph+skin deformation.
func _ready() -> void:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/einar_ual_Pistol_Shoot01_surfaces/"
	var model_file := "human_rig.glb"
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--folder="): root = argument.trim_prefix("--folder=") + "/"
		if argument.begins_with("--model-file="): model_file = argument.trim_prefix("--model-file=")
	assert(model_file.get_file() == model_file and model_file.ends_with(".glb"))
	var reference = JSON.parse_string(FileAccess.get_file_as_string(root + "surface_reference.json"))
	assert(reference is Dictionary and not reference.is_empty())
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(root + model_file, state) == OK)
	var model := document.generate_scene(state)
	add_child(model)
	var skeleton := model.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var player := model.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var animations := player.get_animation_list()
	var clip := ""
	for candidate in animations:
		if candidate != "RESET":
			assert(clip.is_empty(), "Unexpected multiple action clips")
			clip = candidate
	assert(not clip.is_empty())
	player.play(clip)
	var probe := preload("res://skin_motion_check.gd").new()
	var evidence := {}
	for object_name in reference:
		var meshes: Array[Node] = []
		for candidate in model.find_children("*", "MeshInstance3D", true, false):
			if str(candidate.name).replace(".", "_") == str(object_name).replace(".", "_"): meshes.append(candidate)
		assert(meshes.size() == 1, object_name)
		var mesh := meshes[0] as MeshInstance3D
		assert(mesh.mesh.get_blend_shape_count() == 0 or mesh.mesh.get_blend_shape_count() == reference[object_name].size())
		var worst := 0.0
		for sample in reference[object_name]:
			player.seek(float(sample.time_s), true)
			skeleton.force_update_all_bone_transforms()
			var points := probe.skinned_points(mesh, skeleton, 1)
			for source_point in sample.points:
				var expected := Vector3(source_point[0], source_point[2], -source_point[1])
				var nearest := INF
				for point in points: nearest = minf(nearest, point.distance_to(expected))
				worst = maxf(worst, nearest)
		print("SURFACE_ERROR ", object_name, " ", worst)
		assert(worst < 0.001, "Source deformation mismatch")
		evidence[object_name] = {"max_sampled_surface_distance_m": worst, "frames": reference[object_name].size()}
	probe.free()
	var output := FileAccess.open(root + "native_surface_check.json", FileAccess.WRITE)
	assert(output != null)
	output.store_string(JSON.stringify({"glb_sha256": FileAccess.get_sha256(root + model_file), "clip": clip, "surfaces": evidence, "scope": "Sampled nearest surface distance at authored frame times; not artistic acceptance"}, "  "))
	print("EINAR_NATIVE_SURFACE_GATE_OK")
	get_tree().quit(0)
