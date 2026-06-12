extends Control
class_name MissionResults
## Victory / defeat screen shown after combat ends.
## Writes runtime/godot_combat/mission_result.json so Python can consume the
## outcome and apply XP, funds, casualties to GameState.

const NEON       := Color(0.10, 0.95, 0.72, 1.0)
const TEXT       := Color(0.84, 0.95, 0.92, 1.0)
const WARN       := Color(1.00, 0.72, 0.22, 1.0)
const ENEMY_COL  := Color(1.00, 0.34, 0.30, 1.0)
const PLAYER_COL := Color(0.10, 0.95, 0.72, 1.0)

var _outcome      : String = "victory"
var _result       : Dictionary = {}
var _elapsed      : float  = 0.0
var _shown        : bool   = false
var _extract_btn  : Button = null
var project_root  : String = ""

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_process(true)
	_build_extract_button()

func _process(delta: float) -> void:
	_elapsed += delta
	queue_redraw()

func show_results(outcome: String, result: Dictionary, p_root: String) -> void:
	_outcome     = outcome
	_result      = result
	_shown       = true
	project_root = p_root
	visible      = true
	_write_result_json()
	CombatSignals.audio_event.emit("victory" if outcome == "victory" else "defeat")

	# Fade in
	modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 1.0, 0.6)

func _build_extract_button() -> void:
	_extract_btn = Button.new()
	_extract_btn.text       = "EXTRACT"
	_extract_btn.size       = Vector2(200.0, 44.0)
	_extract_btn.focus_mode = Control.FOCUS_NONE
	var s := StyleBoxFlat.new()
	s.bg_color     = Color(0.04, 0.12, 0.16, 0.96)
	s.border_color = NEON
	s.set_border_width_all(2)
	for c in [0, 1, 2, 3]: s.set_corner_radius(c, 3)
	_extract_btn.add_theme_stylebox_override("normal",  s)
	var sh := StyleBoxFlat.new()
	sh.bg_color     = Color(0.10, 0.28, 0.36, 0.96)
	sh.border_color = WARN
	sh.set_border_width_all(2)
	for c in [0, 1, 2, 3]: sh.set_corner_radius(c, 3)
	_extract_btn.add_theme_stylebox_override("hover", sh)
	_extract_btn.add_theme_color_override("font_color",       TEXT)
	_extract_btn.add_theme_color_override("font_hover_color", WARN)
	_extract_btn.add_theme_font_size_override("font_size", 16)
	_extract_btn.pressed.connect(_on_extract)
	_extract_btn.visible = false
	add_child(_extract_btn)

func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED and _extract_btn != null:
		_extract_btn.position = Vector2((size.x - 200.0) * 0.5, size.y * 0.5 + 140.0)
		_extract_btn.visible  = _shown

func _on_extract() -> void:
	# Get the tree, then quit
	get_tree().quit()

# ── Result JSON ───────────────────────────────────────────────────────────────

func _write_result_json() -> void:
	var path_parts := ["runtime", "godot_combat", "mission_result.json"]
	var rel_path   := "/".join(path_parts)
	var full_path  := project_root.path_join(rel_path) if project_root != "" else rel_path

	# Ensure directory
	var dir_path := full_path.get_base_dir()
	DirAccess.make_dir_recursive_absolute(dir_path)

	var payload := {
		"schema_version": 1,
		"outcome":        _outcome,
		"turn_reached":   int(_result.get("turn_number", 1)),
		"casualties":     _result.get("casualties", []),
		"enemies_killed": int(_result.get("enemies_killed", 0)),
		"xp_per_agent":   _xp_for_outcome(),
		"funds_earned":   int(_result.get("fund_reward", 0)),
		"timestamp":      Time.get_unix_time_from_system(),
	}
	var f := FileAccess.open(full_path, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(payload, "  "))

func _xp_for_outcome() -> int:
	if _outcome == "victory": return 120
	if _outcome == "retreat": return 40
	return 20   # defeat

# ── Drawing ───────────────────────────────────────────────────────────────────

func _draw() -> void:
	if not _shown:
		return

	# Dim backdrop
	draw_rect(Rect2(Vector2.ZERO, size), Color(0, 0, 0, 0.88), true)

	var is_victory := _outcome == "victory"
	var title_col  := PLAYER_COL if is_victory else ENEMY_COL
	var title_text := "MISSION COMPLETE" if is_victory else "MISSION FAILED"

	# Panel
	var pw  := minf(640.0, size.x * 0.6)
	var ph  := 340.0
	var px  := (size.x - pw) * 0.5
	var py  := (size.y - ph) * 0.5 - 20.0
	draw_rect(Rect2(px, py, pw, ph), Color(0.02, 0.05, 0.08, 0.97), true)
	draw_rect(Rect2(px, py, pw, ph), title_col, false, 2.5)

	# Glowing title
	var pulse := 0.80 + 0.20 * sin(_elapsed * 2.5)
	draw_string(ThemeDB.fallback_font,
			Vector2(size.x * 0.5, py + 44.0),
			title_text, HORIZONTAL_ALIGNMENT_CENTER, int(pw), 22,
			Color(title_col.r, title_col.g, title_col.b, pulse))

	# Separator
	draw_line(Vector2(px + 16.0, py + 58.0), Vector2(px + pw - 16.0, py + 58.0), title_col, 1.0)

	# Stats
	var sy := py + 78.0
	var col2 := TEXT
	_draw_stat("OUTCOME",       _outcome.to_upper(),
			   Vector2(px + 20.0, sy), pw - 40.0, title_col, col2); sy += 26.0
	_draw_stat("TURNS",         str(_result.get("turn_number", 1)),
			   Vector2(px + 20.0, sy), pw - 40.0, TEXT, col2);      sy += 26.0
	_draw_stat("ENEMIES KILLED",str(_result.get("enemies_killed", 0)),
			   Vector2(px + 20.0, sy), pw - 40.0, TEXT, col2);      sy += 26.0
	_draw_stat("FUNDS EARNED",  "$%d" % int(_result.get("fund_reward", 0)),
			   Vector2(px + 20.0, sy), pw - 40.0, NEON, col2);      sy += 26.0
	_draw_stat("XP PER AGENT",  "+%d" % _xp_for_outcome(),
			   Vector2(px + 20.0, sy), pw - 40.0, NEON, col2);      sy += 26.0

	# Casualties
	var casualties : Array = _result.get("casualties", [])
	if not casualties.is_empty():
		draw_line(Vector2(px + 16.0, sy), Vector2(px + pw - 16.0, sy), ENEMY_COL, 1.0)
		sy += 14.0
		draw_string(ThemeDB.fallback_font,
				Vector2(px + 20.0, sy), "CASUALTIES:", HORIZONTAL_ALIGNMENT_LEFT, -1, 10, ENEMY_COL)
		sy += 18.0
		for c_name in casualties:
			draw_string(ThemeDB.fallback_font,
					Vector2(px + 32.0, sy), "✦ " + str(c_name),
					HORIZONTAL_ALIGNMENT_LEFT, -1, 10, WARN)
			sy += 16.0

func _draw_stat(label: String, value: String, pos: Vector2, width: float,
				label_col: Color, val_col: Color) -> void:
	draw_string(ThemeDB.fallback_font, pos, label,
			HORIZONTAL_ALIGNMENT_LEFT, -1, 11, label_col)
	draw_string(ThemeDB.fallback_font,
			Vector2(pos.x + width, pos.y), value,
			HORIZONTAL_ALIGNMENT_RIGHT, int(width), 11, val_col)
