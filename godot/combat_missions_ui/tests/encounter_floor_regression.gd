extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var board = load("res://scripts/battlefield.gd").new()
	root.add_child(board)
	var layout = load("res://scripts/map_wall_layout.gd")
	var assets := ProjectSettings.globalize_path("res://../../assets/maps")
	var checked := 0
	for filename in DirAccess.get_files_at(assets):
		if not filename.ends_with(".walls.json"): continue
		var geometry: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(assets.path_join(filename)))
		board.configure(Vector2(5120,2880),null,layout.cover_nodes(geometry),Vector2i(38,14))
		var original_walls: Array = board._wall_cells.duplicate()
		var players: Array[Dictionary] = []
		var enemies: Array[Dictionary] = []
		for row in [3,7,11,15,19,23]: players.append({"position":Vector2i(1,row)})
		for row in [3,7,11,15,19,23]: enemies.append({"position":Vector2i(38,row)})
		var objective := {"cell":Vector2i(38,14)}
		layout.place_encounter(players,enemies,objective,board)
		var arena: Array[Vector2i] = layout.largest_floor_region(board,Vector2i(1,3))
		assert(arena.size() >= 13,filename+": room for encounter")
		var occupied: Array[Vector2i] = []
		for group in [players,enemies]:
			for unit in group:
				var cell: Vector2i = unit["position"]
				assert(arena.has(cell),filename+": spawn in main arena")
				assert(not occupied.has(cell),filename+": unique spawn")
				occupied.append(cell)
				assert(not board.find_path(cell,objective["cell"]).is_empty(),filename+": objective reachable")
		assert(board._wall_cells == original_walls,filename+": walls unchanged")
		if "underground_market" in filename:
			assert(arena.size()==421,filename+": interior, not the isolated 68-cell border")
		checked += 1
	board.free()
	print("ENCOUNTER_FLOOR_CHECKS_PASSED ",checked)
	quit()
