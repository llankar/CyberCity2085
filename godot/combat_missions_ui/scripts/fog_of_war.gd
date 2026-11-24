extends RefCounted
## Pure tactical visibility rules shared by player rendering and enemy AI.

const BASE_VISION_RANGE := 15

static func vision_range(unit: Dictionary) -> int:
	return maxi(1, int(unit.get("vision_range", BASE_VISION_RANGE)))

static func can_see(observer: Dictionary, target: Dictionary, has_los: Callable) -> bool:
	if int(observer.get("hp", 0)) <= 0 or int(target.get("hp", 0)) <= 0:
		return false
	var origin: Vector2i = observer.get("position", Vector2i.ZERO)
	var destination: Vector2i = target.get("position", Vector2i.ZERO)
	var distance := absi(origin.x - destination.x) + absi(origin.y - destination.y)
	return distance <= vision_range(observer) and bool(has_los.call(origin, destination))

static func visible_cells(units: Array[Dictionary], cols: int, rows: int,
		has_los: Callable) -> Dictionary:
	var result := {}
	for unit: Dictionary in units:
		if int(unit.get("hp", 0)) <= 0:
			continue
		var origin: Vector2i = unit.get("position", Vector2i.ZERO)
		var sight := vision_range(unit)
		for y in range(maxi(0, origin.y - sight), mini(rows, origin.y + sight + 1)):
			for x in range(maxi(0, origin.x - sight), mini(cols, origin.x + sight + 1)):
				var cell := Vector2i(x, y)
				if absi(origin.x - x) + absi(origin.y - y) <= sight \
						and bool(has_los.call(origin, cell)):
					result[cell] = true
	return result
