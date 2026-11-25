extends Node3D
const FOLDER := "E:/CyberCity2085-3d-lab/generated/phase2/hunyuan166/rook_combat/"

func _ready() -> void:
	get_window().size = Vector2i(1920, 1080)
	var model := FOLDER + "review_upright/optimized.glb"
	var source := "E:/CyberCity2085-3d-lab/sources/rook_combat/00_E.png"
	var native = JSON.parse_string(FileAccess.get_file_as_string(FOLDER + "review_upright/godot.json"))
	var generation = JSON.parse_string(FileAccess.get_file_as_string(FOLDER + "result.json"))
	if FileAccess.get_sha256(model) != native.source_sha256 or FileAccess.get_sha256(source) != generation.source_sha256:
		get_tree().quit(1); return
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	if doc.append_from_file(model, state) != OK:
		get_tree().quit(1); return
	var actor := doc.generate_scene(state) as Node3D
	add_child(actor)
	var bounds := AABB()
	var first := true
	for node in actor.find_children("*", "MeshInstance3D", true, false):
		var box: AABB = node.global_transform * node.get_aabb()
		bounds = box if first else bounds.merge(box)
		first = false
	if first or bounds.size.y <= 0:
		get_tree().quit(1); return
	var factor := 1.8 / bounds.size.y
	actor.scale *= factor
	actor.position.y -= bounds.position.y * factor
	var world := WorldEnvironment.new()
	world.environment = Environment.new()
	world.environment.background_mode = Environment.BG_COLOR
	world.environment.background_color = Color(.08, .09, .10)
	world.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	world.environment.ambient_light_color = Color.WHITE
	world.environment.ambient_light_energy = .7
	add_child(world)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55, -25, 0)
	add_child(light)
	var camera := Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 8
	add_child(camera)
	camera.position = Vector3(2.5, 3.8, 5.5)
	camera.look_at(Vector3(0, .8, 0))
	var layer := CanvasLayer.new()
	add_child(layer)
	var note := Label.new()
	note.position = Vector2(20, 20)
	note.text = "Actual Rook combat input / Hunyuan geometry from that exact image\nNo generated texture, rig or animation. Neutral diagnostic; not production art."
	layer.add_child(note)
	var reference := TextureRect.new()
	reference.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	reference.texture = ImageTexture.create_from_image(Image.load_from_file(source))
	layer.add_child(reference)
	var report := {"model_sha256": native.source_sha256, "source_sha256": generation.source_sha256,
		"body_height_m": 1.8, "measurements": [], "scope": "Same source design at calibrated zoom; static untextured geometry only"}
	for item in [["close", 62.208], ["overview", 20.736]]:
		await RenderingServer.frame_post_draw
		var measured := absf(camera.unproject_position(Vector3(0, 1.8, 0)).y - camera.unproject_position(Vector3.ZERO).y)
		camera.size *= measured / float(item[1])
		var projected := absf(camera.unproject_position(Vector3(0, 1.8, 0)).y - camera.unproject_position(Vector3.ZERO).y)
		if absf(projected-float(item[1])) > .1:
			get_tree().quit(1); return
		reference.size = Vector2.ONE * (float(item[1]) / .84375)
		reference.position = camera.unproject_position(Vector3.ZERO) + Vector2(-150, 0) - reference.size * Vector2(.5, .953125)
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var image := get_viewport().get_texture().get_image()
		if image.get_size() != Vector2i(1920, 1080):
			get_tree().quit(1); return
		var path := FOLDER + "combat_scale_" + str(item[0]) + ".png"
		if image.save_png(path) != OK:
			get_tree().quit(1); return
		report.measurements.append({"view": item[0], "projected_height_px": projected, "png_sha256": FileAccess.get_sha256(path)})
	var file := FileAccess.open(FOLDER + "combat_scale.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("AI_COMBAT_SCALE_CAPTURE_PASS ", JSON.stringify(report))
	get_tree().quit()
