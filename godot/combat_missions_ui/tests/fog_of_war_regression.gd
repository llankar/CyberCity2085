extends SceneTree

class ResultSink extends Control:
	var outcome := ""

	func show_banner(_side: String, _turn: int) -> void:
		pass

	func show_results(result: String, _data: Dictionary, _root: String, _pipe: String, _audio) -> void:
		outcome = result

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var fog = preload("res://scripts/fog_of_war.gd")
	var clear_los := func(_origin: Vector2i, _destination: Vector2i): return true
	var blocked_los := func(origin: Vector2i, destination: Vector2i):
		return not (origin.y == 0 and destination.y == 0 and origin.x < 2 and destination.x > 2)
	var scout := {"hp": 20, "position": Vector2i(0, 0), "vision_range": 15}
	var near := {"hp": 10, "position": Vector2i(0, 15), "vision_range": 15}
	var far := {"hp": 10, "position": Vector2i(0, 16), "vision_range": 15}
	var hidden := {"hp": 10, "position": Vector2i(3, 0), "vision_range": 15}
	assert(fog.can_see(scout, near, clear_los), "target at 15 cells must be visible")
	assert(not fog.can_see(scout, far, clear_los), "target at 16 cells must remain hidden")
	assert(not fog.can_see(scout, hidden, blocked_los), "opaque obstacle must preserve fog behind it")
	var units: Array[Dictionary] = [scout]
	var cells: Dictionary = fog.visible_cells(units, 40, 28, blocked_los)
	assert(cells.has(Vector2i(0, 15)), "vision map must include the fifteenth cell")
	assert(not cells.has(Vector2i(0, 16)), "vision map must exclude the sixteenth cell")
	assert(not cells.has(Vector2i(3, 0)), "vision map leaked behind LOS blocker")
	var cybereyes := {"hp": 20, "position": Vector2i(0, 0), "vision_range": 18}
	assert(fog.can_see(cybereyes, far, clear_los), "Cybereyes Mk III must extend vision to 18")
	var board = load("res://scripts/battlefield.gd").new()
	var walls: Array[Dictionary] = []
	for x in range(40):
		for y in [0, 2]:
			walls.append({"cell": Vector2i(x, y), "solid": true})
	board.configure(Vector2(1280, 720), null, walls, Vector2i(20, 14))
	var mission = load("res://scripts/combat_mission_ui.gd").new()
	mission._battlefield = board
	var start := Vector2i(1, 1)
	mission.player_units.assign([{"hp": 20, "position": Vector2i(13, 1)}])
	mission.enemy_units.assign([
		{"hp": 20, "ap": 4, "position": start, "enemy_subtype": "grunt"},
		{"hp": 20, "position": Vector2i(2, 1)},
	])
	mission._enemy_act(0)
	assert(mission.enemy_units[0]["position"] == start, "pursuit cannot cross an allied unit")
	assert(mission.enemy_units[0]["ap"] == 4, "blocked pursuit consumes no move AP")
	mission.enemy_units.pop_back()
	mission._enemy_act(0)
	assert(mission.enemy_units[0]["position"] == Vector2i(3, 1), "pursuit stops at the first legal shot")
	var no_walls: Array[Dictionary] = []
	board.configure(Vector2(1280, 720), null, no_walls, Vector2i(2, 1))
	mission.objective = {"type": "containment", "cell": Vector2i(2, 1)}
	mission.enemy_units.assign([
		{"hp": 20, "ap": 4, "position": Vector2i(5, 1)},
		{"hp": 20, "position": Vector2i(4, 1)},
	])
	mission._enemy_containment_act(0)
	var detour: Vector2i = mission.enemy_units[0]["position"]
	assert(detour.x == 5 and absi(detour.y - 1) == 1, "breacher detours around an ally")
	var center := Vector2i(20, 14)
	var center_wall: Array[Dictionary] = [{"cell": center, "solid": true}]
	board.configure(Vector2(1280, 720), null, center_wall, center)
	mission.player_units.assign([{"hp": 20, "position": Vector2i(39, 27)}])
	mission.enemy_units.assign([{"hp": 20, "ap": 3, "position": Vector2i(15, 14)}])
	mission._enemy_act(0)
	assert(mission.enemy_units[0]["position"] == Vector2i(17, 14), "a blocked search goal still permits movement")
	assert(mission.player_units[0]["hp"] == 20, "search cannot attack a hidden target")
	assert(board.find_path(Vector2i(19, 14), center).is_empty(), "exact paths still reject blocked destinations")
	board.configure(Vector2(1280, 720), null, no_walls, center)
	var shooter := {"hp": 20, "position": Vector2i(5, 5)}
	mission.player_units.assign([
		{"hp": 20, "defense": 10, "position": Vector2i(6, 5)},
		{"hp": 20, "defense": 3, "position": Vector2i(9, 5)},
		{"hp": 20, "defense": 0, "position": Vector2i(22, 5)},
	])
	assert(mission._select_visible_player_target(shooter, "grunt", 10) == 0, "grunt prioritizes proximity")
	assert(mission._select_visible_player_target(shooter, "elite", 24) == 1, "elite prioritizes the exposed visible target")
	assert(mission._select_visible_player_target(shooter, "elite", 3) == 0, "elite prefers an available shot")
	var low_wall: Array[Dictionary] = [{"cell": Vector2i(6, 6), "solid": true, "high": false}]
	board.configure(Vector2(1280, 720), null, low_wall, center)
	mission.player_units.assign([{"hp": 20, "position": Vector2i(9, 5)}])
	mission.enemy_units.assign([{"hp": 20, "ap": 2, "position": Vector2i(5, 5), "enemy_subtype": "elite"}])
	mission._enemy_act(0)
	assert(mission.enemy_units[0]["position"] == Vector2i(5, 6), "elite moves to low cover toward its target")
	assert(mission.enemy_units[0]["ap"] == 0, "elite spends one AP on repositioning and one on fire")
	mission.enemy_units.assign([{"hp": 20, "ap": 2, "position": Vector2i(5, 5), "enemy_subtype": "grunt"}])
	mission._enemy_act(0)
	assert(mission.enemy_units[0]["position"] == Vector2i(5, 5), "grunt holds an available firing position")
	mission.player_units.assign([
		{"hp": 20, "max_hp": 20, "position": Vector2i(6, 5)},
		{"hp": 6, "max_hp": 20, "position": Vector2i(9, 5)},
	])
	mission.handoff = {"mission": {"tactical_profile": {"wounded_weight": 38, "distance_weight": 3}}}
	assert(mission._select_visible_player_target(shooter, "grunt", 10) == 1, "Novatek prioritizes wounded targets")
	assert(mission._select_visible_player_target(shooter, "grunt", 2) == 0, "doctrine cannot override range")
	board.configure(Vector2(1280, 720), null, no_walls, center)
	mission.handoff = {"mission": {"tactical_profile": {"command_radius_cells": 4}}}
	mission.player_units.assign([
		{"hp": 20, "position": Vector2i(6, 5)},
		{"hp": 20, "position": Vector2i(5, 9)},
	])
	mission.enemy_units.assign([
		{"hp": 20, "position": Vector2i(5, 5), "enemy_theme": "corp_37"},
		{"hp": 20, "position": Vector2i(5, 8), "enemy_theme": "corp_37", "enemy_subtype": "commander"},
	])
	assert(mission._enemy_engagement_target(0, "grunt", 10) == 1, "linked follower shares commander target")
	assert(mission._enemy_engagement_target(0, "grunt", 2) == 0, "follower cannot fire beyond range")
	mission.enemy_units[0]["vision_range"] = 2
	assert(mission._enemy_engagement_target(0, "grunt", 10) == 0, "command link cannot reveal targets")
	mission.enemy_units[0].erase("vision_range")
	mission.enemy_units[1]["status_effects"] = ["suppressed"]
	assert(mission._enemy_engagement_target(0, "grunt", 10) == 0, "suppressed commander loses the link")
	mission.enemy_units[1]["status_effects"] = []
	var link_wall: Array[Dictionary] = [{"cell": Vector2i(5, 6), "solid": true}]
	board.configure(Vector2(1280, 720), null, link_wall, center)
	assert(mission._linked_enemy_commander(0) == -1, "opaque wall breaks commander link")
	mission.enemy_units.clear()
	for action in ["EXTRACT", "RESCUE", "HACK"]:
		mission.objective = {"needs_marker": true, "action_key": action}
		assert(not mission._elimination_objective_met(), "an interactive objective still requires its action")
	mission.objective = {"needs_marker": false, "type": "kill_all"}
	assert(mission._elimination_objective_met(), "elimination missions still reward clearing the board")
	var generator = load("res://scripts/encounter_generator.gd").new()
	mission.objective = generator.build_objective("data_with_detour", 40, 28)
	assert(mission.objective.progress_needed == 2, "data download takes two interactions")
	mission.battle_ended = true # Skip presentation in the headless fixture.
	mission.turn_number = 1
	mission.active_player_index = 0
	mission.player_units.assign([{"hp": 20, "ap": 3}, {"hp": 20, "ap": 3}])
	mission._interact_with_objective()
	assert(mission.objective_progress == 1 and not mission.objective_completed)
	assert(mission.player_units[0].ap == 2)
	mission.active_player_index = 1
	mission._interact_with_objective()
	assert(mission.objective_progress == 1 and mission.player_units[1].ap == 3)
	mission.turn_number += 1
	assert(mission._objective_interaction_available(), "next squad turn can complete the download")
	var layout = load("res://scripts/map_wall_layout.gd")
	mission.objective = generator.build_objective("safe_extraction", 40, 28)
	mission.player_units.assign([{"hp": 20, "ap": 3, "position": Vector2i(1, 1)}])
	mission.active_player_index = 0
	mission.objective_progress = 0
	layout.place_encounter(mission.player_units, mission.enemy_units, mission.objective, board)
	var witness: Vector2i = mission.objective.cell
	mission._interact_with_objective()
	var exit: Vector2i = mission.objective.cell
	assert(exit != witness and not board.is_wall(exit), "witness secured reveals a distinct floor marker")
	assert(not board.find_path(witness, exit).is_empty(), "extraction stays reachable")
	assert(board.objective_cell == exit and mission.objective.label == "Reach Extraction")
	assert(not mission.objective_completed and not mission._objective_interaction_available())
	mission.objective = generator.build_objective("data_with_detour", 40, 28)
	mission.objective_progress = 0
	mission.turn_number = 1
	mission.player_units[0].ap = 3
	layout.place_encounter(mission.player_units, mission.enemy_units, mission.objective, board)
	var terminal: Vector2i = mission.objective.cell
	mission.player_units[0].position = terminal - Vector2i(1, 0)
	mission.enemy_units.assign([{"hp": 20, "position": terminal + Vector2i(1, 0)}])
	mission._interact_with_objective()
	assert(mission.objective.progress_needed == 3 and mission.objective_progress == 1)
	assert(mission.objective.cell != terminal and mission.objective.label == "Establish Field Proxy")
	assert(not board.find_path(terminal, mission.objective.cell).is_empty())
	mission.turn_number += 1
	mission.player_units[0].position = mission.objective.cell
	mission._interact_with_objective()
	assert(mission.objective_progress == 2 and not mission.objective_completed)
	assert(mission.objective.label == "Complete Download")
	var sink := ResultSink.new()
	mission._banner = sink
	mission._results = sink
	mission.player_units[0]["name"] = "Witness Escort"
	mission.player_units[0]["max_hp"] = 20
	mission.turn_number += 1
	mission._interact_with_objective()
	assert(sink.outcome == "victory" and mission.objective_completed)
	mission.enemy_units.clear()
	mission.objective = generator.build_objective("sabotage_window", 40, 28)
	mission.objective_completed = false
	mission.objective_progress = 0
	mission.player_units[0].ap = 3
	mission._interact_with_objective()
	assert(not mission.objective_completed)
	assert(mission.objective.hold_until_turn == mission.turn_number + 1)
	mission._interact_with_objective()
	assert(mission.player_units[0].ap == 2, "arming only spends AP once")
	assert(not mission._elimination_objective_met(), "clearing hostiles cannot skip the hold")
	var armed_turn: int = mission.turn_number
	for survives in [true, false]:
		mission.turn_number = armed_turn
		mission.turn_side = "enemy"
		mission.objective_completed = false
		mission.player_units[0].hp = 20 if survives else 0
		mission._resolve_enemy_turn()
		assert(sink.outcome == ("victory" if survives else "defeat"))
		assert(mission.objective_completed == survives)
	mission.objective = generator.build_objective("defend", 40, 28)
	mission.objective.cell = Vector2i(14, 14)
	mission.player_units[0].hp = 20
	mission.turn_number = 3
	mission.turn_side = "enemy"
	mission.objective_completed = false
	sink.outcome = ""
	assert(not mission._elimination_objective_met())
	mission._resolve_enemy_turn()
	assert(sink.outcome.is_empty() and mission.objective_progress == 3)
	mission.turn_side = "enemy"
	mission._resolve_enemy_turn()
	assert(sink.outcome == "victory" and mission.objective_progress == 4)
	mission.turn_side = "enemy"
	mission.turn_number = 4
	mission.objective_completed = false
	mission.enemy_units.assign([{"hp": 20, "position": Vector2i(16, 14)}])
	mission._resolve_enemy_turn()
	assert(mission.enemy_units[0].position == Vector2i(15, 14), "breacher advances to the defense zone")
	assert(sink.outcome == "defeat" and not mission.objective_completed)
	mission.objective.cell = Vector2i(14, 14)
	mission.enemy_units[0].position = Vector2i(15, 14)
	layout.place_encounter(mission.player_units, mission.enemy_units, mission.objective, board)
	assert(not mission._defense_zone_breached(), "deployment cannot place a guard inside the marked defense zone")
	mission.player_units.assign([
		{"name": "Oracle", "hp": 20, "ap": 3, "stress": 0},
		{"name": "Rook", "hp": 0, "stress": 35},
		{"name": "Vera", "hp": 10, "stress": 0},
	])
	mission.active_player_index = 0
	mission._apply_psi_focus()
	assert(mission.player_units[0].ap == 3 and mission.player_units[1].stress == 35)
	mission.player_units[2].stress = 8
	mission._apply_psi_focus()
	assert(mission.player_units[0].ap == 2 and mission.player_units[2].stress == 0)
	assert(mission.player_units[1].stress == 35 and "8 stress" in mission.status_line)
	var medical_healing := {"Trauma Patch": 12, "Med Kit Pro": 16, "Nano-Repair Kit": 18}
	for item in medical_healing:
		var patient := {"name": "Oracle", "hp": 10, "max_hp": 40, "ap": 3, "available_actions": [item]}
		mission.player_units[0] = patient
		mission._apply_medical_utility(item)
		assert(patient.hp == 10 + medical_healing[item])
		assert(patient.ap == 2 and item in mission.status_line)
		patient.hp = 39
		mission._apply_medical_utility(item)
		assert(patient.hp == 40 and patient.ap == 1)
		mission._apply_medical_utility(item)
		assert(patient.ap == 1)
		patient.hp = 20
		patient.available_actions = []
		mission._apply_medical_utility(item)
		assert(patient.hp == 20 and patient.ap == 1)
	mission._hud = load("res://scripts/hud_controller.gd").new()
	assert(mission._attack_audio_event({}, "Mind Spike", "PSI") == "psi")
	mission._configure_visual_hud()
	mission._hud.size = Vector2(1280, 720)
	mission._hud.player_units.assign([{"available_actions": [
		"Move", "Psi Focus", "Trauma Patch", "VTOL Heavy Strike",
		"Adrenaline Shot", "Smoke Grenade", "Tactical Scanner", "Stim Pack", "Hacking Module",
	]}])
	mission._hud._rebuild_agent_actions()
	assert(mission._hud._visible_actions == [
		"Move", "Psi Focus", "Trauma Patch", "VTOL Heavy Strike", "RETREAT", "NEXT", "END TURN",
	])
	assert("1 AP" in mission._hud._action_btns["Psi Focus"].tooltip_text)
	assert("25 stress per living" in mission._hud._action_btns["Psi Focus"].tooltip_text)
	assert("12 HP to this agent" in mission._hud._action_btns["Trauma Patch"].tooltip_text)
	mission._hud.free()
	mission._hud = null
	mission.player_units.assign([{"name": "Oracle", "hp": 20, "max_hp": 20, "ap": 3, "position": Vector2i(1, 1)}])
	mission.enemy_units.clear()
	for kind in ["civilian_rescue", "recon_scan"]:
		mission.objective = generator.build_objective(kind, 40, 28)
		mission.objective_progress = 0
		mission.objective_completed = false
		sink.outcome = ""
		layout.place_encounter(mission.player_units, mission.enemy_units, mission.objective, board)
		var visited: Array[Vector2i] = []
		for step in range(3):
			var marker: Vector2i = mission.objective.cell
			assert(not board.is_wall(marker) and marker not in visited)
			if not visited.is_empty():
				assert(not board.find_path(visited.back(), marker).is_empty())
			visited.append(marker)
			assert(mission.objective.label == mission.objective.phase_labels[step])
			mission.player_units[0].position = marker
			mission.player_units[0].ap = 2
			mission._interact_with_objective()
			assert(mission.objective_progress == step + 1)
			if step < 2:
				assert(sink.outcome.is_empty() and not mission._objective_interaction_available())
			mission.turn_number += 1
		assert(sink.outcome == "victory" and mission.objective_completed)
	sink.free()
	mission.free()
	board.free()
	print("GODOT_FOG_OF_WAR_CHECKS_PASSED")
	quit(0)
