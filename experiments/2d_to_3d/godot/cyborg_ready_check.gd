extends Node3D
## Actual deformed mesh bounds versus Blender, including all nine pistol parts.

func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/cyborg_pistol01/"
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(folder+"human.glb",state)==OK)
	var model := document.generate_scene(state,24,false,false)
	add_child(model)
	var player := model.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	var skeleton := model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	assert(skeleton.get_bone_count()==24)
	assert(player.has_animation("CombatReadyStudy"))
	var probe := preload("res://skin_motion_check.gd").new()
	var meshes := {}
	for mesh in model.find_children("*","MeshInstance3D",true,false): meshes[str(mesh.name).replace(".","_").replace(" ","_")]=mesh
	assert(meshes.size()==11)
	var references = JSON.parse_string(FileAccess.get_file_as_string(folder+"native_reference.json"))
	assert(references.size()==9)
	var worst := 0.0
	for sample in references:
		player.play("CombatReadyStudy")
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
	var report := {"status":"PASS","meshes":11,"sampled_poses":9,"maximum_bounds_corner_error_m":worst,"glb_sha256":FileAccess.get_sha256(folder+"human.glb"),"scope":"Actual deformed bounding boxes only; not surface contact, seam or artistic approval"}
	var output := FileAccess.open(folder+"native_ready_validation.json",FileAccess.WRITE)
	assert(output!=null)
	output.store_string(JSON.stringify(report,"  "))
	output.close()
	probe.free()
	print("CYBORG_READY_NATIVE_GEOMETRY_PASS ",JSON.stringify(report))
	get_tree().quit()
