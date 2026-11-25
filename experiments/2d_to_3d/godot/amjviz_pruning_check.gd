extends Node3D
## Compare every actual skinned vertex against the author's game GLB.

func imported(path: String) -> Node3D:
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(path,state)==OK)
	var model := document.generate_scene(state,24,false,false)
	add_child(model)
	return model

func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/amjviz_pruned145/"
	var source_path := "E:/CyberCity2085-3d-lab/sources/blenderkit_cyberpunk143/source_godot.glb"
	var source := imported(source_path)
	var candidate := imported(folder+"human.glb")
	var original_player := source.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	var player := candidate.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	var original_rig := source.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	var rig := candidate.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	assert(original_rig.get_bone_count()==706 and rig.get_bone_count()==262)
	assert(original_player.get_animation_list()==player.get_animation_list())
	var original_meshes := source.find_children("*","MeshInstance3D",true,false)
	var meshes := candidate.find_children("*","MeshInstance3D",true,false)
	assert(original_meshes.size()==meshes.size())
	var samples: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(folder+"samples.json"))
	var probe := preload("res://skin_motion_check.gd").new()
	var worst := 0.0
	var count := 0
	var vertex_checks := 0
	var clips := {}
	for clip in samples:
		assert(player.has_animation(clip))
		var clip_worst := 0.0
		for time in samples[clip]:
			original_player.play(clip);original_player.seek(time,true);original_player.pause()
			player.play(clip);player.seek(time,true);player.pause()
			original_rig.force_update_all_bone_transforms();rig.force_update_all_bone_transforms()
			for i in range(meshes.size()):
				var expected: PackedVector3Array = probe.skinned_points(original_meshes[i],original_rig,1,true)
				var actual: PackedVector3Array = probe.skinned_points(meshes[i],rig,1,true)
				assert(actual.size()==expected.size())
				for vertex in range(actual.size()):
					var error := actual[vertex].distance_to(expected[vertex])
					worst=maxf(worst,error);clip_worst=maxf(clip_worst,error)
				vertex_checks+=actual.size()
			count+=1
			await get_tree().process_frame
		clips[clip]={"samples":samples[clip].size(),"maximum_vertex_error_m":clip_worst}
		print("AMJVIZ_PRUNED_CLIP_VERTICES ",clip," error_m=",clip_worst)
	var file := FileAccess.open(folder+"native_equivalence.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"source_sha256":FileAccess.get_sha256(source_path),
		"candidate_sha256":FileAccess.get_sha256(folder+"human.glb"),"source_bones":706,"candidate_bones":262,
		"samples":count,"vertex_checks":vertex_checks,"maximum_vertex_error_m":worst,"clips":clips,
		"scope":"Full source-game/native skin vertices at source key/midpoint times; not exact original Blender B-Bone fidelity or final art"},"  "))
	file.close()
	probe.free()
	if worst>.000001:
		push_error("Game source pruning mismatch: %s"%worst);get_tree().quit(1);return
	print("AMJVIZ_PRUNED_NATIVE_EQUIVALENCE_PASS samples=",count," vertex_checks=",vertex_checks," error_m=",worst)
	get_tree().quit()
