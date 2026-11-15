extends RefCounted
## Stored wall cells share the background texture UVs (top-left origin).

static func geometry_for_map(map_data: Dictionary, asset_root: String) -> Dictionary:
	var geometry := map_data.get("geometry", {}) as Dictionary
	var image_path := str(map_data.get("path", "")).replace("\\", "/")
	if image_path.is_empty():
		return geometry
	if not image_path.is_absolute_path():
		image_path = asset_root.replace("\\", "/").path_join(image_path)
	var sidecar := image_path.get_basename() + ".walls.json"
	if not FileAccess.file_exists(sidecar):
		return geometry
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(sidecar))
	# A restarted standalone scene may still carry an old embedded handoff.
	# Prefer the current stored survey so wall corrections are actually visible.
	if parsed is Dictionary and str(parsed.get("image", "")) == image_path.get_file():
		return parsed
	return geometry

static func cover_nodes(geometry: Dictionary) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	var seen: Dictionary = {}
	# JSON numbers arrive as floats. Array equality against integer literals
	# rejects an otherwise valid persisted survey, silently dropping all walls.
	var grid: Array = geometry.get("grid", [])
	if grid.size() != 2 or int(grid[0]) != 40 or int(grid[1]) != 28:
		return result
	for wall: Dictionary in geometry.get("walls", []):
		for pair: Array in wall.get("cells", []):
			if pair.size() != 2:
				continue
			var cell := Vector2i(int(pair[0]), int(pair[1]))
			if cell.x < 0 or cell.x >= 40 or cell.y < 0 or cell.y >= 28 or seen.has(cell):
				continue
			seen[cell] = true
			result.append({"cell": cell, "high": bool(wall.get("blocks_sight", true)), "solid": true, "wall_id": str(wall.get("id", "")), "kind":str(wall.get("kind", "solid_obstacle")), "outline_uv": wall.get("outline_uv", [])})
	return result

static func place_encounter(players: Array[Dictionary], enemies: Array[Dictionary], objective: Dictionary, board) -> void:
	if players.is_empty():
		return
	var origin: Vector2i = board.nearest_open_cell(players[0].get("position", Vector2i.ZERO))
	var floor_cells: Array[Vector2i] = board.reachable_cells(origin, 40*28)
	floor_cells.append(origin)
	var occupied: Array[Vector2i] = []
	for group: Array in [players, enemies]:
		for unit: Dictionary in group:
			var desired: Vector2i = unit.get("position", origin)
			var best := Vector2i(-1, -1)
			var best_distance := 99999
			for cell: Vector2i in floor_cells:
				var distance := absi(cell.x-desired.x) + absi(cell.y-desired.y)
				if not occupied.has(cell) and distance < best_distance:
					best = cell
					best_distance = distance
			if best.x >= 0:
				unit["position"] = best
				occupied.append(best)
	var desired: Vector2i = objective.get("cell", origin)
	var closest := origin
	var distance := 99999
	for cell: Vector2i in floor_cells:
		var candidate_distance := absi(cell.x-desired.x) + absi(cell.y-desired.y)
		if candidate_distance < distance and not occupied.has(cell):
			closest = cell
			distance = candidate_distance
	objective["cell"] = closest
	board.objective_cell = closest
