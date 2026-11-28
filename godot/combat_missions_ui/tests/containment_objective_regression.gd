extends SceneTree

func _init() -> void:
	var generator = preload("res://scripts/encounter_generator.gd").new()
	var objective: Dictionary = generator.build_objective(
		"containment", 40, 28,
		{"breach_half_width_cells": 3, "active_breachers": 1, "breach_steps_per_phase": 1},
	)
	assert(objective["needs_marker"] and not objective["interactive"])
	assert(objective["cell"] == Vector2i(14, 14))
	assert(objective["breach_half_width_cells"] == 3)

	var rules = preload("res://scripts/containment_objective.gd")
	var enemies := [
		{"hp": 10, "position": Vector2i(24, 18)},
		{"hp": 10, "position": Vector2i(20, 14)},
		{"hp": 0, "position": Vector2i(14, 14)},
	]
	assert(rules.breacher_indices(enemies, objective) == [1])
	objective["active_breachers"] = 3
	assert(rules.breacher_indices(enemies, objective) == [1, 0])
	assert(rules.target_cell(Vector2i(20, 20), objective) == Vector2i(14, 17))
	assert(not rules.breached(enemies, objective))
	enemies[1]["position"] = Vector2i(14, 17)
	assert(rules.breached(enemies, objective))
	enemies[1]["position"] = Vector2i(14, 18)
	assert(not rules.breached(enemies, objective))
	print("CONTAINMENT_OBJECTIVE_CHECKS_PASSED")
	quit(0)
