extends Node3D
## Pose retention gate only: decimation intentionally changes surface topology.

func load_model(path: String) -> Node3D:
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(path,state)==OK)
	var model := document.generate_scene(state,30,false,false)
	add_child(model)
	return model

func transform_error(first: Transform3D, second: Transform3D) -> float:
	return maxf(first.origin.distance_to(second.origin),maxf(first.basis.x.distance_to(second.basis.x),maxf(first.basis.y.distance_to(second.basis.y),first.basis.z.distance_to(second.basis.z))))

func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/"
	var models := [load_model(folder+"grab3d_cyborg01/human.glb"), load_model(folder+"grab3d_cyborg_lod01/human.glb")]
	var skeletons: Array[Skeleton3D] = []
	var players: Array[AnimationPlayer] = []
	for model in models:
		skeletons.append(model.find_children("*", "Skeleton3D", true, false)[0])
		players.append(model.find_children("*", "AnimationPlayer", true, false)[0])
		assert(skeletons[-1].get_bone_count()==24)
	var worst := 0.0
	var position_error := 0.0
	var samples := 0
	for clip in ["walk", "run"]:
		assert(absf(players[0].get_animation(clip).length-players[1].get_animation(clip).length)<.001)
		for sample in range(17):
			for index in range(2):
				players[index].play(clip)
				players[index].seek(players[index].get_animation(clip).length*sample/16.0,true)
				players[index].pause()
				skeletons[index].force_update_all_bone_transforms()
			for bone in range(24):
				var other := skeletons[1].find_bone(skeletons[0].get_bone_name(bone))
				assert(other>=0)
				worst=maxf(worst,transform_error(skeletons[0].get_bone_global_pose(bone),skeletons[1].get_bone_global_pose(other)))
				position_error=maxf(position_error,skeletons[0].get_bone_global_pose(bone).origin.distance_to(skeletons[1].get_bone_global_pose(other).origin))
			samples+=1
	# Re-export resamples source quaternion curves. This is bounded LOD fidelity,
	# not a claim of byte-exact animation or identical interpolation.
	assert(worst<.003 and position_error<.002, "LOD animation exceeded 2mm position / .003 basis-axis tolerance: %s / %s"%[position_error,worst])
	var report := {"status":"PASS","maximum_joint_transform_error":worst,"maximum_joint_position_error_m":position_error,"position_tolerance_m":.002,"basis_axis_tolerance":.003,"sampled_poses":samples,"bones":24,"clips":["walk","run"],"scope":"Bounded native skeleton transform retention; not identical interpolation, silhouette, foot contact or final art acceptance"}
	var output := FileAccess.open(folder+"grab3d_cyborg_lod01/native_pose_retention.json",FileAccess.WRITE)
	assert(output!=null)
	output.store_string(JSON.stringify(report,"  "))
	output.close()
	print("CYBORG_LOD_NATIVE_POSES_PASS ",JSON.stringify(report))
	get_tree().quit()
