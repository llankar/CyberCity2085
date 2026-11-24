extends Node3D

var equipment_meshes: Array[Node3D] = []

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_B:
		for mesh in equipment_meshes:
			mesh.visible = not mesh.visible


func _ready() -> void:
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
	var model := document.generate_scene(state)
	add_child(model)
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

	var environment := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("07101b")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("4edff0")
	env.ambient_light_energy = 0.35
	environment.environment = env
	add_child(environment)

	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55.0, -35.0, 0.0)
	light.light_energy = 1.4
	light.shadow_enabled = true
	add_child(light)

	var camera := Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 2.4
	camera.position = Vector3(1.8, 1.5, 1.8)
	add_child(camera)
	camera.look_at(Vector3(0.0, 0.45, 0.0))
	print("CYBERCITY_GODOT_GLTF_OK ", model_path)
	if DisplayServer.get_name() == "headless":
		get_tree().quit()

