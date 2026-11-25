extends Node3D
## Actual deformed mesh bounds versus Blender, including all nine pistol parts.

func _ready() -> void:
	var fire := "--fire-study" in OS.get_cmdline_user_args()
	var clip := "PistolFireStudy" if fire else "CombatReadyStudy"
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/"+("cyborg_fire01/" if fire else "cyborg_pistol01/")
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
	assert(meshes.size()==11)
	var references = JSON.parse_string(FileAccess.get_file_as_string(folder+"native_reference.json"))
	assert(references.size()==(19 if fire else 9))
	var worst := 0.0
	for sample in references:
		player.play(clip)
		player.seek(sample.time_s,true)
		player.pause()
		skeleton.force_update_all_bone_transforms()
		for name_value in sample.mesh_bounds_blender:
			assert(meshes.has(name_value),name_value)
			var mesh: MeshInstance3D = meshes[name_value]
			var points := probe.skinned_points(mesh,skeleton,1,true)
			assert(not points.is_empty())
			var actual := AABB(points[0],Vector3.ZERO)
			for point in points:actual=actual.expand(point)
			var expected := AABB()
			var first := true
			var box: Array = sample.mesh_bounds_blender[name_value]
			for x in [box[0][0],box[1][0]]:
				for y in [box[0][1],box[1][1]]:
					for z in [box[0][2],box[1][2]]:
						var corner := Vector3(x,z,-y)
						expected=AABB(corner,Vector3.ZERO) if first else expected.expand(corner)
						first=false
			worst=maxf(worst,maxf(actual.position.distance_to(expected.position),actual.end.distance_to(expected.end)))
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
	var report := {"status":"PASS","meshes":11,"sampled_poses":references.size(),"maximum_bounds_corner_error_m":worst,"fire_to_ready_position_reset_error_m":reset_error,"actual_slide_travel_m":slide_travel,"glb_sha256":FileAccess.get_sha256(folder+"human.glb"),"scope":"Actual deformed bounding boxes only; not surface contact, seam or artistic approval"}
	var output := FileAccess.open(folder+("native_fire_validation.json" if fire else "native_ready_validation.json"),FileAccess.WRITE)
	assert(output!=null)
	output.store_string(JSON.stringify(report,"  "))
	output.close()
	probe.free()
	print("CYBORG_FIRE_NATIVE_GEOMETRY_PASS " if fire else "CYBORG_READY_NATIVE_GEOMETRY_PASS ",JSON.stringify(report))
	get_tree().quit()
