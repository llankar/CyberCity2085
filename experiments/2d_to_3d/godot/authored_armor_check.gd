extends Node3D
func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/unvanquished_human01/"
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(folder+"human_armor.glb",state)==OK)
	var model := document.generate_scene(state)
	add_child(model)
	var skeleton := model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	assert(skeleton.get_bone_count()==122)
	assert(model.find_children("*","AnimationPlayer",true,false).is_empty(),"Static source qualification must not advertise fake actions")
	var meshes := {}
	for mesh in model.find_children("*","MeshInstance3D",true,false):meshes[str(mesh.name).replace(".","_")]=mesh
	assert(meshes.size()==21)
	var reference = JSON.parse_string(FileAccess.get_file_as_string(folder+"static_surface_reference.json"))
	assert(reference.size()==21)
	var probe := preload("res://skin_motion_check.gd").new()
	var errors := {}
	for name_value in reference:
		var mesh := meshes[str(name_value).replace(".","_")] as MeshInstance3D
		var points := probe.skinned_points(mesh,skeleton,1)
		var worst := 0.0
		for source_point in reference[name_value]:
			var expected := Vector3(source_point[0],source_point[2],-source_point[1])
			var nearest := INF
			for point in points:nearest=minf(nearest,point.distance_to(expected))
			worst=maxf(worst,nearest)
		assert(worst<0.0001,"Authored armor rest surface mismatch")
		errors[name_value]=worst
	probe.free()
	var file := FileAccess.open(folder+"native_static_check.json",FileAccess.WRITE)
	assert(file!=null)
	file.store_string(JSON.stringify({"glb_sha256":FileAccess.get_sha256(folder+"human_armor.glb"),"meshes":21,"bones":122,"surface_errors_m":errors,"scope":"Neutral authored mesh/skin correspondence only; animation, fit and final Rook art not accepted"},"  "))
	print("UNV_NATIVE_AUTHORED_ARMOR_REST_OK meshes=21 bones=122")
	get_tree().quit(0)
