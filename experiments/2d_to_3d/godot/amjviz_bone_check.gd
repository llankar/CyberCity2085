extends Node3D
## Diagnostic endpoints separate animation/TRS errors from nonlinear skin effects.

func converted(point: Array) -> Vector3:
	return Vector3(point[0],point[2],-point[1])

func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/amjviz_runtime144/"
	var reference: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(folder+"bone_reference145.json"))
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(folder+"human.glb",state)==OK)
	var model := document.generate_scene(state,24,false,false)
	add_child(model)
	var player := model.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	var skeleton := model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	var results := {}
	for clip in reference.clips:
		var samples := []
		for sample in reference.clips[clip]:
			player.play(clip);player.seek(sample.time_s,true);player.pause()
			skeleton.force_update_all_bone_transforms()
			var head_error := 0.0
			var tail_error := 0.0
			var worst_head := ""
			var worst_tail := ""
			for name_value in sample.bones:
				var index := skeleton.find_bone(name_value)
				assert(index>=0,name_value)
				var expected: Dictionary = sample.bones[name_value]
				var transform := skeleton.global_transform*skeleton.get_bone_global_pose(index)
				var head_delta := transform.origin.distance_to(converted(expected.head))
				var tail_delta := (transform*Vector3(0,expected.length,0)).distance_to(converted(expected.tail))
				if head_delta>head_error:head_error=head_delta;worst_head=name_value
				if tail_delta>tail_error:tail_error=tail_delta;worst_tail=name_value
			samples.append({"time_s":sample.time_s,"head_error_m":head_error,"head_bone":worst_head,
				"tail_error_m":tail_error,"tail_bone":worst_tail})
		results[clip]=samples
		print("AMJVIZ_BONE_CLIP_MEASURED ",clip)
	var file := FileAccess.open(folder+"bone_diagnostic145.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"glb_sha256":FileAccess.get_sha256(folder+"human.glb"),
		"reference_sha256":FileAccess.get_sha256(folder+"bone_reference145.json"),"clips":results,
		"scope":"Actual source/native endpoints; diagnostic, not mesh/art acceptance"},"  "))
	file.close()
	print("AMJVIZ_BONE_DIAGNOSTIC_WRITTEN")
	get_tree().quit()
