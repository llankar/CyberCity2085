extends SceneTree

func _initialize() -> void:
	var combat = load("res://scripts/combat_mission_ui.gd").new()
	combat.enemy_units.assign([
		{"enemy_subtype": "elite", "hp": 0},
		{"name": "Commander", "enemy_subtype": "commander", "hp": 5, "position": Vector2i(8, 4)},
		{"enemy_subtype": "grunt", "hp": 8},
	])
	combat.initial_enemy_count = 3
	combat.objective = {"type": "assassination", "progress_needed": 1}
	assert(combat._assassination_target_index() == 1)
	assert(not combat._elimination_objective_met())
	assert(combat._assassination_objective_text() == "PRIORITY TARGET // Locate the target")
	combat._player_visible_cells[Vector2i(8, 4)] = true
	assert(combat._assassination_objective_text() == "PRIORITY TARGET // Commander")
	combat.enemy_units[1].hp = 0
	assert(combat._elimination_objective_met())
	assert(combat.objective_completed and combat.objective_progress == 1)
	assert(combat._assassination_objective_text() == "PRIORITY TARGET NEUTRALIZED")
	combat.objective.type = "kill_all"
	assert(not combat._elimination_objective_met())
	combat.free()
	print("ASSASSINATION_OBJECTIVE_PASSED")
	quit()
