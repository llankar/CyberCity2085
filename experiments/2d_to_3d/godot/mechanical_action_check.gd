extends RefCounted
## Native articulated geometry checks, separate from artistic acceptance.

func verify_strike(actor: Node3D) -> void:
	var player := actor.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	assert(player.has_animation("Melee"))
	player.play("Melee")
	var animation := player.get_animation("Melee")
	assert(animation.loop_mode == Animation.LOOP_NONE)
	var skeleton := actor.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var hand: MeshInstance3D
	for candidate in actor.find_children("*", "MeshInstance3D", true, false):
		if str(candidate.name).replace(".", "_").replace("-", "_") == "GEO_hand_joint_L_Evaluated": hand = candidate
	assert(hand != null)
	var probe := preload("res://skin_motion_check.gd").new()
	var positions: Array[Vector3] = []
	for time_s in [0.0, 0.5, animation.length]:
		player.seek(time_s, true)
		skeleton.force_update_all_bone_transforms()
		positions.append(probe.skinned_points(hand, skeleton, 1)[0])
	assert(positions[0].distance_to(positions[1]) > 0.6, "Hand did not perform the actual strike")
	assert(positions[0].distance_to(positions[2]) < 0.0001, "Strike did not recover to rest")
	probe.free()
	print("MECHANICAL_STRIKE_STAGE_OK reach=", positions[0].distance_to(positions[1]), " recovered=true")

func verify_hit(actor: Node3D) -> Dictionary:
	var player := actor.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	assert(player.has_animation("Hit"))
	var clip := player.get_animation("Hit")
	assert(clip.loop_mode == Animation.LOOP_NONE and absf(clip.length - 0.8) < 0.0001)
	var skeleton := actor.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var probe := preload("res://skin_motion_check.gd").new()
	var evidence := {}
	var feet_checked := 0
	var head_checked := false
	for node in actor.find_children("*", "MeshInstance3D", true, false):
		var label := str(node.name)
		var head := "head_cover" in label
		var foot := ("toes" in label or "heel" in label) and not "heel_damper" in label
		if not head and not foot: continue
		player.play("Hit")
		player.seek(0, true)
		skeleton.force_update_all_bone_transforms()
		var baseline := probe.skinned_points(node, skeleton, 1)
		var maximum := 0.0
		var returned := 0.0
		for frame in range(25):
			player.seek(frame / 30.0, true)
			skeleton.force_update_all_bone_transforms()
			var points := probe.skinned_points(node, skeleton, 1)
			assert(points.size() == baseline.size())
			for index in range(points.size()):
				var error: float = baseline[index].distance_to(points[index])
				maximum = maxf(maximum, error)
				if frame == 24: returned = maxf(returned, error)
		if foot:
			assert(maximum < 0.0001, "Actual native hit foot slipped")
			feet_checked += 1
		if head:
			assert(maximum > 0.05, "Actual head did not recoil")
			head_checked = true
		assert(returned < 0.0001, "Hit did not recover")
		evidence[label] = {"maximum_vertex_displacement_m": maximum, "return_error_m": returned}
	assert(feet_checked == 4 and head_checked)
	probe.free()
	print("MECHANICAL_HIT_NATIVE_OK planted_feet=4 recovered=true")
	return evidence

func verify_shutdown(actor: Node3D) -> Dictionary:
	var player := actor.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	assert(player.has_animation("Death"))
	var clip := player.get_animation("Death")
	assert(clip.loop_mode == Animation.LOOP_NONE and absf(clip.length-2.0)<0.0001)
	var skeleton := actor.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var meshes := actor.find_children("*", "MeshInstance3D", true, false)
	assert(meshes.size() == 124)
	var probe := preload("res://skin_motion_check.gd").new()
	var held_geometry := {}
	var samples := []
	var drift := 0.0
	player.play("Death")
	for time_s in [0.0,0.4,1.25,1.6,2.0]:
		player.seek(time_s,true)
		skeleton.force_update_all_bone_transforms()
		var minimum := Vector3(INF,INF,INF)
		var maximum := Vector3(-INF,-INF,-INF)
		for mesh in meshes:
			var points := probe.skinned_points(mesh,skeleton,1)
			assert(not points.is_empty())
			for index in range(points.size()):
				minimum = minimum.min(points[index])
				maximum = maximum.max(points[index])
				if time_s == 2.0: drift=maxf(drift,points[index].distance_to(held_geometry[mesh.name][index]))
			if time_s == 1.6: held_geometry[mesh.name]=points
		assert(minimum.y > -0.00001, "Shutdown geometry penetrates flat floor")
		assert(absf(minimum.y)<0.0001, "Shutdown geometry floats above floor")
		samples.append({"time_s":time_s,"height_m":maximum.y-minimum.y,"horizontal_span_m":maxf(maximum.x-minimum.x,maximum.z-minimum.z),"floor_minimum_m":minimum.y})
	assert(samples[0].height_m > 1.8)
	assert(samples[4].height_m < 0.8 and samples[4].horizontal_span_m > 1.2,"Robot failed to topple")
	assert(drift<0.0001,"Dead geometry fails to remain settled")
	probe.free()
	print("MECHANICAL_SHUTDOWN_NATIVE_OK settled=true meshes=124 final_height=",samples[4].height_m)
	return {"height_initial_m":samples[0].height_m,"samples":samples,"settled_max_vertex_drift_m":drift,"scope":"All124meshes at five native poses, flat floor only; no inter-part collision guarantee"}
