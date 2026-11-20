extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func press(button: JoyButton) -> void:
	var event := InputEventJoypadButton.new()
	event.button_index = button
	event.pressed = true
	Input.parse_input_event(event)
	await process_frame
	event.pressed = false
	Input.parse_input_event(event)
	await process_frame

func run() -> void:
	var mission = load("res://scenes/combat_mission_ui.tscn").instantiate()
	root.add_child(mission)
	await create_timer(2.3).timeout
	if not mission.battle_started or mission.player_units.size() < 2:
		push_error("Default tactical fixture did not deploy a squad.")
		quit(1)
		return
	var selected: int = mission.active_player_index
	await press(JOY_BUTTON_RIGHT_SHOULDER)
	if mission.active_player_index == selected:
		push_error("Right shoulder did not cycle the active unit.")
		quit(1)
		return
	var agent: Dictionary = mission.player_units[mission.active_player_index]
	var origin: Vector2i = agent.position
	var previous_ap: int = agent.ap
	var directions := {
		JOY_BUTTON_DPAD_UP: Vector2i.UP, JOY_BUTTON_DPAD_DOWN: Vector2i.DOWN,
		JOY_BUTTON_DPAD_LEFT: Vector2i.LEFT, JOY_BUTTON_DPAD_RIGHT: Vector2i.RIGHT,
	}
	var moved := false
	for button: JoyButton in directions:
		var destination: Vector2i = origin + directions[button]
		if not destination in mission._battlefield.move_range_cells or destination == mission.objective.get("cell"):
			continue
		if mission._is_cell_occupied(destination, mission.active_player_index, -1):
			continue
		await press(button)
		if mission._battlefield.hovered_cell != destination:
			break
		await press(JOY_BUTTON_A)
		moved = agent.position == destination and agent.ap == previous_ap - 1
		break
	if not moved:
		push_error("Directional pad and A did not preview and execute a legal 1 AP move.")
		quit(1)
		return
	await press(JOY_BUTTON_X)
	if mission._hud.gamepad_action.to_upper() != "MOVE" or "choose action" not in mission._hud.tactical_status():
		push_error("X did not open the action bar on Move with controller hints.")
		quit(1)
		return
	await press(JOY_BUTTON_DPAD_UP)
	if mission._hud.gamepad_action != "END TURN" or mission.pending_end_turn_confirmation:
		push_error("The action bar did not wrap or executed before confirmation.")
		quit(1)
		return
	await press(JOY_BUTTON_A)
	if not mission.pending_end_turn_confirmation or mission.turn_side != "player":
		push_error("Y did not open the end-turn confirmation.")
		quit(1)
		return
	await press(JOY_BUTTON_B)
	if mission.pending_end_turn_confirmation or mission.turn_side != "player":
		push_error("B did not cancel the end-turn confirmation.")
		quit(1)
		return
	await press(JOY_BUTTON_Y)
	await press(JOY_BUTTON_A)
	if mission.pending_end_turn_confirmation or mission.turn_side != "enemy":
		push_error("A did not confirm the end turn.")
		quit(1)
		return
	print("TACTICAL_GAMEPAD_CHECKS_PASSED")
	quit()
