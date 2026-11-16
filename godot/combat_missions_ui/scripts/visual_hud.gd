extends "res://scripts/hud_controller.gd"
## Visual presentation only. Actions still use the original signal/mechanics.
signal quality_changed(level: int)
var mission_title := "TACTICAL INSERTION"
var objective_text := ""
var target_info: Dictionary = {}
var settings_open := false
var quality := 2
var _portrait_rects: Array[Rect2] = []
var _log_button: Button
var _settings_button: Button
var _command_rows := 1
var _quality_button: Button

func _ready() -> void:
	super._ready()
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_log_button = _utility("JOURNAL [L]", func():
		show_log = not show_log
		get_parent().get_parent().show_combat_log = show_log
		queue_redraw())
	_settings_button = _utility("RÉGLAGES", func():
		settings_open = not settings_open
		_quality_button.visible = settings_open
		queue_redraw())
	_quality_button = _utility("QUALITÉ : ÉLEVÉE", func():
		quality = (quality + 1) % 3
		_quality_button.text = "QUALITÉ : " + ["BASSE", "MOYENNE", "ÉLEVÉE"][quality]
		quality_changed.emit(quality))
	_quality_button.visible = false
	_reposition_buttons()

func _utility(label: String, callback: Callable) -> Button:
	var btn := Button.new()
	btn.text = label
	btn.pressed.connect(callback)
	btn.focus_mode = Control.FOCUS_NONE
	_style_btn(btn, false, false)
	add_child(btn)
	return btn

func _process(delta: float) -> void:
	_elapsed += delta
	# HUD redraws only on state changes; no per-frame portrait uploads.

func _reposition_buttons() -> void:
	if size.x < 1: return
	var actions: Array[String] = []
	for action: String in _visible_actions:
		if action not in _SYSTEM_ACTIONS: actions.append(action)
	var left := 16.0
	var available := maxf(300.0, size.x - 235.0)
	var columns := maxi(1, mini(mini(7, actions.size()),int(available / 126.0)))
	_command_rows = maxi(1, int(ceil(float(actions.size())/float(columns))))
	var width := minf(145.0, (available - float(columns - 1) * 6.0) / float(columns))
	for i in range(actions.size()):
		var btn := _action_btns[actions[i]] as Button
		btn.position = Vector2(left + float(i % columns) * (width + 6.0), size.y - 68.0 - float(i / columns) * 60.0)
		btn.size = Vector2(width, 54)
		var labels := {"Move":"BOUGER", "Defend":"COUVERT", "Rifle Burst":"RAFALE", "Pistol Shot":"PISTOLET", "Overwatch":"VIGILANCE", "Psi Focus":"PSI", "Trauma Patch":"SOIGNER", "Katana Slash":"KATANA", "Missile Salvo":"MISSILES"}
		btn.text = str(labels.get(actions[i],actions[i].to_upper()))
		btn.tooltip_text = actions[i]
	for action: String in _SYSTEM_ACTIONS:
		if not _action_btns.has(action): continue
		var btn := _action_btns[action] as Button
		btn.position = Vector2(size.x - 211.0, size.y - (68.0 if action == "END TURN" else 123.0))
		btn.size = Vector2(195, 48)
		btn.text = "FIN DU TOUR  »" if action == "END TURN" else "AGENT SUIVANT [TAB]"
	if is_instance_valid(_log_button):
		_log_button.position = Vector2(size.x - 240, 16)
		_log_button.size = Vector2(118, 34)
		_settings_button.position = Vector2(size.x - 116, 16)
		_settings_button.size = Vector2(100, 34)
		_quality_button.position = Vector2(size.x - 266, 92)
		_quality_button.size = Vector2(236, 38)

func _style_btn(btn: Button, active: bool, disabled: bool) -> void:
	super._style_btn(btn, active, disabled)
	for state: String in ["normal", "hover", "pressed", "disabled", "focus"]:
		var box := btn.get_theme_stylebox(state).duplicate() as StyleBoxFlat
		box.bg_color = Color(0.045, 0.065, 0.07, 0.95) if not active else Color(0.20, 0.14, 0.035, 0.96)
		box.border_color = WARN if active or btn.text.begins_with("FIN") else Color(0.12, 0.65, 0.68, 0.7)
		box.set_border_width_all(1)
		box.set_corner_radius_all(7)
		box.shadow_color = Color(0, 0, 0, 0.5)
		box.shadow_size = 5
		btn.add_theme_stylebox_override(state, box)
	btn.add_theme_font_size_override("font_size", 13)

func _draw() -> void:
	_panel(Rect2(16, 16, minf(385, size.x * 0.35), 102), NEON)
	_ds("CYBERCITY 2085", Vector2(32, 44), 23, TEXT)
	_ds(mission_title.to_upper().left(38), Vector2(32, 69), 13, NEON)
	_ds(objective_text.left(48), Vector2(32, 96), 12, WARN)
	var phase_x := size.x * 0.5 - 138.0 if size.x >= 1100 else 16.0
	var phase_y := 16.0 if size.x >= 1100 else 132.0
	_panel(Rect2(phase_x, phase_y, 276, 36), NEON if turn_side == "player" else ENEMY_COL)
	_ds("TOUR %02d  //  %s" % [turn_number, "PHASE JOUEUR" if turn_side == "player" else "PHASE ENNEMIE"], Vector2(phase_x + 14, phase_y + 24), 15, TEXT)
	_draw_roster()
	_draw_target()
	if not status_line.is_empty():
		_ds(status_line.left(100), Vector2(18, size.y - 210 - float(_command_rows-1)*60.0), 12, NEON)
	if show_log: _draw_combat_log()
	if settings_open:
		_panel(Rect2(size.x - 280, 64, 264, 100), NEON)
		_ds("RENDU // F9 : INTERFACE CLASSIQUE", Vector2(size.x - 266, 85), 11, TEXT)
		_ds("F8 : relevés de murs", Vector2(size.x - 266, 151), 11, TEXT)

func _panel(rect: Rect2, color: Color) -> void:
	var cut := 8.0
	var p := PackedVector2Array([rect.position + Vector2(cut, 0), Vector2(rect.end.x, rect.position.y), rect.end - Vector2(0, cut), rect.end - Vector2(cut, 0), Vector2(rect.position.x, rect.end.y), rect.position + Vector2(0, cut)])
	draw_colored_polygon(p, Color(0.015, 0.035, 0.043, 0.94))
	p.append(p[0])
	draw_polyline(p, Color(color, 0.7), 1.2, true)
	draw_line(rect.position + Vector2(10, 0), rect.position + Vector2(minf(90, rect.size.x - 10), 0), color, 2, true)

func _draw_roster() -> void:
	_portrait_rects.clear()
	var y := size.y - 194.0 - float(_command_rows-1)*60.0
	var x := 16.0
	var max_width := size.x - 245.0
	var compact := clampf((max_width - 260) / float(maxi(1, player_units.size() - 1)), 40, 88)
	for i in range(player_units.size()):
		var u := player_units[i]
		var active := i == active_player_idx
		var w := 252.0 if active else compact
		if x + w > max_width + 16: break
		var r := Rect2(x, y, w, 112)
		_portrait_rects.append(r)
		_panel(r, WARN if active else NEON)
		var tex := portrait_textures.get(str(u.get("name", "")), null) as Texture2D
		var pr := Rect2(x + 5, y + 5, minf(83, w - 10), 80)
		if tex != null:
			_portrait(tex, pr)
		var tx := x + 97 if active else x + 6
		_ds(str(u.get("name", "AGENT")).to_upper().left(16 if active else 9), Vector2(tx, y + 23 if active else y + 99), 15 if active else 10, TEXT)
		if active:
			_ds("PV  %d / %d" % [u.get("hp", 0), u.get("max_hp", 1)], Vector2(tx, y + 47), 13, TEXT)
			_bar(Rect2(tx, y + 53, 138, 5), float(u.get("hp", 0)) / maxf(1, float(u.get("max_hp", 1))), NEON)
			_ds("PA  %d    STRESS  %d %%" % [u.get("ap", 0), u.get("stress", 0)], Vector2(tx, y + 79), 11, TEXT)
			_bar(Rect2(tx, y + 88, 138, 3), float(u.get("stress", 0)) / 100, WARN)
		else:
			_bar(Rect2(x + 6, y + 104, w - 12, 3), float(u.get("hp", 0)) / maxf(1, float(u.get("max_hp", 1))), NEON)
		if int(u.get("hp", 0)) <= 0:
			draw_rect(r, Color(0, 0, 0, 0.75))
			_ds("K.I.A.", Vector2(x + 8, y + 65), 14, ENEMY_COL)
		x += w + 7

func _portrait(tex: Texture2D, rect: Rect2) -> void:
	var sz := tex.get_size()
	var edge := minf(sz.x, sz.y)
	draw_texture_rect_region(tex, rect, Rect2((sz.x-edge)*0.5, 0, edge, edge))

func _bar(rect: Rect2, fraction: float, color: Color) -> void:
	draw_rect(rect, Color(0.08, 0.15, 0.18))
	draw_rect(Rect2(rect.position, Vector2(rect.size.x * clampf(fraction, 0, 1), rect.size.y)), color)

func _draw_target() -> void:
	if target_info.is_empty(): return
	var x := size.x - 310.0
	_panel(Rect2(x, 170, 294, 132), ENEMY_COL)
	var portrait := target_info.get("portrait",null) as Texture2D
	if portrait != null: _portrait(portrait,Rect2(x+12,182,62,62))
	_ds(str(target_info.get("name", "CONTACT")).left(18), Vector2(x+84, 199), 16, TEXT)
	_ds("PV  %d / %d" % [target_info.get("hp", 0), target_info.get("max_hp", 1)], Vector2(x+84, 224), 15, TEXT)
	_bar(Rect2(x+84, 232, 194, 5), float(target_info.get("hp", 0)) / maxf(1, float(target_info.get("max_hp", 1))), ENEMY_COL)
	_ds(str(target_info.get("detail", "")), Vector2(x+16, 261), 12, TEXT)
	_ds(str(target_info.get("chance_label", "")), Vector2(x+16, 286), 18, WARN)

func _draw_combat_log() -> void:
	var r := Rect2(16, 134, minf(520, size.x - 32), minf(210, size.y - 350))
	_panel(r, NEON)
	_ds("JOURNAL DE COMBAT", r.position + Vector2(14, 24), 13, NEON)
	var count := mini(combat_log.size(), 8)
	for i in range(count):
		_ds(combat_log[combat_log.size()-count+i].left(76), r.position + Vector2(14, 47+i*19), 11, TEXT)

func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		for i in range(_portrait_rects.size()):
			if _portrait_rects[i].has_point(event.position):
				if not event.pressed: CombatSignals.unit_clicked.emit(i, false)
				get_viewport().set_input_as_handled()
				return

func _ensure_action_buttons(actions: Array[String]) -> void:
	super._ensure_action_buttons(actions)
	for action: String in actions:
		var btn := _action_btns[action] as Button
		if btn.icon != null or action in _SYSTEM_ACTIONS: continue
		var key := "fire"
		var name_lower := action.to_lower()
		if "move" in name_lower: key = "move"
		elif "defend" in name_lower: key = "defend"
		elif "psi" in name_lower: key = "psi"
		elif "slash" in name_lower or "blade" in name_lower or "punch" in name_lower: key = "melee"
		elif "patch" in name_lower: key = "heal"
		elif "overwatch" in name_lower: key = "watch"
		elif "missile" in name_lower: key = "missile"
		btn.icon = load("res://icons/%s.svg" % key)

func _update_button_styles() -> void:
	for action: String in _action_btns:
		var btn := _action_btns[action] as Button
		if btn.visible:
			_style_btn(btn, action.to_upper() == selected_action.to_upper() and action not in _SYSTEM_ACTIONS, turn_side != "player")
