extends Node3D
## Actual deformed mesh bounds versus Blender, including all nine pistol parts.

func compare_sample(meshes: Dictionary,skeleton: Skeleton3D,probe: Node,boxes: Dictionary) -> Dictionary:
	var worst := 0.0
	var floor_value := INF
	var body_height := 0.0
	for name_value in boxes:
		assert(meshes.has(name_value),name_value)
		var mesh: MeshInstance3D = meshes[name_value]
		var points: PackedVector3Array = probe.skinned_points(mesh,skeleton,1,true)
		assert(not points.is_empty())
		var actual := AABB(points[0],Vector3.ZERO)
		for point in points:actual=actual.expand(point)
		floor_value=minf(floor_value,actual.position.y)
		if name_value=="char1":body_height=actual.size.y
		var expected := AABB()
		var first := true
		var box: Array = boxes[name_value]
		for x in [box[0][0],box[1][0]]:
			for y in [box[0][1],box[1][1]]:
				for z in [box[0][2],box[1][2]]:
					var corner := Vector3(x,z,-y)
					expected=AABB(corner,Vector3.ZERO) if first else expected.expand(corner)
					first=false
		worst=maxf(worst,maxf(actual.position.distance_to(expected.position),actual.end.distance_to(expected.end)))
	return {"error":worst,"floor":floor_value,"body_height":body_height}

func _ready() -> void:
	var jacket_study := "--authored-jacket-study" in OS.get_cmdline_user_args()
	var pouch_study := "--pouch-study" in OS.get_cmdline_user_args() or jacket_study
	var skin_normal_study := "--skin-normal-study" in OS.get_cmdline_user_args() or pouch_study
	var single_neck_study := "--single-neck-study" in OS.get_cmdline_user_args() or skin_normal_study
	var undercut_study := "--undercut-study" in OS.get_cmdline_user_args() or single_neck_study
	var run_study := "--run-clearance-study" in OS.get_cmdline_user_args() or undercut_study
	var neck_study := "--neck-uv-study" in OS.get_cmdline_user_args() or run_study
	var quiff_study := "--quiff-study" in OS.get_cmdline_user_args() or neck_study
	var head_study := "--head-fit-study" in OS.get_cmdline_user_args() or quiff_study
	var material_study := "--rook-material-study" in OS.get_cmdline_user_args()
	var actions := "--actions-study" in OS.get_cmdline_user_args() or material_study or head_study
	var fire := "--fire-study" in OS.get_cmdline_user_args() or actions
	var clip := "PistolFireStudy" if fire else "CombatReadyStudy"
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/"+("rook_material01/" if material_study else ("cyborg_actions01/" if actions else ("cyborg_fire01/" if fire else "cyborg_pistol01/")))
	if head_study:folder="E:/CyberCity2085-3d-lab/generated/phase2/rook_head_fit126/"
	if quiff_study:folder="E:/CyberCity2085-3d-lab/generated/phase2/rook_hair127/"
	if neck_study:folder="E:/CyberCity2085-3d-lab/generated/phase2/rook_neck_uv128/"
	if run_study:folder="E:/CyberCity2085-3d-lab/generated/phase2/rook_run129/"
	if undercut_study:folder="E:/CyberCity2085-3d-lab/generated/phase2/rook_undercut133/"
	if single_neck_study:folder="E:/CyberCity2085-3d-lab/generated/phase2/rook_single_neck138/"
	if skin_normal_study:folder="E:/CyberCity2085-3d-lab/generated/phase2/rook_normal_strength139/"
	if pouch_study:folder="E:/CyberCity2085-3d-lab/generated/phase2/rook_pouches140/"
	if jacket_study:folder="E:/CyberCity2085-3d-lab/generated/phase2/rook_diesel_replacement141/"
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(folder+"human.glb",state)==OK)
	var model := document.generate_scene(state,24,false,false)
	add_child(model)
	var player := model.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	var skeleton := model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	assert(skeleton.get_bone_count()==(25 if fire else 24))
	assert(player.has_animation(clip))
	var probe := preload("res://skin_motion_check.gd").new()
	var meshes := {}
	for mesh in model.find_children("*","MeshInstance3D",true,false): meshes[str(mesh.name).replace(".","_").replace(" ","_")]=mesh
	assert(meshes.size()==(16 if jacket_study else (15 if pouch_study else (13 if quiff_study else (12 if head_study else 11)))))
	var references = JSON.parse_string(FileAccess.get_file_as_string(folder+"native_reference.json"))
	assert(references.size()==(6 if actions else (19 if fire else 9)))
	var sets: Dictionary = references if actions else {clip:references}
	var worst := 0.0
	var count := 0
	var floors := {}
	var clip_errors := {}
	var final_death_height := 0.0
	for selected_clip in sets:
		assert(player.has_animation(selected_clip))
		floors[selected_clip]=INF
		clip_errors[selected_clip]={"error_m":0.0,"time_s":0.0,"integer_key_error_m":0.0}
		for sample in sets[selected_clip]:
			player.play(selected_clip)
			player.seek(sample.time_s,true)
			player.pause()
			skeleton.force_update_all_bone_transforms()
			var measured := compare_sample(meshes,skeleton,probe,sample.mesh_bounds_blender)
			worst=maxf(worst,measured.error)
			if measured.error>clip_errors[selected_clip].error_m:
				clip_errors[selected_clip].error_m=measured.error
				clip_errors[selected_clip].time_s=sample.time_s
			if absf(sample.time_s*24-roundf(sample.time_s*24))<.0001:clip_errors[selected_clip].integer_key_error_m=maxf(clip_errors[selected_clip].integer_key_error_m,measured.error)
			floors[selected_clip]=minf(floors[selected_clip],measured.floor)
			if selected_clip=="DeathStudy":final_death_height=measured.body_height
			count+=1
		if selected_clip in ["MeleeStudy","DeathStudy"] or (run_study and selected_clip=="run"):assert(floors[selected_clip]>=-.0001,"Retargeted mesh penetrates floor: %s"%floors[selected_clip])
		print("CYBORG_CLIP_NATIVE_BOUNDS ",selected_clip," floor_m=",floors[selected_clip]," error=",clip_errors[selected_clip])
	if actions:assert(final_death_height>.15 and final_death_height<.9,"Death did not settle horizontally")
	var diagnostic := FileAccess.open(folder+"native_bounds_diagnostic.json",FileAccess.WRITE)
	diagnostic.store_string(JSON.stringify({"clips":clip_errors,"floors":floors,"maximum_error_m":worst,"glb_sha256":FileAccess.get_sha256(folder+"human.glb")},"  "))
	diagnostic.close()
	assert(worst<.0005,"Native mesh bounds mismatch: %s"%worst)
	var reset_error := 0.0
	var slide_travel := 0.0
	if fire:
		player.play(clip)
		player.seek(0,true)
		skeleton.force_update_all_bone_transforms()
		var start: Array[Transform3D] = []
		for bone in range(25):start.append(skeleton.get_bone_global_pose(bone))
		player.seek(8.0/24,true)
		skeleton.force_update_all_bone_transforms()
		var slide_index := skeleton.find_bone("PistolSlide")
		var hand_index := skeleton.find_bone("RightHand")
		assert(slide_index>=0 and hand_index>=0)
		slide_travel=(skeleton.global_transform*skeleton.get_bone_global_pose(slide_index).origin).distance_to(skeleton.global_transform*skeleton.get_bone_global_pose(hand_index).origin)
		assert(absf(slide_travel-.02)<.0001,"Actual slide travel differs from20mm: %s"%slide_travel)
		player.play("CombatReadyStudy")
		player.seek(0,true)
		skeleton.force_update_all_bone_transforms()
		for bone in range(25):reset_error=maxf(reset_error,start[bone].origin.distance_to(skeleton.get_bone_global_pose(bone).origin))
		assert(reset_error<.0001,"Fire-to-ready reset failed: %s"%reset_error)
	var report := {"status":"PASS","meshes":meshes.size(),"sampled_poses":count,"minimum_mesh_floor_by_clip_m":floors,"final_death_body_height_m":final_death_height,"maximum_bounds_corner_error_m":worst,"fire_to_ready_position_reset_error_m":reset_error,"actual_slide_travel_m":slide_travel,"glb_sha256":FileAccess.get_sha256(folder+"human.glb"),"scope":"Actual deformed bounding boxes only; not surface contact, seam or artistic approval"}
	var output := FileAccess.open(folder+("native_actions_validation.json" if actions else ("native_fire_validation.json" if fire else "native_ready_validation.json")),FileAccess.WRITE)
	assert(output!=null)
	output.store_string(JSON.stringify(report,"  "))
	output.close()
	probe.free()
	print("CYBORG_ACTIONS_NATIVE_GEOMETRY_PASS " if actions else ("CYBORG_FIRE_NATIVE_GEOMETRY_PASS " if fire else "CYBORG_READY_NATIVE_GEOMETRY_PASS "),JSON.stringify(report))
	get_tree().quit()
