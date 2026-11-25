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
var human_height := 1.718
var robot_height := 2.4
var human_weapon: Node3D

func subject_height(subject: Node3D) -> float:
	var bounds := AABB()
	var first := true
	var probe := preload("res://skin_motion_check.gd").new()
	for mesh in subject.find_children("*", "MeshInstance3D", true, false):
		if mesh.skin != null and mesh.get_node_or_null(mesh.skeleton) is Skeleton3D:
			var skeleton := mesh.get_node(mesh.skeleton) as Skeleton3D
			skeleton.force_update_all_bone_transforms()
			# Skin bind matrices can cancel FBX node scale/rotation. Mesh global
			# transform alone is not the rendered position of a skinned vertex.
			for point in probe.skinned_points(mesh, skeleton, 1):
				bounds = AABB(point, Vector3.ZERO) if first else bounds.expand(point)
				first = false
			continue
		# Mesh AABBs include the union of possible morph displacements, which is
		# not the actor's reference height and changes when clips are bundled.
		for surface in range(mesh.mesh.get_surface_count()):
			var vertices: PackedVector3Array = mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]
			for vertex in vertices:
				var point: Vector3 = mesh.global_transform * vertex
				bounds = AABB(point, Vector3.ZERO) if first else bounds.expand(point)
				first = false
	probe.free()
	assert(not first and bounds.size.y > 0.5)
	return bounds.size.y

func load_subject(path: String, position_value: Vector3) -> bool:
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	if document.append_from_file(path, state) != OK:
		push_error("Missing comparison subject: " + path)
		return false
	# Rest-valued tracks reset prior action poses and must survive import.
	var subject := document.generate_scene(state, 30, false, false)
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
	if "--msaa4" in OS.get_cmdline_user_args(): get_viewport().msaa_3d = Viewport.MSAA_4X
	if "--sprite-review" in OS.get_cmdline_user_args():
		get_window().content_scale_size = Vector2i(1920, 1080)
		get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
		await get_tree().process_frame
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/"
	var human_file := "authored_outfit_realtime.glb" if "--realtime" in OS.get_cmdline_user_args() else "authored_outfit.glb"
	var rocketbox_motion := "--rocketbox-motion-study" in OS.get_cmdline_user_args()
	var rocketbox := "--rocketbox-study" in OS.get_cmdline_user_args() or rocketbox_motion
	var charge := "--charge" in OS.get_cmdline_user_args() or rocketbox
	var human_path := root + "einar_pbr01/human_pbr.glb" if charge else root + "authored_tactical01/" + human_file
	var bundled_human := charge and "--human-bundle-study" in OS.get_cmdline_user_args()
	var rigged_human := charge and ("--rigged-human" in OS.get_cmdline_user_args() or bundled_human)
	if rigged_human: human_path = root + "einar_motion01/human_motion.glb"
	if bundled_human: human_path = root + "einar_bundle02/human_actions.glb"
	var action_human := charge and "--human-action-study" in OS.get_cmdline_user_args()
	assert(not (bundled_human and action_human), "Choose one human study")
	if action_human: human_path = root + "einar_pistol_fit01_surfaces/human_pistol.glb"
	if rocketbox:
		assert(not rigged_human and not action_human, "Choose one human source")
		human_path = root + "rocketbox_military03/character_dielectric.glb"
		if rocketbox_motion:
			human_path = root + "rocketbox_military03/motion01/human_motion.glb"
			rigged_human = true
	var robot_path := root + "security_pbr_robot01/robot_pbr.glb" if charge else root + "george_tactical/george_tactical.glb"
	var robot_idle := charge and "--robot-idle-study" in OS.get_cmdline_user_args()
	if robot_idle: robot_path = root + "security_idle01/robot_idle.glb"
	if not load_subject(human_path, Vector3(-1.6, 0, 0)):
		get_tree().quit(2)
		return
	if not load_subject(robot_path, Vector3(1.6, 0, 0)):
		get_tree().quit(2)
		return
	if bundled_human:
		human_weapon = preload("res://pistol_attachment.gd").attach(subjects[0])
		human_weapon.visible = false
	if rocketbox_motion:
		human_weapon = preload("res://rocketbox_pistol_attachment.gd").attach(subjects[0])
		human_weapon.visible = false
	if "--authored-groom" in OS.get_cmdline_user_args():
		assert(bundled_human, "Authored groom study requires the shared character rig")
		preload("res://groom_attachment.gd").attach(subjects[0], "einar_groom02_layered_lod")
	if charge:
		human_height = subject_height(subjects[0])
		robot_height = subject_height(subjects[1])
		print("CHARGE_STATIC_SUBJECTS_LOADED human_height=", human_height, " robot_height=", robot_height)
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
			if "--tactical" in OS.get_cmdline_user_args():
				continue
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
	if "--tactical" in OS.get_cmdline_user_args():
		load_tactical_map()
		camera.size = 22
		target = Vector3(0, 1, 2)
	update_camera()
	var layer := CanvasLayer.new()
	add_child(layer)
	hud = Label.new()
	hud.position = Vector2(20, 16)
	hud.add_theme_font_size_override("font_size", 19)
	layer.add_child(hud)
	if "--sprite-review" in OS.get_cmdline_user_args():
		setup_sprite_review(layer)
	selected = 1
	play_clip("Idle")
	if robot_idle:
		var idle_player := subjects[1].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
		assert(idle_player.current_animation == "Idle")
		print("CHARGE_ROBOT_IDLE_DISPATCH_OK")
	selected = 0
	clip_status = "Human: static fitting model; action clips unavailable"
	if rigged_human: play_clip("Idle")
	if action_human: play_clip("Shoot")
	print("COMPARISON_STAGE_LOADED subjects=", subjects.size(), " tile_width_m=1")
	if "--self-test" in OS.get_cmdline_user_args():
		var key := InputEventKey.new()
		key.pressed = true
		key.keycode = KEY_TAB
		_unhandled_input(key)
		assert(selected == 1)
		key.keycode = KEY_2
		_unhandled_input(key)
		if charge:
			assert("unavailable" in clip_status)
			var robot_players := subjects[1].find_children("*", "AnimationPlayer", true, false)
			if robot_idle:
				assert(robot_players.size() == 1 and robot_players[0].has_animation("Idle"))
			else: assert(robot_players.is_empty())
		else:
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
		if rigged_human:
			var walking_player := subjects[0].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
			assert(walking_player.current_animation == "Walk")
			print("CHARGE_HUMAN_WALK_DISPATCH_OK")
			play_clip("Shoot")
		if action_human or bundled_human or rocketbox_motion:
			play_clip("Shoot")
			var action_player := subjects[0].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
			assert(action_player.current_animation == "Pistol_Shoot")
			if human_weapon: assert(human_weapon.visible)
			print("CHARGE_HUMAN_PISTOL_DISPATCH_OK")
		else: assert("unavailable" in clip_status)
		if bundled_human or rocketbox_motion:
			var bundle_player := subjects[0].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
			play_clip("Melee")
			assert(bundle_player.current_animation == "Punch_Cross")
			if human_weapon: assert(not human_weapon.visible)
			play_clip("Death")
			assert(bundle_player.current_animation == "Death01")
			if human_weapon: assert(not human_weapon.visible)
			print("CHARGE_HUMAN_FIVE_ACTION_DISPATCH_OK")
		selected = 1
		play_clip("Idle")
		selected = 0
		clip_status = "Human: static fitting model; action clips unavailable"
		if rigged_human:
			play_clip("Idle")
			var human_player := subjects[0].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
			assert(human_player.current_animation == "Idle")
			print("CHARGE_HUMAN_IDLE_DISPATCH_OK")
		if action_human: play_clip("Shoot")
		print("COMPARISON_INPUT_TEST_OK selection,camera_mode,explicit_action_availability robot_clip=", "unavailable" if charge else "Walk")
	if rigged_human and "--walk-preview" in OS.get_cmdline_user_args(): play_clip("Walk")
	if rigged_human and "--shoot-preview" in OS.get_cmdline_user_args(): play_clip("Shoot")
	# Let asset upload/shader setup settle before collecting timing evidence.
	for frame in range(30):
		await get_tree().process_frame
	var started := Time.get_ticks_usec()
	for frame in range(120):
		await get_tree().process_frame
	var elapsed := (Time.get_ticks_usec() - started) / 1000000.0
	print("COMPARISON_RENDER_TIMING frames=120 seconds=", elapsed, " average_fps=", 120.0 / elapsed)
	for argument in OS.get_cmdline_user_args():
		if not argument.begins_with("--benchmark-output="): continue
		var destination := argument.trim_prefix("--benchmark-output=")
		assert(destination.begins_with(root) and destination.ends_with(".json"))
		await get_tree().create_timer(1.0).timeout
		var begin := Time.get_ticks_usec()
		var begin_drawn := Engine.get_frames_drawn()
		var samples: Array[float] = []
		var max_draw_calls := 0.0
		var max_video_bytes := 0.0
		var previous := begin
		while Time.get_ticks_usec() - begin < 5000000:
			await RenderingServer.frame_post_draw
			var now := Time.get_ticks_usec()
			samples.append((now - previous) / 1000.0)
			previous = now
			max_draw_calls = maxf(max_draw_calls, Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
			max_video_bytes = maxf(max_video_bytes, Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED))
		var seconds := (Time.get_ticks_usec() - begin) / 1000000.0
		var drawn := Engine.get_frames_drawn() - begin_drawn
		assert(drawn > 0 and not samples.is_empty())
		samples.sort()
		var texture_size := get_viewport().get_texture().get_size()
		var evidence := {"window_size": [get_window().size.x, get_window().size.y], "render_texture_size": [texture_size.x, texture_size.y], "logical_viewport_size": [get_viewport().get_visible_rect().size.x, get_viewport().get_visible_rect().size.y], "seconds": seconds, "rendered_frames": drawn, "rendered_frames_per_s": drawn / seconds, "frame_post_draw_interval_p95_ms": samples[int((samples.size() - 1) * 0.95)], "max_draw_calls": max_draw_calls, "engine_reported_video_bytes": max_video_bytes, "scope": "Five-second native rendered-frame interval; no GPU execution timing, no full VRAM peak or production benchmark", "human": human_path, "robot": robot_path}
		var output := FileAccess.open(destination, FileAccess.WRITE)
		assert(output != null)
		output.store_string(JSON.stringify(evidence, "  "))
		output.close()
		print("COMPARISON_NATIVE_BENCHMARK_OK ", JSON.stringify(evidence))
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
	camera.position = target + Vector3(sin(yaw) * cos(elevation), sin(elevation), cos(yaw) * cos(elevation)) * 50
	camera.look_at(target)

func setup_sprite_review(layer: CanvasLayer) -> void:
	var folder := "E:/CyberCity2085-3d-lab/sources/sprite_review/"
	var calibration = JSON.parse_string(FileAccess.get_file_as_string(folder + "calibration.json"))
	if not calibration is Dictionary or get_viewport().get_visible_rect().size != Vector2(1920, 1080):
		push_error("Sprite review requires prepared inputs and 1920x1080 viewport")
		get_tree().quit(6)
		return
	var body_px: float = calibration.close_human_px
	if "--overview" in OS.get_cmdline_user_args():
		body_px = calibration.overview_human_px
	var measured := absf(camera.unproject_position(Vector3(0, human_height, 0)).y - camera.unproject_position(Vector3.ZERO).y)
	camera.size *= measured / body_px
	var verified := absf(camera.unproject_position(Vector3(0, human_height, 0)).y - camera.unproject_position(Vector3.ZERO).y)
	assert(absf(verified - body_px) < 0.1)
	for index in range(2):
		var key: String = calibration.atlases[index].key
		var manifest = JSON.parse_string(FileAccess.get_file_as_string(folder + key + ".json"))
		var atlas := Image.load_from_file(folder + key + ".png")
		var frame_size := Vector2i(manifest.frame_size[0], manifest.frame_size[1])
		var frame_index_value: int = manifest.animations.idle.rows[1][0]
		var columns := atlas.get_width() / frame_size.x
		var frame := atlas.get_region(Rect2i(Vector2i(frame_index_value % columns, frame_index_value / columns) * frame_size, frame_size))
		var display_body := body_px * (1.0 if index == 0 else float(calibration.robot_sprite_multiplier))
		var display_size := Vector2(frame_size) * display_body / (frame_size.y * float(manifest.reference_height_uv))
		var foot := camera.unproject_position(subjects[index].position)
		var reference_foot := foot + Vector2(-95 if index == 0 else 95, 0)
		var picture := TextureRect.new()
		picture.texture = ImageTexture.create_from_image(frame)
		picture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		picture.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		picture.size = display_size
		picture.position = reference_foot - Vector2(manifest.anchor_uv[0], manifest.anchor_uv[1]) * display_size
		layer.add_child(picture)
		for entry in [[reference_foot, "Sprite 2D"], [foot, "Mesh 3D"]]:
			var caption := Label.new()
			caption.text = entry[1]
			caption.position = entry[0] + Vector2(-35, 12)
			caption.add_theme_font_size_override("font_size", 14)
			layer.add_child(caption)
	var note := Label.new()
	note.position = Vector2(20, 270)
	note.text = "SPRITE REVIEW: default alley calibration | human reference %.3f px | robot sprite x1.65\n3D human projected height verified; robot actual height %.3f m\nSprite shader/rim/ground shadows are not reproduced in this review." % [body_px, robot_height]
	layer.add_child(note)
	print("SPRITE_PIXEL_HEIGHT_VERIFIED expected=", body_px, " projected=", verified)

func load_tactical_map() -> void:
	subjects[0].position = Vector3(-1.5, 0, 1.5)
	subjects[1].position = Vector3(1.5, 0, 1.5)
	var folder := "E:/CyberCity2085-3d-lab/sources/tactical_map/"
	var name_value := "city_exterior_neon_market_alley"
	var data = JSON.parse_string(FileAccess.get_file_as_string(folder + name_value + ".walls.json"))
	if not data is Dictionary:
		push_error("Run prepare_tactical_inputs.py first")
		get_tree().quit(5)
		return
	var image := Image.load_from_file(folder + name_value + ".png")
	if image == null:
		get_tree().quit(5)
		return
	image.generate_mipmaps()
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(data.grid[0], data.grid[1])
	floor_mesh.mesh = plane
	floor_mesh.position.y = -0.03
	var asphalt := StandardMaterial3D.new()
	asphalt.albedo_texture = ImageTexture.create_from_image(image)
	asphalt.roughness = 0.95
	asphalt.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	floor_mesh.material_override = asphalt
	add_child(floor_mesh)
	var occupied: Dictionary = {}
	var batches: Dictionary = {true: [], false: []}
	for obstacle in data.walls:
		var tall: bool = "building" in obstacle.id
		for cell in obstacle.cells:
			var key := Vector2i(cell[0], cell[1])
			if occupied.has(key):
				continue
			occupied[key] = true
			var height := 3.0 if tall else 0.7
			batches[tall].append(Transform3D(Basis.IDENTITY, Vector3(cell[0] - data.grid[0] / 2.0 + 0.5, height / 2, cell[1] - data.grid[1] / 2.0 + 0.5)))
	var batch_instances := 0
	for tall in batches:
		var geometry := MultiMeshInstance3D.new()
		var block := BoxMesh.new()
		block.size = Vector3(1, 3.0 if tall else 0.7, 1)
		var instances := MultiMesh.new()
		instances.transform_format = MultiMesh.TRANSFORM_3D
		instances.mesh = block
		instances.instance_count = batches[tall].size()
		for index in range(instances.instance_count): instances.set_instance_transform(index, batches[tall][index])
		geometry.multimesh = instances
		var surface := StandardMaterial3D.new()
		surface.albedo_color = Color(0.12, 0.15, 0.17) if tall else Color(0.28, 0.29, 0.27)
		surface.roughness = 0.8
		geometry.material_override = surface
		add_child(geometry)
		batch_instances += instances.instance_count
	assert(batch_instances == occupied.size())
	print("TACTICAL_OBSTACLE_BATCHES_OK instances=", batch_instances, " batches=2")
	# No clear landing footprint exists on this alley: show the aircraft hovering.
	load_subject("E:/CyberCity2085-3d-lab/generated/phase2/vtol01/vtol.glb", Vector3(-6, 4, -4))
	load_subject("E:/CyberCity2085-3d-lab/generated/phase2/crate_procedural/crate_procedural.glb", Vector3(-3, 0, 2))
	load_subject("E:/CyberCity2085-3d-lab/generated/phase2/generator01/generator.glb", Vector3(4.5, 0, 1.5))
	assert(subjects.size() == 5)
	for subject in subjects.slice(0, 2):
		var cell := Vector2i(floori(subject.position.x + data.grid[0] / 2.0), floori(subject.position.z + data.grid[1] / 2.0))
		assert(not occupied.has(cell), "Actor spawned in blocked cell")
	print("TACTICAL_MAP_LAYOUT_LOADED cells=", occupied.size(), " subjects=", subjects.size(), " visual=2.5D_floor_plus_blocked_cells")

func play_clip(name_value: String) -> void:
	var players := subjects[selected].find_children("*", "AnimationPlayer", true, false)
	if players.is_empty():
		clip_status = "Requested action unavailable (not simulated)"
		return
	var player := players[0] as AnimationPlayer
	var aliases := {"Shoot": "Pistol_Shoot", "Melee": "Punch_Cross", "Death": "Death01"}
	if aliases.has(name_value) and player.has_animation(aliases[name_value]): name_value = aliases[name_value]
	if not player.has_animation(name_value):
		clip_status = "Requested action unavailable: " + name_value
		return
	player.play(name_value)
	if selected == 0 and human_weapon: human_weapon.visible = name_value == "Pistol_Shoot"
	if name_value == "Idle" or name_value == "Walk":
		player.get_animation(name_value).loop_mode = Animation.LOOP_LINEAR
	clip_status = ("Human animation: " if selected == 0 else "Robot animation: ") + name_value

func _process(_delta: float) -> void:
	if hud:
		hud.text = "EXPERIMENTAL SCALE REVIEW | 1 m tiles | NOT FINAL ART\nLeft: human %.3f m | Right: robot %.3f m (measured mesh heights)\nSelected: %s | %s\nTAB / click: select | 1 Idle  2 Walk  3 Shoot  4 Death  5 Melee\nC: isometric / orbit | RMB drag: orbit | Wheel: zoom\nFPS %d | draw calls %d | rendered primitives %d" % [human_height, robot_height, "Human" if selected == 0 else "Robot", clip_status, Engine.get_frames_per_second(), Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME), Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)]
		if "--tactical" in OS.get_cmdline_user_args():
			hud.text += "\nExisting alley layout + 2D floor / prototype obstacle volumes\nVTOL hovering: no clear landing footprint | art NOT accepted"

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
		var actions := {KEY_1: "Idle", KEY_2: "Walk", KEY_3: "Shoot", KEY_4: "Death", KEY_5: "Melee"}
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
