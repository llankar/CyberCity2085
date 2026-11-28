extends RefCounted

static func breacher_indices(enemy_units: Array, objective: Dictionary) -> Array[int]:
	var target := objective.get("cell", Vector2i.ZERO) as Vector2i
	var candidates: Array[Vector2i] = []
	for index in range(enemy_units.size()):
		var enemy := enemy_units[index] as Dictionary
		if int(enemy.get("hp", 0)) <= 0: continue
		var cell := enemy.get("position", Vector2i.ZERO) as Vector2i
		var dx := cell.x - target.x
		var distance := (absi(dx) if objective.get("type") == "defend" else maxi(0, dx)) + absi(cell.y - target.y)
		candidates.append(Vector2i(distance, index))
	candidates.sort_custom(func(a: Vector2i, b: Vector2i): return a.y < b.y if a.x == b.x else a.x < b.x)
	var selected: Array[int] = []
	var limit := clampi(int(objective.get("active_breachers", 1)), 0, candidates.size())
	for index in range(limit):
		selected.append(candidates[index].y)
	return selected

static func target_cell(enemy_cell: Vector2i, objective: Dictionary) -> Vector2i:
	var marker := objective.get("cell", Vector2i.ZERO) as Vector2i
	var half_width := int(objective.get("breach_half_width_cells", 3))
	return Vector2i(marker.x, clampi(enemy_cell.y, marker.y - half_width, marker.y + half_width))

static func breached(enemy_units: Array, objective: Dictionary) -> bool:
	if objective.get("type", "") != "containment": return false
	var marker := objective.get("cell", Vector2i.ZERO) as Vector2i
	var half_width := int(objective.get("breach_half_width_cells", 3))
	for value in enemy_units:
		var enemy := value as Dictionary
		if int(enemy.get("hp", 0)) <= 0: continue
		var cell := enemy.get("position", Vector2i.ZERO) as Vector2i
		if cell.x <= marker.x and absi(cell.y - marker.y) <= half_width:
			return true
	return false
