extends Node3D
## Bounded cohort diagnostic, not a production mission benchmark.
const FOLDER := "E:/CyberCity2085-3d-lab/generated/phase2/modularity166/"
var actors: Array[Node3D] = []
var camera: Camera3D

func calibrate(pixels: float) -> float:
	var height := absf(camera.unproject_position(Vector3(0, 1.8, 0)).y - camera.unproject_position(Vector3.ZERO).y)
	camera.size *= height / pixels
	return absf(camera.unproject_position(Vector3(0, 1.8, 0)).y - camera.unproject_position(Vector3.ZERO).y)

func _ready() -> void:
	get_window().size = Vector2i(1920, 1080)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	var manifest = JSON.parse_string(FileAccess.get_file_as_string(FOLDER + "exports.json"))
	var sources: Array[Node3D] = []
	for item in manifest.exports:
		if FileAccess.get_sha256(item.file) != item.sha256:
			get_tree().quit(1); return
		var doc := GLTFDocument.new()
		var state := GLTFState.new()
		if doc.append_from_file(item.file, state) != OK:
			get_tree().quit(1); return
		sources.append(doc.generate_scene(state) as Node3D)
	for index in 16:
		var actor := sources[index % 2].duplicate() as Node3D
		add_child(actor)
		actor.position = Vector3((index % 4) * 3, 0, (index / 4) * 3)
		actors.append(actor)
		var player := actor.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
		player.get_animation("Rocketbox_Walk").loop_mode = Animation.LOOP_LINEAR
		player.play("Rocketbox_Walk")
		player.seek(index * .07, true)
	for source in sources: source.free()
	var world := WorldEnvironment.new()
	world.environment = Environment.new()
	world.environment.background_mode = Environment.BG_COLOR
	world.environment.background_color = Color(.06, .075, .09)
	world.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	world.environment.ambient_light_color = Color.WHITE
	world.environment.ambient_light_energy = .65
	add_child(world)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55, -30, 0)
	light.shadow_enabled = true
	add_child(light)
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(40, 40)
	ground.mesh = plane
	var material := StandardMaterial3D.new()
	material.albedo_color = Color(.16, .18, .20)
	ground.material_override = material
	add_child(ground)
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 20
	add_child(camera)
	camera.position = Vector3(12, 18, 23)
	camera.look_at(Vector3(4.5, .8, 4.5))
	await RenderingServer.frame_post_draw
	var close_pixels := calibrate(62.208)
	if absf(close_pixels - 62.208) > .1:
		get_tree().quit(1); return
	var layer := CanvasLayer.new()
	add_child(layer)
	var caption := Label.new()
	caption.position = Vector2(20, 20)
	caption.text = "2 authored bodies / shared 80-bone rig / real source textures\nDiagnostic stage, not a production map. Different designs from Rook.\nFixed 1.8m projection calibrated against actual combat zoom."
	layer.add_child(caption)
	var reference := TextureRect.new()
	reference.texture = ImageTexture.create_from_image(Image.load_from_file("E:/CyberCity2085-3d-lab/sources/rook_combat/00_E.png"))
	reference.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	reference.position = Vector2(30, 140)
	reference.size = Vector2.ONE * (62.208 / .84375)
	layer.add_child(reference)
	var measurements: Array = []
	for count in [2, 8, 16]:
		for index in 16:
			actors[index].visible = index < count
			actors[index].process_mode = Node.PROCESS_MODE_INHERIT if index < count else Node.PROCESS_MODE_DISABLED
		for warmup in 60: await RenderingServer.frame_post_draw
		var samples: Array[float] = []
		var begin := Time.get_ticks_usec()
		var last := begin
		var begin_utc := Time.get_unix_time_from_system()
		var calls := 0
		while Time.get_ticks_usec() - begin < 5000000:
			await RenderingServer.frame_post_draw
			var now := Time.get_ticks_usec()
			samples.append((now - last) / 1000.0)
			last = now
			calls = maxi(calls, int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)))
		var seconds := (Time.get_ticks_usec() - begin) / 1000000.0
		samples.sort()
		measurements.append({"units": count, "seconds": seconds, "begin_utc_unix_s": begin_utc,
			"end_utc_unix_s": Time.get_unix_time_from_system(), "rendered_frames": samples.size(),
			"rendered_frames_per_s": samples.size() / seconds,
			"frame_post_draw_interval_p95_ms": samples[int((samples.size()-1)*.95)], "max_draw_calls": calls})
	await RenderingServer.frame_post_draw
	var close_image := get_viewport().get_texture().get_image()
	close_image.save_png(FOLDER + "cohort_close.png")
	var overview_pixels := calibrate(20.736)
	reference.size = Vector2.ONE * (20.736 / .84375)
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(FOLDER + "cohort_overview.png")
	var file := FileAccess.open(FOLDER + "cohort_benchmark.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({"status": "PASS", "sources": manifest.exports,
		"measurements": measurements, "viewport": [close_image.get_width(), close_image.get_height()],
		"close_1_8m_pixels": close_pixels, "overview_1_8m_pixels": overview_pixels,
		"renderer": RenderingServer.get_current_rendering_method(),
		"scope": "Native frame submission intervals, isolated stage, two shared source models. Not GPU execution time, peak VRAM or production mission acceptance."}, "  "))
	file.close()
	print("COHORT_NATIVE_BENCHMARK_PASS ", JSON.stringify(measurements))
	get_tree().quit()
