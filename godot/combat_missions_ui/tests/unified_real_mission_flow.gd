extends SceneTree
## Plays the normal objective loop to completion. It never calls _end_combat,
## _complete_mission, or mutates objective completion/result state directly.

func _initialize() -> void:
	call_deferred("run")


func _arg_value(args: PackedStringArray, key: String) -> String:
	for index in range(args.size() - 1):
		if args[index] == key:
			return args[index + 1]
	return ""


func _advance_objective(scene) -> bool:
	var active: Dictionary = scene._current_active_player()
	if active.is_empty():
		return false
	var objective_cell: Vector2i = scene.objective.get("cell", Vector2i.ZERO)
	var position: Vector2i = scene._cell_position(active)
	var interact_range := int(scene.objective.get("interact_range", 2))
	if absi(position.x - objective_cell.x) + absi(position.y - objective_cell.y) <= interact_range:
		scene._interact_with_objective()
		return true
	var route: Array[Vector2i] = scene._battlefield.find_path(position, objective_cell)
	if route.size() <= 1:
		return false
	var ap := int(active.get("ap", 0))
	var destination_index := mini(route.size() - 1, maxi(1, ap))
	# The marker itself may be occupied/blocked; stop at the furthest legal cell.
	while destination_index > 0:
		var destination := route[destination_index]
		if destination in scene._battlefield.move_range_cells \
				and not scene._is_cell_occupied(destination, scene.active_player_index, -1):
			scene._move_active_unit_to(destination)
			return true
		destination_index -= 1
	return false


func run() -> void:
	seed(2085)
	var args := OS.get_cmdline_user_args()
	var expected_outcome := _arg_value(args, "--qa-real-outcome")
	if expected_outcome.is_empty():
		expected_outcome = "victory"
	var confirm_path := _arg_value(args, "--qa-confirm")
	var capture_dir := _arg_value(args, "--qa-captures")
	var scene = load("res://scenes/combat_mission_ui.tscn").instantiate()
	scene.handoff_path = _arg_value(args, "--handoff")
	root.add_child(scene)
	await RenderingServer.frame_post_draw
	print("UNIFIED_FIRST_FRAME monotonic_ms=", Time.get_ticks_msec())
	for attempt in range(30):
		if scene.battle_started:
			break
		await process_frame
	assert(scene.battle_started, "combat did not deploy")
	print("UNIFIED_REAL_MISSION_READY monotonic_ms=", Time.get_ticks_msec())
	if scene.handoff.get("session", {}).has("audio_path"):
		assert(not scene._audio._music_owned)
		for attempt in range(100):
			scene._poll_audio_release(0.1)
			if scene._audio_released:
				break
			await create_timer(0.1).timeout
		assert(scene._audio_released and scene._audio._music_owned)
		print("UNIFIED_AUDIO_OWNERSHIP_READY")
	var hold_seconds := float(_arg_value(args, "--qa-window-hold-seconds"))
	if hold_seconds > 0.0:
		print("UNIFIED_WINDOW_LIFECYCLE_WAITING")
		await create_timer(hold_seconds).timeout

	var actions := 0
	var turns := 0
	if expected_outcome == "retreat":
		scene._execute_action("RETREAT")
		assert(not scene.battle_ended, "retreat must require confirmation")
		scene._execute_action("RETREAT")
	while not scene.battle_ended and turns < 80:
		if scene.turn_side == "enemy":
			scene._resolve_enemy_turn()
			turns += 1
			await process_frame
			continue
		if scene.turn_side != "player":
			await process_frame
			continue
		var progressed := false
		if expected_outcome == "victory":
			progressed = _advance_objective(scene)
		if progressed:
			actions += 1
		else:
			scene._end_player_turn()
		await process_frame

	assert(scene.battle_ended, "real objective loop did not reach a terminal outcome")
	assert(scene._results._outcome == expected_outcome, "mission produced the wrong terminal outcome")
	if expected_outcome == "victory":
		assert(scene.objective_completed, "mission ended without completing its authored objective")
		assert(actions >= int(scene.objective.get("progress_needed", 1)), "objective was not completed through actions")
	elif expected_outcome == "defeat":
		assert(scene._player_alive_count() == 0, "defeat was not caused by squad elimination")
	print("UNIFIED_REAL_MISSION_COMPLETED actions=", actions, " turns=", turns)
	await create_timer(0.75).timeout

	var session: Dictionary = scene.handoff.session
	assert(FileAccess.file_exists(session.prepared_path))
	assert(not FileAccess.file_exists(session.result_path))
	if not capture_dir.is_empty():
		DirAccess.make_dir_recursive_absolute(capture_dir)
		await process_frame
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png(capture_dir.path_join("godot-real-results.png")) == OK)
	print("UNIFIED_NATIVE_RESULTS_WAITING")
	while not FileAccess.file_exists(confirm_path):
		await create_timer(0.05).timeout
	scene._results._extract_btn.pressed.emit()
	assert(FileAccess.file_exists(session.result_path))
	print("UNIFIED_NATIVE_RESULT_CONFIRMED")

