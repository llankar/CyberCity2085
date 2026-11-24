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
	print("GODOT_FOG_OF_WAR_CHECKS_PASSED")
	quit(0)
