extends SceneTree
## Drives regional objective terminal states through normal combat actions.
## It never calls _end_combat/_complete_mission or mutates completion state.

func _initialize() -> void:
	call_deferred("run")

func _arg_value(args: PackedStringArray, key: String) -> String:
	for index in range(args.size() - 1):
		if args[index] == key:
			return args[index + 1]
	return ""

func run() -> void:
	seed(2085)
	var args := OS.get_cmdline_user_args()
	var expected := _arg_value(args, "--qa-outcome")
	assert(expected in ["victory", "defeat"])
	var mission = load("res://scenes/combat_mission_ui.tscn").instantiate()
	mission.handoff_path = _arg_value(args, "--handoff")
	root.add_child(mission)
	for attempt in range(90):
		if mission.battle_started:
			break
		await process_frame
	assert(mission.battle_started)
	var kind := _arg_value(args, "--qa-objective")
	assert(mission.objective.get("type", "") == kind)

	if expected == "defeat":
		assert(kind == "containment")
		var marker := mission.objective.cell as Vector2i
		var breachers: Array[int] = mission._containment_breacher_indices()
		assert(breachers.size() == 1)
		var breacher: int = breachers[0]
		var placed := false
		var width := int(mission.objective.get("breach_half_width_cells", 3))
		for y in range(maxi(0, marker.y - width), mini(mission.GRID_ROWS, marker.y + width + 1)):
			var goal := Vector2i(marker.x, y)
			var start := goal + Vector2i.RIGHT
			if mission._battlefield.is_wall(goal) or mission._battlefield.is_wall(start):
				continue
			if mission._is_cell_occupied(goal, -1, breacher) or mission._is_cell_occupied(start, -1, breacher):
				continue
			mission.enemy_units[breacher].position = start
			placed = true
			break
		assert(placed, "The authored breach needs an unoccupied approach for this fixture.")
		mission.turn_side = "enemy"
		mission._resolve_enemy_turn()
		assert(mission._containment_breached())
	elif kind == "defend":
		assert(not mission._defense_zone_breached())
		mission.turn_number = int(mission.objective["defend_turns_required"])
		mission.turn_side = "enemy"
		mission._resolve_enemy_turn()
		assert(mission._enemy_alive_count() > 0)
	else:
		var actor := mission.player_units[mission.active_player_index] as Dictionary
		actor["aim"] = 100
		var priority_target: int = mission._assassination_target_index()
		for index in range(mission.enemy_units.size()):
			if kind == "assassination" and index != priority_target:
				continue
			var enemy := mission.enemy_units[index] as Dictionary
			enemy["hp"] = 1
			enemy["defense"] = 0
			enemy["position"] = mission._cell_position(actor) + Vector2i.RIGHT
			for attempt in range(20):
				actor["ap"] = 4
				mission._attack_enemy(index, "Rifle Burst")
				if int(enemy.get("hp", 0)) == 0:
					break
			assert(int(enemy.get("hp", 0)) == 0)
		if kind == "assassination":
			assert(priority_target >= 0 and mission._enemy_alive_count() > 0)

	assert(mission.battle_ended)
	assert(mission._results._outcome == expected)
	if expected == "victory":
		assert(mission.objective_completed)
	else:
		assert(not mission.objective_completed)
	var session: Dictionary = mission.handoff.session
	assert(FileAccess.file_exists(session.prepared_path))
	assert(not FileAccess.file_exists(session.result_path))
	mission._results._extract_btn.pressed.emit()
	assert(FileAccess.file_exists(session.result_path))
	print("REGIONAL_NATIVE_OUTCOME_PASSED objective=", kind, " outcome=", expected)
	quit()
