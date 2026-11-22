extends SceneTree
## Drives both containment terminal states through normal combat actions.
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
	assert(mission.objective.get("type", "") == "containment")

	if expected == "defeat":
		var marker := mission.objective.cell as Vector2i
		var breacher: int = mission._containment_breacher_index()
		assert(breacher >= 0)
		mission.enemy_units[breacher].position = marker + Vector2i.RIGHT
		mission.turn_side = "enemy"
		mission._resolve_enemy_turn()
		assert(mission._containment_breached())
	else:
		var actor := mission.player_units[mission.active_player_index] as Dictionary
		actor["aim"] = 100
		for index in range(mission.enemy_units.size()):
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
	print("CONTAINMENT_NATIVE_OUTCOME_PASSED outcome=", expected)
	quit()
