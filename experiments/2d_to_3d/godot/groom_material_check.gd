extends Node3D
func _ready() -> void:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/einar_groom_occlusion03/"
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(root + "authored_groom.glb", state) == OK)
	var model := document.generate_scene(state)
	add_child(model)
	preload("res://groom_attachment.gd").enable_vertex_palette(model)
	var evidence := {}
	for mesh in model.find_children("*", "MeshInstance3D", true, false):
		var material := mesh.get_active_material(0) as StandardMaterial3D
		assert(material.vertex_color_use_as_albedo and not material.vertex_color_is_srgb)
		var colors: PackedColorArray = mesh.mesh.surface_get_arrays(0)[Mesh.ARRAY_COLOR]
		assert(colors.size() > 100)
		var mean := 0.0
		for color in colors: mean += (color.r + color.g + color.b) / 3.0
		mean /= colors.size()
		assert(mean > 0 and mean < 0.95, "Palette must not collapse to black/white")
		evidence[str(mesh.name)] = {"colors": colors.size(), "mean_rgb": mean, "vertex_color_as_albedo": material.vertex_color_use_as_albedo, "base_color": str(material.albedo_color)}
		print("GROOM_COLOR_ROUTE ", mesh.name, " ", JSON.stringify(evidence[str(mesh.name)]))
	var output := FileAccess.open(root + "native_material_check.json", FileAccess.WRITE)
	output.store_string(JSON.stringify(evidence, "  "))
	print("AUTHORED_GROOM_PALETTE_GATE_OK")
	get_tree().quit(0)
