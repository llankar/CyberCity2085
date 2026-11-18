extends Control
class_name MissionResults
## Victory / defeat screen shown after combat ends.
## Writes IPC signal to notify Python and result JSON so the campaign engine
## can apply XP, funds, casualties to GameState and continue the mission flow.

const NEON       := Color(0.10, 0.95, 0.72, 1.0)
const TEXT       := Color(0.84, 0.95, 0.92, 1.0)
const WARN       := Color(1.00, 0.72, 0.22, 1.0)
const ENEMY_COL  := Color(1.00, 0.34, 0.30, 1.0)
const PLAYER_COL := Color(0.10, 0.95, 0.72, 1.0)

var _outcome      : String = "victory"
var _result       : Dictionary = {}
var _elapsed      : float  = 0.0
var _shown        : bool   = false
var _confirmed := false
var _session: Dictionary={}
var _audio_node: Node=null
var _confirmation_elapsed:=0.0
var _extract_btn  : Button = null
var project_root  : String = ""
var ipc_pipe_path : String = ""  # Unix pipe path for IPC signal to Python

func _ready() -> void:
	set_anchors_preset(Control.PRESET_TOP_LEFT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_process(true)
	_build_extract_button()
	get_viewport().size_changed.connect(_fit_viewport)
	_fit_viewport()

func _process(delta: float) -> void:
	_elapsed += delta
	if _confirmed and not _session.is_empty():
		_confirmation_elapsed+=delta
		var ack: Variant=null
		if FileAccess.file_exists(str(_session.get("ack_path",""))):
			ack=JSON.parse_string(FileAccess.get_file_as_string(str(_session.ack_path)))
		if ack is Dictionary and ack.get("protocol_version")==2 and ack.get("session_id")==_session.get("session_id") and ack.get("status")=="accepted":
			get_tree().quit()
		elif _confirmation_elapsed>15.0:
			_extract_btn.text="RETRY RETURN"
			_extract_btn.disabled=false
	queue_redraw()

func _unhandled_key_input(event: InputEvent) -> void:
	if _shown and event is InputEventKey and event.pressed and not event.echo and event.keycode in [KEY_ENTER,KEY_KP_ENTER]:
		_on_extract()
		get_viewport().set_input_as_handled()

func show_results(outcome: String, result: Dictionary, p_root: String, ipc_pipe_path_str: String = "", audio: Node = null) -> void:
	_outcome     = outcome
	_result      = result.duplicate(true)
	_session = _result.get("session",{})
	_audio_node=audio
	_confirmed=false
	_shown       = true
	project_root = p_root
	ipc_pipe_path = ipc_pipe_path_str
	visible      = true
	_extract_btn.visible = true
	_position_extract()
	CombatSignals.audio_event.emit("victory" if outcome == "victory" else "defeat")
	if audio != null: _result["music_playback"] = audio.playback_bookmark()
	_publish(_prepared_path(),_payload("prepared"))
	preload("res://scripts/session_mailbox.gd").status(_session, "result_prepared")

	# Fade in
	modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 1.0, 0.6)
	
	# Preparation never publishes the final mailbox or the completion signal.

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
		_position_extract()
		_extract_btn.visible = _shown

func _fit_viewport() -> void:
	position=Vector2.ZERO
	size=get_viewport_rect().size
	if _extract_btn!=null:_position_extract()
	queue_redraw()

func _ui_scale() -> float:
	return clampf(size.y/720.0,.85,1.6)

func _panel_rect() -> Rect2:
	var scale_factor:=_ui_scale()
	var names: Array=_result.get("casualties",[])
	var width:=minf(640.0*scale_factor,size.x*.90)
	var height:=minf((360.0+min(names.size(),6)*20.0)*scale_factor,size.y-40.0)
	return Rect2((size-Vector2(width,height))*.5,Vector2(width,height))

func _position_extract() -> void:
	var panel:=_panel_rect()
	_extract_btn.size=Vector2(240,48)*_ui_scale()
	_extract_btn.position=Vector2((size.x-_extract_btn.size.x)*.5,panel.end.y-64*_ui_scale())
	_extract_btn.add_theme_font_size_override("font_size",roundi(18*_ui_scale()))

func _signal_completion_to_python() -> void:
	if ipc_pipe_path.is_empty():
		return
	var f := FileAccess.open(ipc_pipe_path, FileAccess.WRITE)
	if f != null:
		f.store_string("COMBAT_COMPLETE\n")
		f.close()

func _on_extract() -> void:
	if not _shown or (_confirmed and _extract_btn.disabled):return
	if _audio_node!=null:_result["music_playback"]=_audio_node.playback_bookmark()
	if not _publish(_result_path(),_payload("confirmed")):
		_extract_btn.text="RETURN FAILED — RETRY"
		return
	preload("res://scripts/session_mailbox.gd").status(_session, "result_confirmed")
	_confirmed=true
	_confirmation_elapsed=0.0
	_extract_btn.text="RETURNING…"
	_extract_btn.disabled=true
	if not ipc_pipe_path.is_empty():
		_publish(ipc_pipe_path.get_base_dir().path_join("ipc_result.json"),_payload("confirmed"))
		_signal_completion_to_python()
	if _session.is_empty():get_tree().quit()

func _result_path() -> String:
	return str(_session.get("result_path",project_root.path_join("runtime/godot_combat/mission_result.json")))

func _prepared_path() -> String:
	return str(_session.get("prepared_path",_result_path()+".prepared"))

func _payload(phase: String) -> Dictionary:
	return {"protocol_version":2,"session_id":_session.get("session_id",""),"mission_id":_session.get("mission_id",""),
		"phase":phase,"outcome":_outcome,"turn_reached":int(_result.get("turn_number",1)),
		"initial_enemy_count":int(_result.get("initial_enemy_count",0)),"enemies_spawned_total":int(_result.get("enemies_spawned_total",_result.get("initial_enemy_count",0))),"enemies_killed":int(_result.get("enemies_killed",0)),
		"agents":_result.get("agents",[]),"support":_result.get("support",[]),
		"objective_completed":_result.get("objective_completed",false),"objective_progress":_result.get("objective_progress",0),
		"music_playback":_result.get("music_playback",{})}

func _publish(path: String,payload: Dictionary) -> bool:
	return preload("res://scripts/session_mailbox.gd").publish(path, payload)

# ── Drawing ───────────────────────────────────────────────────────────────────

func _draw() -> void:
	if not _shown:
		return

	# Dim backdrop
	draw_rect(Rect2(Vector2.ZERO, size), Color(0, 0, 0, 0.88), true)

	var is_victory := _outcome == "victory"
	var title_col  := PLAYER_COL if is_victory else ENEMY_COL
	var title_text := "MISSION COMPLETE" if is_victory else ("TACTICAL RETREAT" if _outcome=="retreat" else "MISSION FAILED")

	# Panel
	var panel:=_panel_rect()
	var scale_factor:=_ui_scale()
	var pw:=panel.size.x
	var ph:=panel.size.y
	var px:=panel.position.x
	var py:=panel.position.y
	draw_rect(Rect2(px, py, pw, ph), Color(0.02, 0.05, 0.08, 0.97), true)
	draw_rect(Rect2(px, py, pw, ph), title_col, false, 2.5)

	# Glowing title
	var pulse := 0.80 + 0.20 * sin(_elapsed * 2.5)
	draw_string(ThemeDB.fallback_font,
			Vector2(px, py + 44.0*scale_factor),
			title_text, HORIZONTAL_ALIGNMENT_CENTER, int(pw), roundi(24*scale_factor),
			Color(title_col.r, title_col.g, title_col.b, pulse))

	# Separator
	draw_line(Vector2(px + 16.0, py + 58.0*scale_factor), Vector2(px + pw - 16.0, py + 58.0*scale_factor), title_col, 1.0)

	# Stats
	var sy := py + 86.0*scale_factor
	var col2 := TEXT
	_draw_stat("OUTCOME",       _outcome.to_upper(),
			   Vector2(px + 20.0, sy), pw - 40.0, title_col, col2); sy += 28.0*scale_factor
	_draw_stat("TURNS",         str(_result.get("turn_number", 1)),
			   Vector2(px + 20.0, sy), pw - 40.0, TEXT, col2);      sy += 28.0*scale_factor
	_draw_stat("ENEMIES KILLED",str(_result.get("enemies_killed", 0)),
			   Vector2(px + 20.0, sy), pw - 40.0, TEXT, col2);      sy += 28.0*scale_factor
	_draw_stat("FUNDS EARNED",  "CAMPAIGN RESOLUTION",
			   Vector2(px + 20.0, sy), pw - 40.0, NEON, col2);      sy += 28.0*scale_factor
	_draw_stat("XP PER AGENT",  "CAMPAIGN RESOLUTION",
			   Vector2(px + 20.0, sy), pw - 40.0, NEON, col2);      sy += 28.0*scale_factor

	# Casualties
	var casualties : Array = _result.get("casualties", [])
	if not casualties.is_empty():
		draw_line(Vector2(px + 16.0, sy), Vector2(px + pw - 16.0, sy), ENEMY_COL, 1.0)
		sy += 14.0*scale_factor
		draw_string(ThemeDB.fallback_font,
				Vector2(px + 20.0, sy), "DOWNED / AWAITING CAMPAIGN OUTCOME:", HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(14*scale_factor), ENEMY_COL)
		sy += 18.0*scale_factor
		for c_name in casualties.slice(0,6):
			draw_string(ThemeDB.fallback_font,
					Vector2(px + 32.0, sy), "✦ " + str(c_name),
					HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(14*scale_factor), WARN)
			sy += 16.0

func _draw_stat(label: String, value: String, pos: Vector2, width: float,
				label_col: Color, val_col: Color) -> void:
	draw_string(ThemeDB.fallback_font, pos, label,
			HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(16*_ui_scale()), label_col)
	draw_string(ThemeDB.fallback_font,
			Vector2(pos.x, pos.y), value,
			HORIZONTAL_ALIGNMENT_RIGHT, int(width), roundi(16*_ui_scale()), val_col)
