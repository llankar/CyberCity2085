extends RefCounted
class_name SpikeCombatRules

const MOVE_COST := 1
const ATTACK_COST := 1
const ATTACK_DAMAGE := 4
const ATTACK_RANGE := 1

static func unit_at(state: SpikeMissionState, x: int, y: int) -> Dictionary:
	for unit in state.units:
		var pos: Dictionary = unit.get("position", {})
		if int(pos.get("x", -1)) == x and int(pos.get("y", -1)) == y and int(unit.get("hp", 0)) > 0:
			return unit
	return {}

static func move_unit(state: SpikeMissionState, unit_id: String, dx: int, dy: int) -> bool:
	var unit := _find_living_unit(state, unit_id)
	if unit.is_empty() or int(unit.get("ap", 0)) < MOVE_COST:
		return false
	var pos: Dictionary = unit.get("position", {})
	var nx := int(pos.get("x", 0)) + dx
	var ny := int(pos.get("y", 0)) + dy
	if nx < 0 or ny < 0 or nx >= SpikeMissionState.GRID_WIDTH or ny >= SpikeMissionState.GRID_HEIGHT:
		return false
	if not unit_at(state, nx, ny).is_empty():
		return false
	unit["position"] = {"x": nx, "y": ny}
	unit["ap"] = int(unit.get("ap", 0)) - MOVE_COST
	state.event_log.append("%s moves to %d,%d." % [unit_id, nx, ny])
	return true

static func attack_unit(state: SpikeMissionState, attacker_id: String, target_id: String) -> bool:
	var attacker := _find_living_unit(state, attacker_id)
	var target := _find_living_unit(state, target_id)
	if attacker.is_empty() or target.is_empty() or int(attacker.get("ap", 0)) < ATTACK_COST:
		return false
	if attacker.get("team") == target.get("team") or _distance(attacker, target) > ATTACK_RANGE:
		return false
	target["hp"] = max(0, int(target.get("hp", 0)) - ATTACK_DAMAGE)
	attacker["ap"] = int(attacker.get("ap", 0)) - ATTACK_COST
	state.event_log.append("%s attacks %s for %d." % [attacker_id, target_id, ATTACK_DAMAGE])
	_update_result(state)
	return true

static func end_turn(state: SpikeMissionState) -> void:
	if state.result != "in_progress":
		return
	state.turn = "enemy" if state.turn == "player" else "player"
	if state.turn == "player":
		state.turn_number += 1
	for unit in state.units:
		if int(unit.get("hp", 0)) > 0 and unit.get("team") == state.turn:
			unit["ap"] = 2
	state.event_log.append("Turn changes to %s." % state.turn)

static func _find_living_unit(state: SpikeMissionState, unit_id: String) -> Dictionary:
	for unit in state.units:
		if unit.get("id") == unit_id and int(unit.get("hp", 0)) > 0:
			return unit
	return {}

static func _distance(a: Dictionary, b: Dictionary) -> int:
	var ap: Dictionary = a.get("position", {})
	var bp: Dictionary = b.get("position", {})
	return abs(int(ap.get("x", 0)) - int(bp.get("x", 0))) + abs(int(ap.get("y", 0)) - int(bp.get("y", 0)))

static func _update_result(state: SpikeMissionState) -> void:
	if state.living_units("enemy").is_empty():
		state.result = "victory"
	elif state.living_units("agent").is_empty():
		state.result = "defeat"
