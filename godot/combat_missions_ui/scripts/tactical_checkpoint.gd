extends RefCounted
## Runtime-only snapshot; static walls/cover, combat rules and campaign stay outside.
const FIELDS := ["initial_enemy_count", "turn_side", "turn_number", "enemy_turn_timer",
	"active_player_index", "_queued_player_index", "selected_target_index", "selected_action",
	"pending_end_turn_confirmation", "show_combat_log", "objective_progress", "objective_completed",
	"overwatch_indices", "defend_indices", "combat_log"]
const GROUPS := ["player_units", "enemy_units", "vehicle_units"]

static func capture(scene: Node) -> Dictionary:
	var session: Dictionary = scene.handoff.get("session", {})
	var state := {}
	for field in FIELDS: state[field] = scene.get(field)
	for group in GROUPS:
		var rows := []
		for unit: Dictionary in scene.get(group):
			var row := unit.duplicate(true)
			var cell: Vector2i = row.position
			row.position = [cell.x, cell.y]
			rows.append(row)
		state[group] = rows
	state.objective = scene.objective.duplicate(true)
	var cell: Vector2i = state.objective.get("cell", Vector2i.ZERO)
	state.objective.cell = [cell.x, cell.y]
	var facings := {}
	for key in scene._unit_tokens:
		var token = scene._unit_tokens[key]
		if is_instance_valid(token) and "facing" in token: facings[key] = int(token.facing)
	return {"protocol_version": 2, "snapshot_version": 1,
		"session_id": session.get("session_id", ""), "mission_id": session.get("mission_id", ""),
		"handoff_fingerprint": session.get("handoff_fingerprint", ""), "state": state,
		"music_playback": scene._audio.playback_bookmark(), "token_facings": facings,
		"camera": {"viewport": [scene.size.x, scene.size.y], "visual_mode": scene.visual_mode, "top_down": scene._battlefield.top_down if scene.visual_mode else false, "position": [scene._camera.position.x, scene._camera.position.y], "zoom": scene._camera.zoom.x}}

static func _integer(value: Variant, minimum: int, maximum: int) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and float(value) == floor(float(value)) and value >= minimum and value <= maximum

static func _cell(value: Variant, cols: int, rows: int) -> bool:
	return value is Array and value.size() == 2 and _integer(value[0], 0, cols-1) and _integer(value[1], 0, rows-1)

static func validate(snapshot: Dictionary, scene: Node) -> String:
	var session: Dictionary = scene.handoff.get("session", {})
	if snapshot.get("protocol_version") != 2 or snapshot.get("snapshot_version") != 1: return "Unsupported tactical snapshot"
	for field in ["session_id", "mission_id", "handoff_fingerprint"]:
		if str(snapshot.get(field, "")).is_empty() or snapshot.get(field) != session.get(field): return "Snapshot identity mismatch: " + field
	var state: Variant = snapshot.get("state")
	if not state is Dictionary: return "Missing tactical state"
	for field in FIELDS:
		if not state.has(field): return "Missing tactical field: " + field
	if state.turn_side not in ["player", "enemy"] or not _integer(state.turn_number, 1, 100000): return "Invalid tactical turn"
	if not _integer(state.initial_enemy_count, 0, 10000) or not _integer(state.objective_progress, 0, 100000): return "Invalid tactical counters"
	if not state.pending_end_turn_confirmation is bool or not state.objective_completed is bool or not state.show_combat_log is bool: return "Invalid tactical flags"
	if not state.selected_action is String or not state.combat_log is Array or state.combat_log.size() > 10000: return "Invalid tactical presentation"
	for line in state.combat_log:
		if not line is String: return "Invalid combat log"
	if not (state.enemy_turn_timer is float or state.enemy_turn_timer is int) or not is_finite(float(state.enemy_turn_timer)) or state.enemy_turn_timer < 0 or state.enemy_turn_timer > 60: return "Invalid enemy timer"
	for group in GROUPS:
		var units: Variant = state.get(group)
		if not units is Array or units.size() > 1000: return "Invalid unit group"
		for row in units:
			if not row is Dictionary or not _cell(row.get("position"), scene.GRID_COLS, scene.GRID_ROWS): return "Invalid unit cell"
			if not _integer(row.get("max_hp"), 1, 1000000) or not _integer(row.get("hp"), 0, row.max_hp) or not _integer(row.get("ap"), 0, 100000): return "Invalid unit health or actions"
			if not row.get("status_effects", []) is Array: return "Invalid unit effects"
			for key in ["stress", "defense", "initiative", "aim", "melee_power", "damage_dealt", "damage_taken", "kills", "actions_used"]:
				if row.has(key) and not _integer(row[key], 0, 1000000): return "Invalid unit statistic"
			if row.has("size_scale") and (not (row.size_scale is int or row.size_scale is float) or not is_finite(float(row.size_scale)) or row.size_scale < 0.1 or row.size_scale > 50): return "Invalid unit scale"
			for key in ["name", "role", "kind"]:
				if row.has(key) and not row[key] is String: return "Invalid unit label"
			for key in ["status_effects", "available_actions"]:
				if not row.has(key): continue
				if not row[key] is Array: return "Invalid effects or actions"
				for value in row[key]:
					if not value is String: return "Invalid effects or actions"
	if state.initial_enemy_count > state.enemy_units.size(): return "Invalid encounter count"
	if state.player_units.size() != scene.player_units.size(): return "Deployment mismatch"
	for i in range(scene.player_units.size()):
		var expected: Dictionary = scene.player_units[i]
		var row: Dictionary = state.player_units[i]
		for key in ["name", "asset_id", "max_hp", "role", "kind"]:
			if row.get(key) != expected.get(key): return "Deployment identity mismatch"
	if not _integer(state.active_player_index, 0, maxi(0, state.player_units.size()-1)) or not _integer(state._queued_player_index, -1, state.player_units.size()-1) or not _integer(state.selected_target_index, -1, maxi(0,state.enemy_units.size()-1)): return "Invalid unit selection"
	for key in ["overwatch_indices", "defend_indices"]:
		if not state[key] is Array: return "Invalid posture list"
		for index in state[key]:
			if not _integer(index, 0, state.player_units.size()-1): return "Invalid posture index"
	if not state.get("objective") is Dictionary or not _cell(state.objective.get("cell"), scene.GRID_COLS, scene.GRID_ROWS): return "Invalid objective"
	var facings: Variant = snapshot.get("token_facings", {})
	if not facings is Dictionary: return "Invalid token facing table"
	var groups := {"p": "player_units", "e": "enemy_units", "v": "vehicle_units"}
	for key in facings:
		if not key is String or key.length() < 2 or not groups.has(key[0]) or not key.substr(1).is_valid_int(): return "Invalid token identity"
		if not _integer(int(key.substr(1)), 0, state[groups[key[0]]].size()-1) or not _integer(facings[key], 0, 7): return "Invalid token facing"
	var camera: Variant = snapshot.get("camera")
	if not camera is Dictionary or not camera.get("position") is Array or camera.position.size() != 2: return "Invalid camera"
	if camera.has("viewport"):
		if not camera.viewport is Array or camera.viewport.size() != 2 or not _integer(camera.viewport[0], 1, 16384) or not _integer(camera.viewport[1], 1, 16384): return "Invalid reference viewport"
	if not camera.get("top_down") is bool or not camera.get("visual_mode") is bool or camera.visual_mode != scene.visual_mode: return "Snapshot graphics mode mismatch"
	for value in camera.position + [camera.get("zoom")]:
		if not (value is int or value is float) or not is_finite(float(value)): return "Invalid camera coordinate"
	if camera.zoom < scene._ZOOM_MIN or camera.zoom > scene._ZOOM_MAX: return "Invalid camera zoom"
	return ""

static func restore(snapshot: Dictionary, scene: Node) -> void:
	# Caller validates the entire snapshot before changing any live tactical field.
	var state: Dictionary = snapshot.state
	if scene.visual_mode: scene._battlefield.top_down = bool(snapshot.camera.top_down)
	for field in FIELDS:
		if field in ["overwatch_indices", "defend_indices"]:
			var indices: Array[int] = []
			for value in state[field]: indices.append(int(value))
			scene.set(field, indices)
		elif field == "combat_log":
			var lines: Array[String] = []; lines.assign(state[field]); scene.set(field, lines)
		else: scene.set(field, state[field])
	for group in GROUPS:
		var units: Array[Dictionary] = []
		for entry: Dictionary in state[group]:
			var row := entry.duplicate(true)
			row.position = Vector2i(int(row.position[0]), int(row.position[1]))
			units.append(row)
		scene.set(group, units)
	scene.objective = state.objective.duplicate(true)
	scene.objective.cell = Vector2i(int(scene.objective.cell[0]), int(scene.objective.cell[1]))

static func restore_camera(snapshot: Dictionary, scene: Node) -> void:
	for key in snapshot.get("token_facings", {}):
		if scene._unit_tokens.has(key) and "facing" in scene._unit_tokens[key]:
			scene._unit_tokens[key].facing = int(snapshot.token_facings[key])
			scene._unit_tokens[key].queue_redraw()
	var camera: Dictionary = snapshot.camera
	if camera.has("viewport") and (float(camera.viewport[0]) != scene.size.x or float(camera.viewport[1]) != scene.size.y):
		return  # _frame_squad already framed the restored units for this new viewport.
	scene._camera.position = Vector2(float(camera.position[0]), float(camera.position[1]))
	scene._camera.zoom = Vector2.ONE * float(camera.zoom)
