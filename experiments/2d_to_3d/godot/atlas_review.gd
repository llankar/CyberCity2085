extends Node2D
## Eight raw orbit views; not yet mapped to production facing semantics.
var views: Array[Sprite2D] = []
var frame_value := 0
var elapsed := 0.0
var fps := 4.8
var playing := true
var selected := 0
var rows: Array = []
var status: Label
var looping := true
var action_name := "walk"

func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/robot_walk_atlas01/"
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--action="):
			action_name = argument.trim_prefix("--action=").to_lower()
			if action_name not in ["idle", "walk", "shoot", "hitrecieve_1", "death"]:
				get_tree().quit(5)
				return
		if argument.begins_with("--atlas-dir="):
			folder = argument.trim_prefix("--atlas-dir=").trim_suffix("/") + "/"
	if not folder.begins_with("E:/CyberCity2085-3d-lab/generated/"):
		get_tree().quit(5)
		return
	var manifest = JSON.parse_string(FileAccess.get_file_as_string(folder + "robot_" + action_name + "_atlas.json"))
	var image := Image.load_from_file(folder + "robot_" + action_name + "_atlas.png")
	if not manifest is Dictionary or image == null:
		get_tree().quit(2)
		return
	rows = manifest.animations[action_name].rows
	fps = manifest.animations[action_name].fps
	looping = manifest.animations[action_name].loop
	var texture := ImageTexture.create_from_image(image)
	for index in range(8):
		var sprite := Sprite2D.new()
		sprite.texture = texture
		sprite.hframes = 8
		sprite.vframes = 4
		sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		sprite.position = Vector2(160 + (index % 4) * 300, 260 + (index / 4) * 290)
		sprite.scale = Vector2.ONE * 1.5
		add_child(sprite)
		views.append(sprite)
		var label := Label.new()
		label.text = "Orbit view %d" % index
		label.position = sprite.position + Vector2(-45, 105)
		add_child(label)
	status = Label.new()
	status.position = Vector2(20, 20)
	status.add_theme_font_size_override("font_size", 20)
	add_child(status)
	update_frames()
	if "--self-test" in OS.get_cmdline_user_args():
		for sample in range(4):
			frame_value = sample
			update_frames()
			for direction in range(8):
				assert(views[direction].frame == int(rows[direction][sample]))
		frame_value = 0
		elapsed = 0
		_process(1.1 / fps)
		assert(frame_value == 1)
		var key := InputEventKey.new()
		key.pressed = true
		key.keycode = KEY_SPACE
		_unhandled_key_input(key)
		assert(not playing)
		_process(2.0 / fps)
		assert(frame_value == 1)
		key.keycode = KEY_RIGHT
		_unhandled_key_input(key)
		assert(selected == 1)
		key.keycode = KEY_LEFT
		_unhandled_key_input(key)
		assert(selected == 0)
		playing = true
		frame_value = 3
		elapsed = 0
		_process(1.1 / fps)
		assert(frame_value == (0 if looping else 3))
		print("ATLAS_PLAYBACK_TEST_OK frames=32 pause=true view_selection=true")
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--capture="):
			var path := argument.trim_prefix("--capture=")
			if not path.begins_with(folder):
				get_tree().quit(3)
				return
			await RenderingServer.frame_post_draw
			await RenderingServer.frame_post_draw
			var error := get_viewport().get_texture().get_image().save_png(path)
			print("ATLAS_REVIEW_CAPTURE ", error)
			get_tree().quit(0 if error == OK else 4)

func update_frames() -> void:
	for direction in range(views.size()):
		views[direction].frame = int(rows[direction][frame_value])
		views[direction].modulate = Color.WHITE if selected == direction else Color(0.8, 0.8, 0.8)
	if status:
		status.text = "ANIMATED ATLAS REVIEW | authored %s | 8 views x 4 poses\nSpace: pause | Left/Right: select view | frame %d | %.2f fps\nRaw camera orbit indices: production facing and foot anchor NOT VERIFIED" % [action_name, frame_value, fps]

func _process(delta: float) -> void:
	if not playing or views.is_empty():
		return
	elapsed += delta
	if elapsed >= 1.0 / fps:
		var steps := int(elapsed * fps)
		frame_value = (frame_value + steps) % 4 if looping else mini(3, frame_value + steps)
		elapsed -= steps / fps
		update_frames()

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_SPACE:
			playing = not playing
		if event.keycode in [KEY_RIGHT, KEY_LEFT]:
			selected = posmod(selected + (1 if event.keycode == KEY_RIGHT else -1), 8)
		update_frames()
