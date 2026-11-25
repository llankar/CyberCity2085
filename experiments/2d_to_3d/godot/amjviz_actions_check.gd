extends Node3D
## Actual full-body/weapon export fidelity; does not stand in for artistic review.

func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/amjviz_actions146/"
	var hair_study := "--hair-study" in OS.get_cmdline_user_args()
	if hair_study:folder="E:/CyberCity2085-3d-lab/generated/phase2/amjviz_hair148/"
	var reference: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(folder+"native_reference.json"))
	var reference_hash := FileAccess.get_sha256(folder+"native_reference.json")
	if "--texture-budget-study" in OS.get_cmdline_user_args():
		assert(not hair_study,"Choose one geometry reference")
		folder="E:/CyberCity2085-3d-lab/generated/phase2/amjviz_budget147_1024/"
	var model_path := folder+("human.glb" if hair_study else "human_actions.glb")
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(model_path,state)==OK)
	var model := document.generate_scene(state,120,false,false)
	add_child(model)
	var player := model.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	var rig := model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	assert(rig.get_bone_count()==262 and player.get_animation_list().size()==7)
	var meshes := {}
	for mesh in model.find_children("*","MeshInstance3D",true,false):meshes[str(mesh.name).replace(".","_").replace(" ","_")]=mesh
	assert(meshes.size()==(11 if hair_study else 10))
	var probe := preload("res://skin_motion_check.gd").new()
	var checker := preload("res://cyborg_ready_check.gd").new()
	var worst := 0.0
	var count := 0
	var clips := {}
	for clip in reference.clips:
		assert(player.has_animation(clip))
		var error := 0.0
		var floor_value := INF
		var final_height := 0.0
		for sample in reference.clips[clip]:
			player.play(clip);player.seek(sample.time_s,true);player.pause();rig.force_update_all_bone_transforms()
			var result: Dictionary = checker.compare_sample(meshes,rig,probe,sample.mesh_bounds_blender,reference.body_name)
			error=maxf(error,result.error);worst=maxf(worst,result.error);floor_value=minf(floor_value,result.body_floor)
			final_height=result.body_height;count+=1
			await get_tree().process_frame
		clips[clip]={"error_m":error,"floor_m":floor_value,"final_body_height_m":final_height,"samples":reference.clips[clip].size()}
		print("AMJVIZ_COMBAT_NATIVE_CLIP ",clip," ",clips[clip])
	var reset_sample: Dictionary = reference.clips["Hard stand"][0]
	player.play("DeathStudy");player.seek(player.current_animation_length,true);player.pause()
	player.play("Hard stand");player.seek(reset_sample.time_s,true);player.pause();rig.force_update_all_bone_transforms()
	var reset: Dictionary = checker.compare_sample(meshes,rig,probe,reset_sample.mesh_bounds_blender,reference.body_name)
	worst=maxf(worst,reset.error)
	probe.free();checker.free()
	var file := FileAccess.open(folder+"native_actions.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"glb_sha256":FileAccess.get_sha256(model_path),
		"reference_sha256":reference_hash,"clips":clips,
		"maximum_error_m":worst,"samples":count,"sample_cadence_hz":48,"death_to_idle_reset_error_m":reset.error,
		"scope":"Actual evaluated body/weapon bounds at source key/midpoint cadence; not full120Hz, artistic/contact or original Rigify fidelity"},"  "))
	file.close()
	if worst>=.0005:
		push_error("Animated source export mismatch: %s"%worst);get_tree().quit(1);return
	for clip in ["Walk (1_24)","Run (1_18)","ShootStudy","MeleeStudy","DeathStudy"]:
		assert(clips[clip].floor_m>=-.0005,"New combat clip penetrates floor")
	assert(clips.DeathStudy.final_body_height_m>.15 and clips.DeathStudy.final_body_height_m<.9,"Death did not settle horizontally")
	print("AMJVIZ_COMBAT_NATIVE_EXPORT_PASS samples=",count," error_m=",worst)
	get_tree().quit()
