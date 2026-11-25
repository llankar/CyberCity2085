extends Node3D
func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/unvanquished_motion01/"
	if "--saved-blend-roundtrip" in OS.get_cmdline_user_args():folder="E:/CyberCity2085-3d-lab/generated/phase2/unvanquished_roundtrip01/"
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(folder+"human_actions.glb",state)==OK)
	var model := document.generate_scene(state,120,false,false)
	add_child(model)
	var skeleton := model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	var player := model.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	assert(skeleton.get_bone_count()==122)
	var meshes := {}
	for mesh in model.find_children("*","MeshInstance3D",true,false):meshes[str(mesh.name).replace(".","_")]=mesh
	assert(meshes.size()==21)
	var reference = JSON.parse_string(FileAccess.get_file_as_string(folder+"source_surface_reference.json"))
	assert(reference.size()==6)
	var durations := {"Idle":400.0/60,"Walk":70.0/60,"Run":90.0/120,"Attack":16.0/60,"Death":40.0/60,"Crouch":10.0/60}
	var probe := preload("res://skin_motion_check.gd").new()
	var errors := {}
	for clip in reference:
		assert(player.has_animation(clip),"Missing authored clip: "+clip)
		assert(absf(player.get_animation(clip).length-durations[clip])<0.0001,"Source duration changed")
		var worst := 0.0
		for sample in reference[clip]:
			player.play(clip)
			player.seek(float(sample.time_s),true)
			player.advance(0)
			skeleton.force_update_all_bone_transforms()
			for name_value in sample.meshes:
				var mesh := meshes[str(name_value).replace(".","_")] as MeshInstance3D
				var points := probe.skinned_points(mesh,skeleton,1)
				for source_point in sample.meshes[name_value]:
					var expected := Vector3(source_point[0],source_point[2],-source_point[1])
					var nearest := INF
					for point in points:nearest=minf(nearest,point.distance_to(expected))
					worst=maxf(worst,nearest)
		assert(worst<0.002,"Authored skin mismatch in metres: "+clip+" "+str(worst))
		errors[clip]=worst
	player.play("Idle");player.seek(0,true);player.advance(0)
	skeleton.force_update_all_bone_transforms()
	var neutral := {}
	for name_value in meshes:neutral[name_value]=probe.skinned_points(meshes[name_value],skeleton,8)
	player.play("Death");player.seek(durations.Death,true);player.advance(0)
	player.play("Idle");player.seek(0,true);player.advance(0)
	skeleton.force_update_all_bone_transforms()
	var reset_error := 0.0
	for name_value in meshes:
		var restored := probe.skinned_points(meshes[name_value],skeleton,8)
		assert(restored.size()==neutral[name_value].size())
		for index in restored.size():reset_error=maxf(reset_error,restored[index].distance_to(neutral[name_value][index]))
	assert(reset_error<0.000001,"Death leaves stale pose channels")
	probe.free()
	var file := FileAccess.open(folder+"native_motion_check.json",FileAccess.WRITE)
	assert(file!=null)
	file.store_string(JSON.stringify({"glb_sha256":FileAccess.get_sha256(folder+"human_actions.glb"),"meshes":21,"bones":122,"surface_errors_m":errors,"death_idle_reset_m":reset_error,"durations_s":durations,"scope":"Six source body clips; grip, weapon composition and final art not accepted"},"  "))
	print("UNV_NATIVE_AUTHORED_MOTION_OK clips=6 meshes=21 bones=122")
	get_tree().quit(0)


