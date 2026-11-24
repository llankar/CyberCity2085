extends Node3D


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
	add_child(document.generate_scene(state))

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
	camera.look_at(Vector3(0.0, 0.45, 0.0))
	add_child(camera)
	print("CYBERCITY_GODOT_GLTF_OK ", model_path)
	if DisplayServer.get_name() == "headless":
		get_tree().quit()

