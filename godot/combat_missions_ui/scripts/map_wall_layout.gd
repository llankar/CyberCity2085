extends RefCounted
## Stored wall cells share the background texture UVs (top-left origin).

const _BATTLEFIELD := preload("res://scripts/battlefield.gd")

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

static func largest_floor_region(board, near: Vector2i) -> Array[Vector2i]:
	# Ignore temporary unit occupancy when choosing the playable arena.
	var remaining: Dictionary = {}
	for y in range(board.GRID_ROWS):
		for x in range(board.GRID_COLS):
			var cell := Vector2i(x, y)
			if not board.is_wall(cell): remaining[cell] = true
	var best: Array[Vector2i] = []
	var best_distance := 999999
	while not remaining.is_empty():
		var first: Vector2i = remaining.keys()[0]
		var region: Array[Vector2i] = [first]
		remaining.erase(first)
		var index := 0
		var distance := 999999
		while index < region.size():
			var cell := region[index]
			index += 1
			distance = mini(distance, absi(cell.x-near.x)+absi(cell.y-near.y))
			for neighbor: Vector2i in [cell+Vector2i.RIGHT, cell+Vector2i.DOWN, cell+Vector2i.LEFT, cell+Vector2i.UP]:
				if remaining.has(neighbor):
					remaining.erase(neighbor)
					region.append(neighbor)
		if region.size() > best.size() or (region.size() == best.size() and distance < best_distance):
			best = region
			best_distance = distance
	return best

static func place_encounter(players: Array[Dictionary], enemies: Array[Dictionary], objective: Dictionary, board) -> void:
	if players.is_empty():
		return
	var floor_cells := largest_floor_region(board, players[0].get("position", Vector2i.ZERO))
	if floor_cells.is_empty(): return
	var origin: Vector2i = floor_cells[0]
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
	var threatened := {}
	if objective.get("type", "") == "defend":
		for enemy in enemies:
			if int(enemy.get("hp", 0)) > 0:
				for cell in _BATTLEFIELD.defense_zone_cells(enemy["position"]):
					threatened[cell] = true
	var desired: Vector2i = objective.get("cell", origin)
	var closest := origin
	var distance := 99999
	for cell: Vector2i in floor_cells:
		var candidate_distance := absi(cell.x-desired.x) + absi(cell.y-desired.y)
		if candidate_distance < distance and not occupied.has(cell) and not threatened.has(cell):
			closest = cell
			distance = candidate_distance
	objective["cell"] = closest
	board.objective_cell = closest
	for marker in ["extraction", "field_proxy"]:
		var offset: Array = objective.get(marker + "_offset", [])
		if offset.size() != 2:
			continue
		var desired_exit := closest + Vector2i(int(offset[0]), int(offset[1]))
		var exit_distance := 99999
		for cell in floor_cells:
			var separation := absi(cell.x-closest.x) + absi(cell.y-closest.y)
			var candidate_distance := absi(cell.x-desired_exit.x) + absi(cell.y-desired_exit.y)
			if separation > int(objective.get("interact_range", 2)) and candidate_distance < exit_distance and not occupied.has(cell):
				objective[marker + "_cell"] = [cell.x, cell.y]
				exit_distance = candidate_distance
	var offsets: Array = objective.get("phase_offsets", [])
	if not offsets.is_empty():
		var used: Array[Vector2i] = [closest]
		var followups: Array = []
		for offset in offsets:
			var preferred := closest + Vector2i(int(offset[0]), int(offset[1]))
			var next := used.back() as Vector2i
			var best_distance := 99999
			for cell in floor_cells:
				var candidate_distance := absi(cell.x-preferred.x) + absi(cell.y-preferred.y)
				if candidate_distance < best_distance and not used.has(cell) and not occupied.has(cell):
					next = cell
					best_distance = candidate_distance
			used.append(next)
			followups.append([next.x, next.y])
		objective["phase_cells"] = followups
