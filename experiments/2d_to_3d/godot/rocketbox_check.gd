extends Node3D

func require(condition: bool, message: String) -> bool:
	if not condition:
		push_error(message)
		get_tree().quit(2)
	return condition

func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03/"
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	if not require(document.append_from_file(folder + "character_dielectric.glb", state) == OK, "GLB import failed"): return
	var model := document.generate_scene(state, 30, false, false)
	add_child(model)
	var rigs := model.find_children("*", "Skeleton3D", true, false)
	var meshes := model.find_children("*", "MeshInstance3D", true, false)
	if not require(rigs.size() == 1 and meshes.size() == 1, "Unexpected candidate hierarchy"): return
	var rig := rigs[0] as Skeleton3D
	var mesh := meshes[0] as MeshInstance3D
	if not require(rig.get_bone_count() == 80 and mesh.skin != null and mesh.get_node_or_null(mesh.skeleton) == rig, "Skin binding failed"): return
	if not require(mesh.mesh.get_surface_count() == 5 and mesh.mesh.get_blend_shape_count() == 175, "Authored surfaces/morphs lost"): return
	var triangles := 0
	var textures := {}
	for surface in range(5):
		var arrays := mesh.mesh.surface_get_arrays(surface)
		triangles += arrays[Mesh.ARRAY_INDEX].size() / 3
		var material := mesh.get_active_material(surface) as StandardMaterial3D
		if not require(material != null and material.metallic == 0, "Dielectric candidate material lost"): return
		for slot in [BaseMaterial3D.TEXTURE_ALBEDO, BaseMaterial3D.TEXTURE_NORMAL]:
			var texture := material.get_texture(slot)
			if not require(texture != null and texture.get_width() >= 1024, "Original texture missing"): return
			textures[texture.get_instance_id()] = texture.get_size()
		var bones: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
		var weights: PackedFloat32Array = arrays[Mesh.ARRAY_WEIGHTS]
		if not require(bones.size() == weights.size() and not bones.is_empty(), "Weight arrays absent"): return
		for index in range(weights.size()):
			if not require(weights[index] >= 0 and is_finite(weights[index]) and bones[index] < mesh.skin.get_bind_count(), "Invalid skin influence"): return
	if not require(triangles == 15517 and textures.size() == 10, "Geometry/texture coverage changed"): return
	rig.force_update_all_bone_transforms()
	var probe := preload("res://skin_motion_check.gd").new()
	var points := probe.skinned_points(mesh, rig, 1)
	probe.free()
	var bounds := AABB(points[0], Vector3.ZERO)
	for point in points:
		if not require(point.is_finite(), "Nonfinite skinned point"): return
		bounds = bounds.expand(point)
	if not require(absf(bounds.size.y - 1.8503574) < 0.001, "Rendered skin scale differs from Blender"): return
	var evidence := {"bones":80,"surfaces":5,"triangles":triangles,"facial_morphs":175,"albedo_normal_textures":textures.size(),"height_m":bounds.size.y,"artistic_acceptance":false}
	var output := FileAccess.open(folder + "native_check.json", FileAccess.WRITE)
	output.store_string(JSON.stringify(evidence, "  "))
	print("ROCKETBOX_NATIVE_ASSET_OK ", JSON.stringify(evidence))
	get_tree().quit(0)
