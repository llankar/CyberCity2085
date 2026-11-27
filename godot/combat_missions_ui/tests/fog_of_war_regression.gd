extends SceneTree

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
	mission.free()
	board.free()
	print("GODOT_FOG_OF_WAR_CHECKS_PASSED")
	quit(0)
