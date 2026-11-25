extends Node3D
func _ready() -> void:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03/"
	var report = JSON.parse_string(FileAccess.get_file_as_string(root+"accessories01/extraction_report.json"))
	var audit = JSON.parse_string(FileAccess.get_file_as_string(root+"component_audit.json"))
	var source_bounds := {}
	for part in audit.components: source_bounds[str(int(part.component))] = part.bounds
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	assert(doc.append_from_file(root+"accessories01/accessories.glb",state) == OK)
	var model := doc.generate_scene(state)
	add_child(model)
	var meshes := model.find_children("*", "MeshInstance3D", true, false)
	assert(meshes.size() == report.parts.size() and meshes.size() == 34)
	var triangles := 0
	var worst := 0.0
	for mesh_node in meshes:
		var mesh := mesh_node as MeshInstance3D
		assert(mesh.skin == null)
		var key := str(mesh.name).trim_prefix("AuthoredProp_")
		assert(source_bounds.has(key))
		var original: Array = source_bounds[key]
		var low := Vector3(original[0][0],original[0][2],-original[1][1])
		var high := Vector3(original[1][0],original[1][2],-original[0][1])
		var bounds := AABB()
		var first := true
		for surface in range(mesh.mesh.get_surface_count()):
			var arrays := mesh.mesh.surface_get_arrays(surface)
			triangles += arrays[Mesh.ARRAY_INDEX].size()/3
			assert(arrays[Mesh.ARRAY_TEX_UV].size() == arrays[Mesh.ARRAY_VERTEX].size())
			var material := mesh.get_active_material(surface) as StandardMaterial3D
			assert(material and material.get_texture(BaseMaterial3D.TEXTURE_ALBEDO) != null)
			for vertex in arrays[Mesh.ARRAY_VERTEX]:
				var point: Vector3 = mesh.global_transform * vertex
				bounds = AABB(point,Vector3.ZERO) if first else bounds.expand(point)
				first = false
		worst = maxf(worst,bounds.position.distance_to(low))
		worst = maxf(worst,bounds.end.distance_to(high))
	assert(triangles == 5500 and worst < 0.001)
	var output := FileAccess.open(root+"accessories01/native_check.json",FileAccess.WRITE)
	output.store_string(JSON.stringify({"parts":34,"triangles":triangles,"max_bounds_error_m":worst,"static_extraction_only":true},"  "))
	print("ROCKETBOX_ACCESSORY_SOURCE_BOUNDS_OK ",worst)
	get_tree().quit(0)
