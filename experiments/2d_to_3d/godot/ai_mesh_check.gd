extends Node
## Native import evidence only: no artistic or performance acceptance implied.

func _ready() -> void:
	var model := ""
	var evidence := ""
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--model="):
			model = argument.trim_prefix("--model=")
		if argument.begins_with("--evidence="):
			evidence = argument.trim_prefix("--evidence=")
	if not model.begins_with("E:/CyberCity2085-3d-lab/") or not evidence.begins_with("E:/CyberCity2085-3d-lab/"):
		push_error("Experimental model and evidence must stay on E:")
		get_tree().quit(1)
		return
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	var error := document.append_from_file(model, state)
	if error != OK:
		push_error("GLB import failed: %s" % error)
		get_tree().quit(1)
		return
	var scene := document.generate_scene(state)
	add_child(scene)
	var count := 0
	var triangles := 0
	var materials := 0
	for node in scene.find_children("*", "MeshInstance3D", true, false):
		var mesh: Mesh = node.mesh
		if mesh == null:
			continue
		count += 1
		triangles += int(mesh.get_faces().size() / 3)
		for surface in mesh.get_surface_count():
			if mesh.surface_get_material(surface) != null:
				materials += 1
	if count == 0 or triangles < 4:
		push_error("Imported GLB has no usable mesh")
		get_tree().quit(1)
		return
	var report := {"status": "PASS", "engine": Engine.get_version_info().string,
		"source": model, "source_sha256": FileAccess.get_sha256(model),
		"mesh_objects": count, "triangles": triangles, "material_surfaces": materials,
		"artistic_acceptance": "NOT VERIFIED"}
	var file := FileAccess.open(evidence, FileAccess.WRITE)
	if file == null:
		get_tree().quit(1)
		return
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("AI_MESH_NATIVE_IMPORT_PASS ", JSON.stringify(report))
	get_tree().quit()
