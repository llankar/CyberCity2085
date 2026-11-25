extends Node3D
## Compare independent prop attachment to the previously verified skinned prop.

func load_model(path: String) -> Node3D:
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(path, state) == OK)
	var model := document.generate_scene(state, 30, false, false) as Node3D
	add_child(model)
	return model

func directed_distance(first: PackedVector3Array, second: PackedVector3Array) -> float:
	var worst := 0.0
	for point in first:
		var nearest := INF
		for candidate in second: nearest = minf(nearest, point.distance_to(candidate))
		worst = maxf(worst, nearest)
	return worst

func _ready() -> void:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/"
	var body := load_model(root + "einar_bundle02/human_actions.glb")
	var reference := load_model(root + "einar_pistol_fit01_surfaces/human_pistol.glb")
	var weapon := preload("res://pistol_attachment.gd").attach(body)
	var attachment := weapon.get_parent() as BoneAttachment3D
	var skeleton := body.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var source_skeleton := reference.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var player := body.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var source_player := reference.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var originals := {}
	for mesh in reference.find_children("EquippedPistol_*", "MeshInstance3D", true, false):
		originals[str(mesh.name).trim_prefix("EquippedPistol_").replace(".", "_")] = mesh
	var parts := weapon.find_children("*", "MeshInstance3D", true, false)
	assert(parts.size() == 9 and originals.size() == 9)
	player.play("Pistol_Shoot"); source_player.play("Pistol_Shoot")
	player.advance(0); source_player.advance(0)
	var probe := preload("res://skin_motion_check.gd").new()
	var worst := 0.0
	var diagnostic := {}
	for fraction in [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]:
		var time: float = player.get_animation("Pistol_Shoot").length * fraction
		player.seek(time, true); source_player.seek(time, true)
		skeleton.force_update_all_bone_transforms(); source_skeleton.force_update_all_bone_transforms()
		attachment.on_skeleton_update()
		for part in parts:
			var name_value := str(part.name).replace(".", "_")
			assert(originals.has(name_value), name_value)
			var wanted := probe.skinned_points(originals[name_value], source_skeleton, 1)
			var actual := PackedVector3Array()
			for surface in range(part.mesh.get_surface_count()):
				var vertices: PackedVector3Array = part.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]
				for vertex in vertices: actual.append(part.global_transform * vertex)
			# Exporting the fitted prop bakes rotations into normals and may reorder
			# split vertices. Compare both complete point sets, not arbitrary indices.
			var error := maxf(directed_distance(actual, wanted), directed_distance(wanted, actual))
			if error > worst:
				worst = error
				diagnostic = {"part": name_value, "fraction": fraction, "weapon_transform": str(weapon.global_transform), "bone_index": attachment.bone_idx}
	print("RUNTIME_PISTOL_PROBE ", worst, " ", JSON.stringify(diagnostic))
	assert(worst < 0.0005, "Runtime pistol differs from measured fitted prop")
	probe.free()
	var output := FileAccess.open(root + "einar_bundle02/native_runtime_pistol.json", FileAccess.WRITE)
	assert(output != null)
	output.store_string(JSON.stringify({"parts": 9, "times": 6, "max_bidirectional_vertex_set_distance_m": worst, "scope": "Complete vertex-set attachment correspondence; no trigger/support-hand artistic acceptance"}, "  "))
	print("EINAR_RUNTIME_PISTOL_ATTACHMENT_OK ", worst)
	get_tree().quit(0)
