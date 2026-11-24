extends Node3D
## Independent scale-review stage. External files remain outside the game runtime.

var camera: Camera3D
var hud: Label
var subjects: Array[Node3D] = []
var selected := 0
var yaw := 0.65
var elevation := 0.6
var target := Vector3(0, 1.0, 0)
var orbiting := false
var orbit_mode := false
var clip_status := "Human: static fitting model; action clips unavailable"

func load_subject(path: String, position_value: Vector3) -> bool:
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	if document.append_from_file(path, state) != OK:
		push_error("Missing comparison subject: " + path)
		return false
	var subject := document.generate_scene(state)
	add_child(subject)
	subject.position = position_value
	subjects.append(subject)
	for mesh in subject.find_children("*", "MeshInstance3D", true, false):
		for index in range(mesh.mesh.get_surface_count()):
			var material = mesh.get_active_material(index)
			if material is StandardMaterial3D:
				var copy := material.duplicate() as StandardMaterial3D
				copy.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
				for slot in [BaseMaterial3D.TEXTURE_ALBEDO, BaseMaterial3D.TEXTURE_NORMAL]:
					var texture := copy.get_texture(slot)
					if texture:
						var pixels := texture.get_image()
						if pixels and not pixels.has_mipmaps():
							pixels.generate_mipmaps(slot == BaseMaterial3D.TEXTURE_NORMAL)
							copy.set_texture(slot, ImageTexture.create_from_image(pixels))
				mesh.set_surface_override_material(index, copy)
	return true

func _ready() -> void:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/"
	var human_file := "authored_outfit_realtime.glb" if "--realtime" in OS.get_cmdline_user_args() else "authored_outfit.glb"
	if not load_subject(root + "authored_tactical01/" + human_file, Vector3(-1.6, 0, 0)):
		get_tree().quit(2)
		return
	if not load_subject(root + "george_tactical/george_tactical.glb", Vector3(1.6, 0, 0)):
		get_tree().quit(2)
		return
	var world := WorldEnvironment.new()
	world.environment = Environment.new()
	world.environment.background_mode = Environment.BG_COLOR
	world.environment.background_color = Color(0.18, 0.18, 0.18)
	world.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	world.environment.ambient_light_color = Color.WHITE
	world.environment.ambient_light_energy = 0.4
	add_child(world)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, -35, 0)
	sun.light_energy = 1.0
	sun.shadow_enabled = true
	add_child(sun)
	for x in range(-4, 5):
		for z in range(-3, 4):
			var tile := MeshInstance3D.new()
			var box := BoxMesh.new()
			box.size = Vector3(0.98, 0.04, 0.98)
			tile.mesh = box
			tile.position = Vector3(x, -0.035, z)
			var material := StandardMaterial3D.new()
			material.albedo_color = Color(0.23, 0.23, 0.23) if (x + z) % 2 == 0 else Color(0.28, 0.28, 0.28)
			material.roughness = 0.9
			tile.material_override = material
			add_child(tile)
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 7.8
	add_child(camera)
	update_camera()
	var layer := CanvasLayer.new()
	add_child(layer)
	hud = Label.new()
	hud.position = Vector2(20, 16)
	hud.add_theme_font_size_override("font_size", 19)
	layer.add_child(hud)
	selected = 1
	play_clip("Idle")
	selected = 0
	clip_status = "Human: static fitting model; action clips unavailable"
	print("COMPARISON_STAGE_LOADED subjects=2 tile_width_m=1")
	if "--self-test" in OS.get_cmdline_user_args():
		var key := InputEventKey.new()
		key.pressed = true
		key.keycode = KEY_TAB
		_unhandled_input(key)
		assert(selected == 1)
		key.keycode = KEY_2
		_unhandled_input(key)
		var player := subjects[1].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
		assert(player.current_animation == "Walk")
		key.keycode = KEY_C
		_unhandled_input(key)
		assert(orbit_mode)
		_unhandled_input(key)
		assert(not orbit_mode)
		key.keycode = KEY_TAB
		_unhandled_input(key)
		assert(selected == 0)
		play_clip("Walk")
		assert("unavailable" in clip_status)
		selected = 1
		play_clip("Idle")
		selected = 0
		clip_status = "Human: static fitting model; action clips unavailable"
		print("COMPARISON_INPUT_TEST_OK selection,robot_clip,camera_mode,human_missing_action")
	# Let asset upload/shader setup settle before collecting timing evidence.
	for frame in range(30):
		await get_tree().process_frame
	var started := Time.get_ticks_usec()
	for frame in range(120):
		await get_tree().process_frame
	var elapsed := (Time.get_ticks_usec() - started) / 1000000.0
	print("COMPARISON_RENDER_TIMING frames=120 seconds=", elapsed, " average_fps=", 120.0 / elapsed)
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--capture="):
			var path := argument.trim_prefix("--capture=")
			if not path.begins_with(root):
				get_tree().quit(3)
				return
			await get_tree().process_frame
			await RenderingServer.frame_post_draw
			await RenderingServer.frame_post_draw
			var result := get_viewport().get_texture().get_image().save_png(path)
			print("COMPARISON_CAPTURE ", result)
			get_tree().quit(0 if result == OK else 4)

func update_camera() -> void:
	camera.position = target + Vector3(sin(yaw) * cos(elevation), sin(elevation), cos(yaw) * cos(elevation)) * 10
	camera.look_at(target)

func play_clip(name_value: String) -> void:
	var players := subjects[selected].find_children("*", "AnimationPlayer", true, false)
	if players.is_empty():
		clip_status = "Human: requested action unavailable (not simulated)"
		return
	var player := players[0] as AnimationPlayer
	if not player.has_animation(name_value):
		clip_status = "Requested action unavailable: " + name_value
		return
	player.play(name_value)
	clip_status = "Robot animation: " + name_value

func _process(_delta: float) -> void:
	if hud:
		hud.text = "EXPERIMENTAL SCALE REVIEW | 1 m tiles | NOT FINAL ART\nLeft: human 1.718 m | Right: robot 2.4 m (rest pose)\nSelected: %s | %s\nTAB / click: select | 1 Idle  2 Walk  3 Shoot  4 Death\nC: isometric / orbit | RMB drag: orbit | Wheel: zoom\nFPS %d | draw calls %d | rendered primitives %d" % ["Human" if selected == 0 else "Robot", clip_status, Engine.get_frames_per_second(), Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME), Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)]

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_TAB:
			selected = 1 - selected
		if event.keycode == KEY_C:
			orbit_mode = not orbit_mode
			if not orbit_mode:
				yaw = 0.65
				elevation = 0.6
				update_camera()
		var actions := {KEY_1: "Idle", KEY_2: "Walk", KEY_3: "Shoot", KEY_4: "Death"}
		if actions.has(event.keycode):
			play_clip(actions[event.keycode])
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_RIGHT:
			orbiting = event.pressed
		if event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			var point: Vector2 = event.position
			var left := camera.unproject_position(subjects[0].position + Vector3.UP)
			var right := camera.unproject_position(subjects[1].position + Vector3.UP)
			selected = 0 if point.distance_to(left) < point.distance_to(right) else 1
		if event.pressed and event.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]:
			camera.size = clampf(camera.size + (-0.5 if event.button_index == MOUSE_BUTTON_WHEEL_UP else 0.5), 3, 16)
	if event is InputEventMouseMotion and orbiting and orbit_mode:
		yaw -= event.relative.x * 0.008
		elevation = clampf(elevation + event.relative.y * 0.008, 0.15, 1.35)
		update_camera()
