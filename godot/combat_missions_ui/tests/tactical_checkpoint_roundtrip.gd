extends SceneTree
const Checkpoint = preload("res://scripts/tactical_checkpoint.gd")
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var args := OS.get_cmdline_user_args()
	var path := ""
	var side := "player"
	var reject_resume := "--reject-resume" in args
	for i in range(args.size()-1):
		if args[i] == "--handoff": path = args[i+1]
		if args[i] == "--phase": side = args[i+1]
	var scene = load("res://scenes/combat_mission_ui.tscn").instantiate()
	scene.handoff_path = path
	if "--qa-classic" in args: scene.visual_mode = false
	root.add_child(scene)
	for i in range(10):
		if scene.battle_started: break
		await process_frame
	assert(scene.battle_started)
	if "--qa-isometric" in args:
		var event := InputEventKey.new()
		event.keycode = KEY_F11; event.pressed = true
		scene._gui_input(event)
		assert(not scene._battlefield.top_down)
	var origin: Vector2i = scene._cell_position(scene.player_units[0])
	var moved := false
	for cell: Vector2i in scene._battlefield.reachable_cells(origin, 1):
		if cell == origin or scene._is_cell_occupied(cell, 0, -1): continue
		scene._move_active_unit_to(cell)
		moved = true; break
	assert(moved and scene.player_units[0].ap == 3)
	scene._execute_action("Defend")
	scene._execute_action("Overwatch")
	scene.player_units[0].hp = maxi(1, int(scene.player_units[0].hp)-2)
	scene.player_units[0].status_effects = ["bleed"]
	scene.turn_number = 3
	scene.objective_progress = 1
	scene.pending_end_turn_confirmation = true
	scene.selected_action = "Pistol Shot"
	scene._camera.position = Vector2(93, 171)
	scene._camera.zoom = Vector2.ONE * 0.7
	scene.turn_side = side
	scene.enemy_turn_timer = 0.8
	scene._sync_display()
	scene.set_process(false)
	await process_frame
	var channel: String = scene.handoff.session.snapshot_path
	assert(FileAccess.file_exists(channel))
	var snapshot: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(channel))
	assert(Checkpoint.validate(snapshot, scene).is_empty())
	var invalid := snapshot.duplicate(true)
	invalid.state.player_units[0].position = [-1, 0]
	assert(not Checkpoint.validate(invalid, scene).is_empty())
	assert(scene._cell_position(scene.player_units[0]) != origin)
	var handoff: Dictionary = scene.handoff.duplicate(true)
	handoff.resume_snapshot = snapshot.duplicate(true)
	if reject_resume: handoff.resume_snapshot.state.player_units[0].max_hp = -1
	preload("res://scripts/session_mailbox.gd").publish(path, handoff)
	scene.queue_free()
	await process_frame
	if "--qa-resize" in args: root.size = Vector2i(1600,900)
	var resumed = load("res://scenes/combat_mission_ui.tscn").instantiate()
	resumed.handoff_path = path
	root.add_child(resumed)
	resumed.set_process(false)
	for i in range(10):
		if resumed.battle_started or not resumed._recovery_error.is_empty(): break
		await process_frame
	if reject_resume:
		assert(not resumed._recovery_error.is_empty() and not resumed.battle_started)
		var status: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(str(resumed.handoff.session.status_path)))
		assert(status.event == "error" and not status.ready)
		assert(resumed._unit_tokens.is_empty(), "Never spawn a fresh encounter as a silent fallback")
		print("TACTICAL_CHECKPOINT_REJECT_PASS")
		resumed.queue_free()
		await process_frame
		quit(); return
	assert(resumed._recovery_error.is_empty(), resumed._recovery_error)
	assert(resumed.battle_started)
	resumed.set_process(false)
	var after := Checkpoint.capture(resumed)
	var normalized: Dictionary = JSON.parse_string(JSON.stringify(after))
	assert(normalized.state == snapshot.state, "All tactical state including AP/postures/objective must roundtrip")
	if "--qa-resize" in args:
		assert(after.camera.viewport == [1600.0,900.0])
		assert(after.camera.zoom >= resumed._ZOOM_MIN and after.camera.zoom <= resumed._ZOOM_MAX)
	else: assert(normalized.camera == snapshot.camera)
	assert(normalized.token_facings == snapshot.token_facings)
	assert(resumed._unit_tokens.p0.position == resumed._battlefield.cell_to_world(resumed._cell_position(resumed.player_units[0])))
	if side == "player":
		resumed.selected_action = "MOVE"
		resumed._sync_display()
		resumed._camera.force_update_scroll()
		var origin_after: Vector2i = resumed._cell_position(resumed.player_units[0])
		var clicked := false
		for destination: Vector2i in resumed._battlefield.reachable_cells(origin_after, 1):
			if destination == origin_after or resumed._is_cell_occupied(destination, 0, -1) or destination == resumed.objective.cell: continue
			var event := InputEventMouseButton.new()
			event.button_index = MOUSE_BUTTON_LEFT; event.pressed = false
			event.position = root.get_canvas_transform() * resumed._battlefield.cell_to_world(destination)
			var ap_before: int = int(resumed.player_units[0].ap)
			resumed._battlefield._unhandled_input(event)
			assert(resumed._cell_position(resumed.player_units[0]) == destination and resumed.player_units[0].ap == ap_before-1)
			clicked = true; break
		assert(clicked, "No legal destination to verify viewport-to-grid click after restore")
	if side == "enemy":
		resumed._resolve_enemy_turn()
		assert(resumed.turn_number == 4 and resumed.turn_side == "player")
	print("TACTICAL_CHECKPOINT_ROUNDTRIP_PASS ", side)
	resumed.queue_free()
	await process_frame
	quit()
