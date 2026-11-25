extends Node3D

var equipment_meshes: Array[Node3D] = []

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_B:
		for mesh in equipment_meshes:
			mesh.visible = not mesh.visible


func _ready() -> void:
	if "--msaa4" in OS.get_cmdline_user_args(): get_viewport().msaa_3d = Viewport.MSAA_4X
	var model_path := "E:/CyberCity2085-3d-lab/outputs/blender/crate/crate.glb"
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--model="):
			model_path = argument.trim_prefix("--model=")
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	var error := document.append_from_file(model_path, state)
	if error != OK:
		push_error("Could not load experimental GLB: %s (%s)" % [model_path, error])
		get_tree().quit(2)
		return
	var authored_human := (model_path.contains("/unvanquished_") or model_path.contains("/scanned_armor_head01/") or model_path.contains("/scanned_armor_hair01/") or model_path.contains("/scanned_armor_shoot01/")) and (model_path.ends_with("/human_actions.glb") or model_path.ends_with("/human_pistol.glb"))
	var model := document.generate_scene(state, 120 if authored_human else 30, false, false)
	add_child(model)
	if "--gltf-uniform-clearcoat" in OS.get_cmdline_user_args():
		var coats := preload("res://uniform_clearcoat.gd").new().apply_uniform_coats(state,model)
		print("UNIFORM_GLTF_CLEARCOAT_APPLIED ",coats.size())
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--model-scale="):
			var unit_scale := argument.trim_prefix("--model-scale=").to_float()
			assert(unit_scale > 0 and unit_scale <= 1000)
			model.scale *= unit_scale
		if argument.begins_with("--model-vertical-offset="):
			model.position.y = argument.trim_prefix("--model-vertical-offset=").to_float()
	if "--attach-pistol" in OS.get_cmdline_user_args(): preload("res://pistol_attachment.gd").attach(model)
	if "--attach-rocketbox-pistol" in OS.get_cmdline_user_args(): preload("res://rocketbox_pistol_attachment.gd").attach(model)
	if "--rocketbox-hair" in OS.get_cmdline_user_args(): preload("res://rocketbox_hair_attachment.gd").attach(model)
	if "--attach-groom" in OS.get_cmdline_user_args():
		var groom_folder := "einar_groom_full02" if "--full-groom" in OS.get_cmdline_user_args() else "einar_groom02"
		if "--layered-groom" in OS.get_cmdline_user_args(): groom_folder += "_layered"
		if "--occluded-groom" in OS.get_cmdline_user_args(): groom_folder = "einar_groom_occlusion03"
		if "--lod-groom" in OS.get_cmdline_user_args(): groom_folder = "einar_groom02_layered_lod"
		preload("res://groom_attachment.gd").attach(model, groom_folder)
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--rotate-x="):
			model.rotation_degrees.x = argument.trim_prefix("--rotate-x=").to_float()
	var requested_clip := "FittingStressTest"
	var sample_fraction := 1.0
	var sample_clip := "--sample-clip" in OS.get_cmdline_user_args()
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--clip="):
			requested_clip = argument.trim_prefix("--clip=")
			sample_clip = true
		if argument.begins_with("--clip-fraction="):
			sample_fraction = clampf(argument.trim_prefix("--clip-fraction=").to_float(), 0.0, 1.0)
	if sample_clip:
		var players := model.find_children("*", "AnimationPlayer", true, false)
		if players.is_empty():
			push_error("No imported animation player")
			get_tree().quit(9)
			return
		var player := players[0] as AnimationPlayer
		var clips := player.get_animation_list()
		print("CYBERCITY_IMPORTED_CLIPS ", clips)
		var selected := ""
		for clip in clips:
			if clip == requested_clip or clip.get_file() == requested_clip:
				selected = clip
				break
		if selected.is_empty():
			push_error("Requested clip missing; available: " + str(clips))
			get_tree().quit(10)
			return
		player.play(selected)
		player.seek(player.get_animation(selected).length * sample_fraction, true)
		player.pause()
		print("CYBERCITY_IMPORTED_CLIP_SAMPLED ", selected)
	if "--stress-pose" in OS.get_cmdline_user_args():
		var rigs := model.find_children("*", "Skeleton3D", true, false)
		if rigs.size() != 1:
			get_tree().quit(7)
			return
		var rig := rigs[0] as Skeleton3D
		var rotations := {"lowerarm_l": 1.1, "lowerarm_r": 0.9, "thigh_l": -0.65, "calf_l": 0.8}
		for bone_name in rotations:
			var bone_index := rig.find_bone(bone_name)
			if bone_index < 0:
				push_error("Missing pose bone: " + bone_name)
				get_tree().quit(8)
				return
			rig.set_bone_pose_rotation(bone_index, rig.get_bone_pose_rotation(bone_index) * Quaternion(Vector3.RIGHT, rotations[bone_name]))
		rig.force_update_all_bone_transforms()
		print("CYBERCITY_STRESS_POSE_APPLIED bones=4")
	if not "--raw-textures" in OS.get_cmdline_user_args():
		var texture_cache: Dictionary = {}
		var generated := 0
		for mesh in model.find_children("*", "MeshInstance3D", true, false):
			for surface in range(mesh.mesh.get_surface_count()):
				var source_material: Material = mesh.get_active_material(surface)
				if source_material is StandardMaterial3D:
					var filtered := source_material.duplicate() as StandardMaterial3D
					filtered.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
					for slot in [BaseMaterial3D.TEXTURE_ALBEDO, BaseMaterial3D.TEXTURE_NORMAL, BaseMaterial3D.TEXTURE_METALLIC, BaseMaterial3D.TEXTURE_ROUGHNESS]:
						var texture := filtered.get_texture(slot)
						if texture:
							var cache_key := "%s:%s" % [texture.get_instance_id(), slot == BaseMaterial3D.TEXTURE_NORMAL]
							if texture_cache.has(cache_key):
								filtered.set_texture(slot, texture_cache[cache_key])
								continue
							var pixels := texture.get_image()
							if pixels and not pixels.has_mipmaps():
								pixels.generate_mipmaps(slot == BaseMaterial3D.TEXTURE_NORMAL)
								var mip_texture := ImageTexture.create_from_image(pixels)
								texture_cache[cache_key] = mip_texture
								filtered.set_texture(slot, mip_texture)
								generated += 1
					mesh.set_surface_override_material(surface, filtered)
		print("CYBERCITY_TEXTURE_SETUP_OK generated=", generated)
	if "--unlit-diagnostic" in OS.get_cmdline_user_args():
		for mesh in model.find_children("*", "MeshInstance3D", true, false):
			for surface in range(mesh.mesh.get_surface_count()):
				var material: Material = mesh.get_active_material(surface)
				if material is StandardMaterial3D:
					var diagnostic := material.duplicate() as StandardMaterial3D
					diagnostic.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
					mesh.set_surface_override_material(surface, diagnostic)
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--hide-material="):
			var hidden_name := argument.trim_prefix("--hide-material=")
			for mesh in model.find_children("*", "MeshInstance3D", true, false):
				for surface in range(mesh.mesh.get_surface_count()):
					var material := mesh.get_active_material(surface) as StandardMaterial3D
					if material and material.resource_name == hidden_name:
						var hidden := material.duplicate() as StandardMaterial3D
						hidden.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
						hidden.albedo_color.a = 0
						mesh.set_surface_override_material(surface, hidden)
	for mesh in model.find_children("*", "MeshInstance3D", true, false):
		if "Boot" in mesh.name:
			equipment_meshes.append(mesh)
	if "--validate-rig" in OS.get_cmdline_user_args():
		var skeletons := model.find_children("*", "Skeleton3D", true, false)
		var meshes := model.find_children("*", "MeshInstance3D", true, false)
		var skinned := 0
		for mesh in meshes:
			if mesh.skin != null and mesh.get_node_or_null(mesh.skeleton) is Skeleton3D:
				skinned += 1
		if skeletons.size() != 1 or skeletons[0].get_bone_count() != 53 or skinned < 10:
			push_error("Rig validation failed: skeletons=%s skinned=%s" % [skeletons.size(), skinned])
			get_tree().quit(3)
			return
		print("CYBERCITY_RIG_OK bones=53 meshes=%s skinned=%s" % [meshes.size(), skinned])
	if "--test-equipment" in OS.get_cmdline_user_args():
		if equipment_meshes.size() != 6:
			get_tree().quit(4)
			return
		var key := InputEventKey.new()
		key.keycode = KEY_B
		key.pressed = true
		_unhandled_key_input(key)
		for mesh in equipment_meshes:
			assert(not mesh.visible)
		_unhandled_key_input(key)
		for mesh in equipment_meshes:
			assert(mesh.visible)
		print("CYBERCITY_EQUIPMENT_TOGGLE_OK parts=6")

	var environment := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("07101b")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("4edff0")
	env.ambient_light_energy = 0.35
	if "--neutral" in OS.get_cmdline_user_args():
		env.ambient_light_color = Color.WHITE
		env.background_color = Color(0.18, 0.18, 0.18)
	environment.environment = env
	add_child(environment)

	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55.0, -35.0, 0.0)
	light.light_energy = 1.4
	light.shadow_enabled = true
	if "--no-shadows" in OS.get_cmdline_user_args():
		light.shadow_enabled = false
	add_child(light)

	var camera := Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 2.4
	camera.position = Vector3(1.8, 1.5, 1.8)
	add_child(camera)
	var bounds := AABB()
	var first_bound := true
	var skin_probe := preload("res://skin_motion_check.gd").new()
	for mesh in model.find_children("*", "MeshInstance3D", true, false):
		if mesh.skin != null and mesh.get_node_or_null(mesh.skeleton) is Skeleton3D:
			var skeleton := mesh.get_node(mesh.skeleton) as Skeleton3D
			skeleton.force_update_all_bone_transforms()
			for point in skin_probe.skinned_points(mesh, skeleton, 1, true):
				bounds = AABB(point, Vector3.ZERO) if first_bound else bounds.expand(point)
				first_bound = false
			continue
		var mesh_bounds: AABB = mesh.global_transform * mesh.get_aabb()
		bounds = mesh_bounds if first_bound else bounds.merge(mesh_bounds)
		first_bound = false
	skin_probe.free()
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--bounds-file="):
			var evidence = JSON.parse_string(FileAccess.get_file_as_string(argument.trim_prefix("--bounds-file=")))
			if not evidence is Dictionary or evidence.is_empty():
				push_error("Invalid animated bounds evidence")
				get_tree().quit(11)
				return
			first_bound = true
			for clip_data in evidence.values():
				var envelope = clip_data["world_envelope"]
				# Blender Z-up to glTF/Godot Y-up, including the flipped depth axis.
				var low := Vector3(envelope[0][0], envelope[0][2], -envelope[1][1])
				var high := Vector3(envelope[1][0], envelope[1][2], -envelope[0][1])
				var clip_bounds := AABB(low, high - low)
				bounds = clip_bounds if first_bound else bounds.merge(clip_bounds)
				first_bound = false
			camera.size = bounds.size.length() * 1.15
			print("CYBERCITY_ANIMATED_BOUNDS_OK ", bounds)
	var target := bounds.get_center() if not first_bound else Vector3(0.0, 0.45, 0.0)
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--focus-height="): target.y = argument.trim_prefix("--focus-height=").to_float()
	# Keep the viewing direction independent of imported model height/units.
	camera.position = target + Vector3(1.8, 1.05, 1.8)
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--view="):
			match argument.trim_prefix("--view="):
				"front": camera.position = target + Vector3(0, 0, 3)
				"side": camera.position = target + Vector3(3, 0, 0)
				"back": camera.position = target + Vector3(0, 0, -3)
				_:
					push_error("Unknown neutral view")
					get_tree().quit(7)
					return
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--camera-distance="):
			var distance := argument.trim_prefix("--camera-distance=").to_float()
			assert(is_finite(distance) and distance > 0.1 and distance <= 1000.0)
			camera.position = target + (camera.position-target).normalized()*distance
	camera.look_at(target)
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--ortho-size="):
			camera.size = clampf(argument.trim_prefix("--ortho-size=").to_float(), 0.05, 1000.0)
	print("CYBERCITY_GODOT_GLTF_OK ", model_path)
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--capture="):
			var output := argument.trim_prefix("--capture=")
			if not output.begins_with("E:/CyberCity2085-3d-lab/"):
				get_tree().quit(5)
				return
			await RenderingServer.frame_post_draw
			await RenderingServer.frame_post_draw
			var result := get_viewport().get_texture().get_image().save_png(output)
			print("CYBERCITY_CAPTURE_RESULT ", result)
			get_tree().quit(0 if result == OK else 6)
			return
	if DisplayServer.get_name() == "headless":
		get_tree().quit()

