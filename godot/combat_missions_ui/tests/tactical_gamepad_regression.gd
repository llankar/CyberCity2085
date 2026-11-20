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
	await press(JOY_BUTTON_Y)
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
