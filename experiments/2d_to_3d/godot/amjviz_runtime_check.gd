extends Node3D
## Actual authored Blender poses versus the exported deform-only GLB.

func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/amjviz_runtime144/"
	var full_diagnostic := "--all-bones-diagnostic" in OS.get_cmdline_user_args()
	if full_diagnostic:folder="E:/CyberCity2085-3d-lab/generated/phase2/amjviz_full144/"
	var diagnostic := "--linear-diagnostic" in OS.get_cmdline_user_args()
	var reset_diagnostic := "--reset-reference" in OS.get_cmdline_user_args()
	var reference_kind := "reset_linear" if reset_diagnostic and diagnostic else ("reset" if reset_diagnostic else ("linear" if diagnostic else "original"))
	var reference_name := "reset_linear_source_reference.json" if reset_diagnostic and diagnostic else ("reset_source_reference.json" if reset_diagnostic else ("linear_source_reference.json" if diagnostic else "native_reference.json"))
	var references: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(folder+reference_name))
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(folder+"human.glb",state)==OK)
	var model := document.generate_scene(state,24,false,false)
	add_child(model)
	var player := model.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	var skeleton := model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	var meshes := model.find_children("*","MeshInstance3D",true,false)
	assert(skeleton.get_bone_count()==706 if full_diagnostic else skeleton.get_bone_count()<706,"Unexpected skeleton coverage")
	assert(player.get_animation_list().size()==references.size())
	var probe := preload("res://skin_motion_check.gd").new()
	var errors := {}
	var count := 0
	var worst := 0.0
	for clip in references:
		assert(player.has_animation(clip),clip)
		var clip_worst := 0.0
		var integer_worst := 0.0
		for sample in references[clip]:
			player.play(clip)
			player.seek(sample.time_s,true)
			player.pause()
			skeleton.force_update_all_bone_transforms()
			var actual := AABB()
			var first := true
			for mesh in meshes:
				for point in probe.skinned_points(mesh,skeleton,1,true):
					actual=AABB(point,Vector3.ZERO) if first else actual.expand(point)
					first=false
			assert(not first)
			var expected := AABB()
			first=true
			var bounds: Array = sample.bounds_blender
			for x in [bounds[0][0],bounds[1][0]]:
				for y in [bounds[0][1],bounds[1][1]]:
					for z in [bounds[0][2],bounds[1][2]]:
						var point := Vector3(x,z,-y)
						expected=AABB(point,Vector3.ZERO) if first else expected.expand(point)
						first=false
			var error := maxf(actual.position.distance_to(expected.position),actual.end.distance_to(expected.end))
			clip_worst=maxf(clip_worst,error)
			if absf(sample.time_s*24-roundf(sample.time_s*24))<.0001:integer_worst=maxf(integer_worst,error)
			worst=maxf(worst,error)
			count+=1
			if count%3==0:await get_tree().process_frame
		errors[clip]={"error_m":clip_worst,"integer_key_error_m":integer_worst}
		print("AMJVIZ_NATIVE_CLIP_BOUNDS ",clip," error_m=",clip_worst)
	var report := {"glb_sha256":FileAccess.get_sha256(folder+"human.glb"),
		"reference_sha256":FileAccess.get_sha256(folder+reference_name),"reference_kind":reference_kind,
		"bones":skeleton.get_bone_count(),"meshes":meshes.size(),"samples":count,
		"maximum_error_m":worst,"clips":errors,
		"scope":"Full evaluated mesh bounds at source key and half-key times; not art/contact acceptance"}
	var report_name := "reset_linear_bounds.json" if reset_diagnostic and diagnostic else ("reset_reference_bounds.json" if reset_diagnostic else ("linear_diagnostic_bounds.json" if diagnostic else "native_bounds.json"))
	var file := FileAccess.open(folder+report_name,FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	file.close()
	if worst>=.0005:
		push_error("Source deformation mismatch: %s"%worst)
		get_tree().quit(1)
		return
	print("AMJVIZ_DIAGNOSTIC_MATCH samples=" if diagnostic or reset_diagnostic or full_diagnostic else "AMJVIZ_DEFORM_NATIVE_PASS samples=",count," bones=",skeleton.get_bone_count()," error_m=",worst)
	get_tree().quit()
