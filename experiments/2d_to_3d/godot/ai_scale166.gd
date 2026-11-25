extends Node3D
var coloured_robot := "--coloured-robot" in OS.get_cmdline_user_args()
var coloured_rook := "--coloured-rook" in OS.get_cmdline_user_args()
var folder := "E:/CyberCity2085-3d-lab/generated/phase2/paint168/robot_official/" if coloured_robot else "E:/CyberCity2085-3d-lab/generated/phase2/hunyuan166/rook_combat/"

func _ready() -> void:
	if coloured_rook:folder="E:/CyberCity2085-3d-lab/generated/phase2/paint171/rook_official/"
	var colour := coloured_robot or coloured_rook
	get_window().size = Vector2i(1920, 1080)
	var model := folder + ("mesh.glb" if colour else "review_upright/optimized.glb")
	var source := "E:/CyberCity2085-3d-lab/sources/robot.png" if coloured_robot else "E:/CyberCity2085-3d-lab/sources/rook_combat/00_E.png"
	var generation = JSON.parse_string(FileAccess.get_file_as_string(folder + "result.json"))
	var native = {"source_sha256":generation.glb_sha256} if colour else JSON.parse_string(FileAccess.get_file_as_string(folder + "review_upright/godot.json"))
	var painted := colour and "--painted-material" in OS.get_cmdline_user_args()
	if painted:
		var derived=JSON.parse_string(FileAccess.get_file_as_string(folder+"painted_material.json"))
		assert(derived.source_sha256==generation.glb_sha256)
		model=folder+"painted_material.glb";native.source_sha256=derived.glb_sha256
	var source_hash: String = generation.reference_sha256 if colour else generation.source_sha256
	if FileAccess.get_sha256(model) != native.source_sha256 or FileAccess.get_sha256(source) != source_hash:
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
	var body_height := 2.4 if coloured_robot else 1.8
	var factor := body_height / bounds.size.y
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
	if colour:note.text=("Combat robot" if coloured_robot else "Rook combat")+" / original 2D and Hunyuan colour (static mesh)"
	layer.add_child(note)
	var reference := TextureRect.new()
	reference.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	var source_image := Image.load_from_file(source)
	if colour:source_image=source_image.get_region(source_image.get_used_rect())
	reference.texture = ImageTexture.create_from_image(source_image)
	layer.add_child(reference)
	var report := {"model_sha256": native.source_sha256, "source_sha256": source_hash,
		"body_height_m": body_height, "measurements": [], "scope": "Same source design at game zoom; static coloured mesh" if colour else "Same source design at calibrated zoom; static untextured geometry only"}
	for item in [["close", 62.208], ["overview", 20.736]]:
		await RenderingServer.frame_post_draw
		var measured := absf(camera.unproject_position(Vector3(0, 1.8, 0)).y - camera.unproject_position(Vector3.ZERO).y)
		camera.size *= measured / float(item[1])
		var projected := absf(camera.unproject_position(Vector3(0, 1.8, 0)).y - camera.unproject_position(Vector3.ZERO).y)
		if not colour and absf(projected-float(item[1])) > .1:
			get_tree().quit(1); return
		reference.size = Vector2.ONE * (float(item[1]) / .84375)
		reference.position = camera.unproject_position(Vector3.ZERO) + Vector2(-150, 0) - reference.size * Vector2(.5, .953125)
		if colour:
			var pixels:=float(item[1])*body_height/1.8
			reference.size=Vector2(pixels*source_image.get_width()/source_image.get_height(),pixels)
			reference.position=camera.unproject_position(Vector3.ZERO)+Vector2(-150,0)-reference.size*Vector2(.5,1)
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var image := get_viewport().get_texture().get_image()
		if image.get_size() != Vector2i(1920, 1080):
			get_tree().quit(1); return
		var path := folder + ("painted_scale_" if painted else "combat_scale_") + str(item[0]) + ".png"
		if image.save_png(path) != OK:
			get_tree().quit(1); return
		report.measurements.append({"view": item[0], "projected_height_px": projected, "png_sha256": FileAccess.get_sha256(path)})
	var file := FileAccess.open(folder + ("painted_scale.json" if painted else "combat_scale.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("AI_COMBAT_SCALE_CAPTURE_PASS ", JSON.stringify(report))
	get_tree().quit()
