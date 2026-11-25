extends Node3D
## Real rigid vehicle surfaces and animation resets; not flight/collision acceptance.
func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/vtol_motion01/"
	var finish_study := "--vtol-finish-study" in OS.get_cmdline_user_args()
	if finish_study: folder = "E:/CyberCity2085-3d-lab/generated/phase2/vtol_finish135/"
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(folder+"vtol_actions.glb",state)==OK)
	var model := document.generate_scene(state)
	add_child(model)
	var player := model.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	assert(player.get_animation_list().size()==3)
	var meshes := {}
	for mesh in model.find_children("*","MeshInstance3D",true,false):meshes[str(mesh.name).replace(".","_")]=mesh
	assert(meshes.size()==(56 if finish_study else 48))
	var references = JSON.parse_string(FileAccess.get_file_as_string(folder+"source_surface_reference.json"))
	var errors := {}
	for clip in ["Rotor_Spin","Gear_Retract","Gear_Extend"]:
		assert(player.has_animation(clip))
		player.play(clip)
		var worst := 0.0
		var diagnostic := {}
		for sample in references[clip]:
			player.seek(sample.time_s,true)
			for name_value in sample.meshes:
				var mesh := meshes[str(name_value).replace(".","_")] as MeshInstance3D
				for source_point in sample.meshes[name_value]:
					var expected := Vector3(source_point[0],source_point[2],-source_point[1])
					var nearest := INF
					for surface in range(mesh.mesh.get_surface_count()):
						var points: PackedVector3Array = mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]
						for point in points:nearest=minf(nearest,(mesh.global_transform*point).distance_to(expected))
					if nearest>worst:
						worst=nearest
						diagnostic={"mesh":name_value,"time":sample.time_s,"expected":str(expected),"error":nearest}
		print("VTOL_SOURCE_COMPARE ",clip," ",JSON.stringify(diagnostic))
		assert(worst<0.0001,"Vehicle native articulation differs from source")
		errors[clip]=worst
	# Explicit action change restores deployed gear without reloading the model.
	player.play("Rotor_Spin");player.seek(0,true)
	var neutral := {}
	for name_value in meshes:
		if "LandingShoe" in name_value:neutral[name_value]=meshes[name_value].global_transform
	assert(neutral.size()==4)
	player.play("Gear_Retract");player.seek(1,true)
	var motion := 0.0
	for name_value in neutral:motion=maxf(motion,neutral[name_value].origin.distance_to(meshes[name_value].global_transform.origin))
	assert(motion>0.5,"Actual landing shoes failed to retract")
	player.play("Rotor_Spin");player.advance(0);player.seek(0,true)
	var reset_error := 0.0
	for name_value in neutral:reset_error=maxf(reset_error,neutral[name_value].origin.distance_to(meshes[name_value].global_transform.origin))
	assert(reset_error<0.0001,"Stowed gear survived action reset")
	var output := FileAccess.open(folder+"native_motion_check.json",FileAccess.WRITE)
	assert(output!=null)
	output.store_string(JSON.stringify({"glb_sha256":FileAccess.get_sha256(folder+"vtol_actions.glb"),"clips":errors,"gear_surface_travel_m":motion,"gear_reset_error_m":reset_error,"scope":"Native rigid surfaces at27sampled poses and four gear action resets; not collision/flight/art acceptance"},"  "))
	print("VTOL_NATIVE_ARTICULATION_OK gear_travel=",motion," reset=",reset_error)
	get_tree().quit(0)
