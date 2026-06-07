extends Node2D

const CELL_SIZE := 72
const ORIGIN := Vector2(96, 96)
const TEAM_COLORS := {"agent": Color.CYAN, "enemy": Color.INDIAN_RED}

var mission_state: SpikeMissionState = SpikeMissionState.default_state()
var selected_unit_id := "agent_echo"

func _ready() -> void:
	print(mission_state.to_json_text())

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("end_turn"):
		SpikeCombatRules.end_turn(mission_state)
		queue_redraw()
	elif event.is_action_pressed("export_state"):
		print(mission_state.to_json_text())
	elif event is InputEventKey and event.pressed:
		_handle_key(event.keycode)

func _handle_key(keycode: int) -> void:
	var moved := false
	if keycode == KEY_UP:
		moved = SpikeCombatRules.move_unit(mission_state, selected_unit_id, 0, -1)
	elif keycode == KEY_DOWN:
		moved = SpikeCombatRules.move_unit(mission_state, selected_unit_id, 0, 1)
	elif keycode == KEY_LEFT:
		moved = SpikeCombatRules.move_unit(mission_state, selected_unit_id, -1, 0)
	elif keycode == KEY_RIGHT:
		moved = SpikeCombatRules.move_unit(mission_state, selected_unit_id, 1, 0)
	elif keycode == KEY_SPACE:
		SpikeCombatRules.attack_unit(mission_state, selected_unit_id, _nearest_enemy_id())
	elif keycode == KEY_TAB:
		_cycle_agent()
	if moved or keycode in [KEY_SPACE, KEY_TAB]:
		queue_redraw()

func _draw() -> void:
	_draw_grid()
	_draw_units()
	draw_string(ThemeDB.fallback_font, Vector2(32, 36), "Godot combat spike — isolated from Arcade runtime", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
	draw_string(ThemeDB.fallback_font, Vector2(32, 60), "Arrows move | Space attack | Tab switch agent | T end turn | J export JSON", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.LIGHT_GRAY)
	draw_string(ThemeDB.fallback_font, Vector2(32, 600), "Mission %s | Turn %d %s | Result %s" % [mission_state.mission_id, mission_state.turn_number, mission_state.turn, mission_state.result], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)

func _draw_grid() -> void:
	for x in range(SpikeMissionState.GRID_WIDTH):
		for y in range(SpikeMissionState.GRID_HEIGHT):
			var rect := Rect2(ORIGIN + Vector2(x, y) * CELL_SIZE, Vector2(CELL_SIZE, CELL_SIZE))
			draw_rect(rect, Color(0.05, 0.08, 0.11), true)
			draw_rect(rect, Color(0.18, 0.55, 0.68), false, 1.0)

func _draw_units() -> void:
	for unit in mission_state.units:
		if int(unit.get("hp", 0)) <= 0:
			continue
		var pos: Dictionary = unit.get("position", {})
		var center := ORIGIN + Vector2(int(pos.get("x", 0)), int(pos.get("y", 0))) * CELL_SIZE + Vector2(CELL_SIZE / 2, CELL_SIZE / 2)
		var color: Color = TEAM_COLORS.get(unit.get("team", ""), Color.GRAY)
		draw_circle(center, 24, color)
		if unit.get("id") == selected_unit_id:
			draw_circle(center, 30, Color.GOLD, false, 3.0)
		draw_string(ThemeDB.fallback_font, center + Vector2(-28, 44), "%s HP:%d AP:%d" % [unit.get("id", "unit"), int(unit.get("hp", 0)), int(unit.get("ap", 0))], HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color.WHITE)

func _nearest_enemy_id() -> String:
	for unit in mission_state.living_units("enemy"):
		return str(unit.get("id", ""))
	return ""

func _cycle_agent() -> void:
	var agents := mission_state.living_units("agent")
	if agents.is_empty():
		return
	var index := 0
	for i in range(agents.size()):
		if agents[i].get("id") == selected_unit_id:
			index = i + 1
	selected_unit_id = str(agents[index % agents.size()].get("id"))
