extends Node3D
## Compare shared-bundle skin transforms, sampled surfaces and action resets.
var states: Array[GLTFState] = []

func load_model(path: String) -> Node3D:
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(path, state) == OK)
	states.append(state)
	var model := document.generate_scene(state, 30, false, false)
	add_child(model)
	return model

func meshes(model: Node3D) -> Dictionary:
	var result := {}
	for mesh in model.find_children("*", "MeshInstance3D", true, false): result[str(mesh.name).replace(".", "_")] = mesh
	return result

func skin_transforms(skeleton: Skeleton3D, mesh: MeshInstance3D) -> Dictionary:
	var result := {}
	for bind in range(mesh.skin.get_bind_count()):
		var bone := mesh.skin.get_bind_bone(bind)
		if bone < 0: bone = skeleton.find_bone(mesh.skin.get_bind_name(bind))
		assert(bone >= 0)
		result[str(skeleton.get_bone_name(bone)).get_slice("_", 0)] = skeleton.global_transform * skeleton.get_bone_global_pose(bone) * mesh.skin.get_bind_pose(bind)
	return result

func transform_error(first: Transform3D, second: Transform3D) -> float:
	return maxf(first.origin.distance_to(second.origin), maxf(first.basis.x.distance_to(second.basis.x), maxf(first.basis.y.distance_to(second.basis.y), first.basis.z.distance_to(second.basis.z))))

func _ready() -> void:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/"
	var robot := "--robot-bundle" in OS.get_cmdline_user_args()
	var folder := root + ("security_bundle01/" if robot else "einar_bundle02/")
	var filename := "robot_actions.glb" if robot else "human_actions.glb"
	var expected_meshes := 124 if robot else 76
	var expected_joints := 124 if robot else 222
	var metadata = JSON.parse_string(FileAccess.get_file_as_string(folder + "bundle_report.json"))
	var bundle := load_model(folder + filename)
	var targets := meshes(bundle)
	var skeleton := bundle.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var player := bundle.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	assert(targets.size() == expected_meshes and skeleton.get_bone_count() == expected_joints)
	var probe := preload("res://skin_motion_check.gd").new()
	var report := {}
	var idle_points := {}
	var selected_meshes: Array[String] = []
	for name_value in targets:
		if (robot and ("cable_tube" in name_value or "head_cover" in name_value or "heel" in name_value or "toes" in name_value or "shin" in name_value)) or "satchel_strap" in name_value or "boot_sole" in name_value or "strap_shoulder" in name_value or "einar_head" in name_value or "pants_main" in name_value:
			selected_meshes.append(name_value)
	assert(selected_meshes.size() >= 8)
	for source in metadata.sources:
		var model := load_model(root + str(source.folder) + "/" + str(source.get("file", "human_rig.glb")))
		var originals := meshes(model)
		var source_skeleton := model.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
		var source_player := model.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
		var clip := ""
		for candidate in source_player.get_animation_list():
			if candidate != "RESET":
				assert(clip.is_empty())
				clip = candidate
		assert(player.has_animation(clip))
		var duration := source_player.get_animation(clip).length
		assert(absf(player.get_animation(clip).length - duration) < 0.00001)
		player.play(clip); source_player.play(clip)
		player.advance(0); source_player.advance(0)
		var worst_transform := 0.0
		var worst_joint := {}
		var worst_surface := 0.0
		for sample in range(17):
			var fraction := sample / 16.0
			player.seek(duration * fraction, true); source_player.seek(duration * fraction, true)
			skeleton.force_update_all_bone_transforms(); source_skeleton.force_update_all_bone_transforms()
			var current := skin_transforms(skeleton, targets.values()[0])
			var wanted := skin_transforms(source_skeleton, originals.values()[0])
			assert(current.size() == expected_joints and wanted.size() == expected_joints)
			for joint in current:
				var error := transform_error(current[joint], wanted[joint])
				if error > worst_transform:
					worst_transform = error
					worst_joint = {"joint": joint, "fraction": fraction, "actual": str(current[joint]), "expected": str(wanted[joint]), "clip": player.current_animation}
			if sample % 2 != 0: continue
			for name_value in selected_meshes:
				var points := probe.skinned_points(targets[name_value], skeleton)
				var expected := probe.skinned_points(originals[name_value], source_skeleton)
				assert(points.size() == expected.size(), name_value)
				for index in range(points.size()): worst_surface = maxf(worst_surface, points[index].distance_to(expected[index]))
				if clip == "Idle" and sample == 0: idle_points[name_value] = expected
		print("BUNDLE_CLIP_COMPARE ", clip, " transform=", worst_transform, " surface=", worst_surface)
		if worst_transform > 0.0001: print("BUNDLE_TRANSFORM_DIAGNOSTIC ", JSON.stringify(worst_joint))
		assert(worst_transform < 0.0001 and worst_surface < 0.0005, "Bundled action differs from individual source")
		report[clip] = {"duration_s": duration, "max_skin_transform_error": worst_transform, "max_sampled_vertex_error_m": worst_surface, "transform_samples": 17, "surface_samples": 9}
		model.free()
		states.pop_back()
	# Death corrections must not survive an ordinary animation change to Idle.
	var death_clip := "Death" if robot else "Death01"
	player.play(death_clip); player.seek(player.get_animation(death_clip).length, true)
	skeleton.force_update_all_bone_transforms()
	player.play("Idle"); player.advance(0); player.seek(0, true)
	skeleton.force_update_all_bone_transforms()
	var reset_error := 0.0
	for name_value in idle_points:
		var points := probe.skinned_points(targets[name_value], skeleton)
		var expected: PackedVector3Array = idle_points[name_value]
		for index in range(points.size()): reset_error = maxf(reset_error, points[index].distance_to(expected[index]))
	assert(reset_error < 0.0005, "Stale corrections after Death to Idle")
	probe.free()
	var output := FileAccess.open(folder + "native_bundle_check.json", FileAccess.WRITE)
	assert(output != null)
	output.store_string(JSON.stringify({"glb_sha256": FileAccess.get_sha256(folder + filename), "clips": report, "death_to_idle_reset_error_m": reset_error, "meshes": expected_meshes, "joints": expected_joints, "selected_surface_meshes": selected_meshes, "scope": "Native original/bundle skin transforms and sampled vertex correspondence; not artistic acceptance"}, "  "))
	print("ROBOT_NATIVE_ACTION_BUNDLE_OK reset=" if robot else "EINAR_NATIVE_ACTION_BUNDLE_OK reset=", reset_error)
	get_tree().quit(0)
