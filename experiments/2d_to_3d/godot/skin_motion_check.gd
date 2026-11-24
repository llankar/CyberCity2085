extends Node3D
## Native skin evaluation gate for the authored head diagnostic, not animation art.

func skinned_points(mesh: MeshInstance3D, skeleton: Skeleton3D) -> PackedVector3Array:
	var result := PackedVector3Array()
	for surface in range(mesh.mesh.get_surface_count()):
		var arrays := mesh.mesh.surface_get_arrays(surface)
		var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var joints: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
		var weights: PackedFloat32Array = arrays[Mesh.ARRAY_WEIGHTS]
		var stride := joints.size() / vertices.size()
		assert(stride == 4 or stride == 8)
		for vertex in range(0, vertices.size(), 8):
			var point := Vector3.ZERO
			for influence in range(stride):
				var weight := weights[vertex * stride + influence]
				if weight <= 0: continue
				var bind := joints[vertex * stride + influence]
				var bone := mesh.skin.get_bind_bone(bind)
				if bone < 0: bone = skeleton.find_bone(mesh.skin.get_bind_name(bind))
				assert(bone >= 0 and bone < skeleton.get_bone_count())
				point += (skeleton.get_bone_global_pose(bone) * mesh.skin.get_bind_pose(bind) * vertices[vertex]) * weight
			result.append(skeleton.global_transform * point)
	return result

func _ready() -> void:
	var walk := "--walk" in OS.get_cmdline_user_args()
	var idle := "--idle" in OS.get_cmdline_user_args() or walk
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/" + ("einar_walk01/" if walk else "einar_idle01/" if idle else "einar_rig01/")
	var source_root := root
	var bundle := "--bundle" in OS.get_cmdline_user_args()
	if bundle: root = "E:/CyberCity2085-3d-lab/generated/phase2/einar_motion01/"
	var clip := "Walk" if walk else "Idle" if idle else "FittingStressTest"
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(root + ("human_motion.glb" if bundle else "human_rig.glb"), state) == OK)
	var model := document.generate_scene(state)
	add_child(model)
	var skeletons := model.find_children("*", "Skeleton3D", true, false)
	assert(skeletons.size() == 1)
	var skeleton := skeletons[0] as Skeleton3D
	assert(skeleton.get_bone_count() == 222)
	var heads := model.find_children("*einar_head*", "MeshInstance3D", true, false)
	var legs := model.find_children("*pants_main*", "MeshInstance3D", true, false)
	assert(heads.size() == 1 and legs.size() == 1)
	var player := model.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	assert(player.has_animation(clip))
	var report = JSON.parse_string(FileAccess.get_file_as_string(source_root + "rig_report.json"))
	if "duration_s" in report:
		assert(absf(player.get_animation(clip).length - float(report.duration_s)) < 0.0001)
	player.play(clip)
	player.seek(0, true)
	skeleton.force_update_all_bone_transforms()
	var neutral_head := skinned_points(heads[0], skeleton)
	var neutral_legs := skinned_points(legs[0], skeleton)
	player.seek(player.get_animation(clip).length * 0.25, true)
	skeleton.force_update_all_bone_transforms()
	var moved_head := skinned_points(heads[0], skeleton)
	var moved_legs := skinned_points(legs[0], skeleton)
	var head_delta := 0.0
	var legs_delta := 0.0
	for index in range(neutral_head.size()):
		assert(moved_head[index].is_finite())
		head_delta = maxf(head_delta, neutral_head[index].distance_to(moved_head[index]))
	for index in range(neutral_legs.size()):
		assert(moved_legs[index].is_finite())
		legs_delta = maxf(legs_delta, neutral_legs[index].distance_to(moved_legs[index]))
	assert(head_delta > (0.0005 if idle else 0.005) and head_delta < 0.2)
	assert(legs_delta > 0.03 if walk else legs_delta < 0.0001)
	player.seek(player.get_animation(clip).length, true)
	skeleton.force_update_all_bone_transforms()
	var end_head := skinned_points(heads[0], skeleton)
	var loop_gap := 0.0
	for index in range(neutral_head.size()):
		loop_gap = maxf(loop_gap, neutral_head[index].distance_to(end_head[index]))
	assert(loop_gap < 0.0001)
	var evidence := {"bones": skeleton.get_bone_count(), "head_max_motion_m": head_delta,
		"legs_max_motion_m": legs_delta, "clip": clip, "head_loop_gap_m": loop_gap,
		"scope": "Native skin transform sampling; not visual animation acceptance"}
	if walk:
		var soles := model.find_children("*boot_sole*", "MeshInstance3D", true, false)
		assert(soles.size() == 2)
		var contacts := {}
		for sole in soles:
			var left: bool = ".L" in str(sole.name) or "_L_" in str(sole.name)
			var start := 0.0 if left else 0.5
			player.seek(player.get_animation(clip).length * start, true)
			skeleton.force_update_all_bone_transforms()
			var before := skinned_points(sole, skeleton)
			var contact_error := 0.0
			var lowest := INF
			for index in range(before.size()):
				lowest = minf(lowest, before[index].y)
			var floor_error := absf(lowest - (-0.03))
			for sample in range(1, 17):
				var finish := start + sample / 32.0
				player.seek(player.get_animation(clip).length * finish, true)
				skeleton.force_update_all_bone_transforms()
				var after := skinned_points(sole, skeleton)
				var sample_lowest := INF
				for index in range(before.size()):
					contact_error = maxf(contact_error, (before[index] + Vector3(0, 0, 0.7 * start)).distance_to(after[index] + Vector3(0, 0, 0.7 * finish)))
					sample_lowest = minf(sample_lowest, after[index].y)
				floor_error = maxf(floor_error, absf(sample_lowest - (-0.03)))
			print("EINAR_WALK_CONTACT_PROBE ", sole.name, " error=", contact_error, " sole_y=", lowest)
			# The independent tactical floor is explicitly at Y=-0.03m.
			assert(contact_error < 0.005 and floor_error < 0.01)
			contacts[str(sole.name)] = {"stance_drift_m": contact_error, "lowest_sole_y_m": lowest, "floor_y_m": -0.03, "max_floor_clearance_error_m": floor_error, "stance_samples": 17}
		evidence["virtual_root_travel_m"] = 0.7
		evidence["contacts"] = contacts
	var file := FileAccess.open(root + ("native_skin_motion_" + clip + ".json" if bundle else "native_skin_motion.json"), FileAccess.WRITE)
	assert(file != null)
	file.store_string(JSON.stringify(evidence, "  "))
	print("EINAR_NATIVE_SKIN_MOTION_OK ", JSON.stringify(evidence))
	get_tree().quit(0)
