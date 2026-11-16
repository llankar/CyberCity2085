extends "res://scripts/hud_controller.gd"
## Visual presentation only. Actions still use the original signal/mechanics.
signal quality_changed(level: int)
var mission_title := "TACTICAL INSERTION"
var objective_text := ""
var target_info: Dictionary = {}
var settings_open := false
var quality := 2
var _portrait_rects: Array[Rect2] = []
var _portrait_press_index := -1
var _log_button: Button
var _settings_button: Button
var _command_rows := 1
var _roster_y := 0.0
var _roster_w := 0.0
var _compact_w := 82.0
var _stacked := false
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
	_set_utility_icon(_log_button,"journal","Journal de combat [L]")
	_set_utility_icon(_settings_button,"settings","Réglages graphiques")
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

func fit_viewport(viewport: Vector2) -> void:
	# Keep the same physical reading size on high-resolution / Windows HiDPI windows.
	set_anchors_preset(Control.PRESET_TOP_LEFT)
	var factor := clampf(viewport.y / 1080.0, 0.85, 2.5)
	scale = Vector2.ONE * factor
	size = viewport / factor
	position = Vector2.ZERO
	_reposition_buttons()
	queue_redraw()

func _reposition_buttons() -> void:
	if size.x < 1: return
	var actions: Array[String] = []
	for action: String in _visible_actions:
		if action not in _SYSTEM_ACTIONS: actions.append(action)
	_compact_w = clampf((size.x * 0.44 - 280.0) / float(maxi(1,player_units.size()-1)),64.0,88.0)
	_roster_w = 280.0 + float(maxi(0,player_units.size()-1))*(_compact_w+7.0)
	_stacked = size.x < _roster_w + float(actions.size())*100.0 + 248.0
	_roster_y = size.y - (242.0 if _stacked else 142.0)
	var left := 16.0 if _stacked else _roster_w+38.0
	var available := maxf(300.0,size.x-left-238.0)
	var columns := maxi(1,mini(actions.size(),int(available/100.0)))
	_command_rows = maxi(1,int(ceil(float(actions.size())/float(columns))))
	var width := minf(128.0,(available-float(columns-1)*7.0)/float(columns))
	if _stacked: _roster_y -= float(_command_rows-1)*104.0
	var labels := {"Move":"BOUGER","Defend":"COUVERT","Rifle Burst":"TIR RAFALE","Pistol Shot":"PISTOLET","Plasma Burst":"PLASMA","Overwatch":"VIGILANCE","Psi Focus":"PSI","Trauma Patch":"SOIGNER","Katana Slash":"KATANA","Blade Strike":"LAME","Servo Punch":"FRAPPE","Missile Salvo":"MISSILES"}
	for i in range(actions.size()):
		var btn := _action_btns[actions[i]] as Button
		btn.position = Vector2(left+float(i%columns)*(width+7.0),size.y-116.0-float(i/columns)*104.0)
		btn.size = Vector2(width,98)
		btn.text = ""
		btn.tooltip_text = actions[i]
		if btn.has_node("Glyph"):
			var glyph := btn.get_node("Glyph") as TextureRect
			glyph.position = Vector2((width-38.0)*0.5,10)
			glyph.size = Vector2(38,38)
			var caption := btn.get_node("Caption") as Label
			caption.text = str(labels.get(actions[i],actions[i].to_upper()))
			caption.position = Vector2(3,58)
			caption.size = Vector2(width-6,30)
	for action: String in _SYSTEM_ACTIONS:
		if not _action_btns.has(action): continue
		var btn := _action_btns[action] as Button
		btn.position = Vector2(size.x-224.0,size.y-(82.0 if action == "END TURN" else 132.0))
		btn.size = Vector2(208,62 if action == "END TURN" else 42)
		btn.text = "FIN DU TOUR  »" if action == "END TURN" else "SUIVANT [TAB]"
		btn.add_theme_font_size_override("font_size",22 if action == "END TURN" else 16)
	if is_instance_valid(_log_button):
		_log_button.position = Vector2(size.x-126,16)
		_log_button.size = Vector2(48,48)
		_settings_button.position = Vector2(size.x-66,16)
		_settings_button.size = Vector2(48,48)
		_quality_button.position = Vector2(size.x-330,112)
		_quality_button.size = Vector2(296,42)

func _style_btn(btn: Button, active: bool, disabled: bool) -> void:
	super._style_btn(btn, active, disabled)
	for state: String in ["normal", "hover", "pressed", "disabled", "focus"]:
		var box := btn.get_theme_stylebox(state).duplicate() as StyleBoxFlat
		box.bg_color = Color(0.045, 0.065, 0.07, 0.95) if not (active or btn.text.begins_with("FIN")) else Color(0.20, 0.14, 0.035, 0.96)
		box.border_color = WARN if active or btn.text.begins_with("FIN") else Color(0.12, 0.65, 0.68, 0.7)
		box.set_border_width_all(1)
		box.set_corner_radius_all(7)
		box.shadow_color = Color(0, 0, 0, 0.5)
		box.shadow_size = 5
		btn.add_theme_stylebox_override(state, box)
	btn.add_theme_font_size_override("font_size", 22 if btn.text.begins_with("FIN") else 20)
	if btn.text.begins_with("FIN"): btn.add_theme_color_override("font_color",WARN)

func _draw() -> void:
	var header_w := minf(465,size.x*0.36)
	_panel(Rect2(16,16,header_w,112),NEON)
	# Skyline mark echoes the reference without taking space from the mission.
	for i in range(5):
		var h: int = [16,31,43,25,12][i]
		draw_rect(Rect2(30+i*6,64-h,4,h),NEON)
	_ds("CYBERCITY 2085",Vector2(72,50),29,TEXT)
	_ds(_fit(mission_title.to_upper(),header_w-32,20),Vector2(32,82),20,NEON)
	_ds(_fit(objective_text,header_w-32,18),Vector2(32,112),18,WARN)
	var phase_y := 16.0 if size.x >= 1400 else 142.0
	var phase_x := size.x*0.5-197.0 if size.x >= 1400 else 16.0
	_panel(Rect2(phase_x,phase_y,394,46),NEON if turn_side == "player" else ENEMY_COL)
	_ds("TOUR %02d  //  %s" % [turn_number,"PHASE JOUEUR" if turn_side == "player" else "PHASE ENNEMIE"],Vector2(phase_x+15,phase_y+31),22,TEXT)
	_draw_roster()
	_draw_target()
	if not status_line.is_empty():
		_ds(_fit(status_line,size.x-50,17),Vector2(18,_roster_y-12),17,NEON)
	if show_log: _draw_combat_log()
	if settings_open:
		_panel(Rect2(size.x-346,80,330,128),NEON)
		_ds("QUALITÉ GRAPHIQUE",Vector2(size.x-330,104),19,TEXT)
		_ds("F9 : interface classique",Vector2(size.x-330,184),17,TEXT)

func _fit(value: String, width: float, font_size: int) -> String:
	var result := value
	while not result.is_empty() and ThemeDB.fallback_font.get_string_size(result,HORIZONTAL_ALIGNMENT_LEFT,-1,font_size).x > width:
		result = result.left(result.length()-1)
	return result + ("…" if result.length() < value.length() else "")

func _panel(rect: Rect2, color: Color) -> void:
	var cut := 8.0
	var p := PackedVector2Array([rect.position + Vector2(cut, 0), Vector2(rect.end.x, rect.position.y), rect.end - Vector2(0, cut), rect.end - Vector2(cut, 0), Vector2(rect.position.x, rect.end.y), rect.position + Vector2(0, cut)])
	draw_colored_polygon(p, Color(0.015, 0.035, 0.043, 0.94))
	p.append(p[0])
	draw_polyline(p, Color(color, 0.7), 1.2, true)
	draw_line(rect.position + Vector2(10, 0), rect.position + Vector2(minf(90, rect.size.x - 10), 0), color, 2, true)

func _draw_roster() -> void:
	_portrait_rects.clear()
	var x := 16.0
	var y := _roster_y
	for i in range(player_units.size()):
		var u := player_units[i]
		var active := i == active_player_idx
		var w := 280.0 if active else _compact_w
		var rect := Rect2(x,y,w,126)
		_portrait_rects.append(rect)
		_panel(rect,NEON if active else Color(0.1,0.7,0.74))
		var tex := portrait_textures.get(str(u.get("name","")),null) as Texture2D
		if tex != null: _portrait(tex,Rect2(x+5,y+5,92 if active else w-10,116 if active else 80))
		var tx := x+108 if active else x+5
		_ds(_fit(str(u.get("name","AGENT")).to_upper(),w-116 if active else w-10,22 if active else 16),Vector2(tx,y+25 if active else y+105),22 if active else 16,TEXT)
		var hp_fraction := float(u.get("hp",0))/maxf(1,float(u.get("max_hp",1)))
		if active:
			_ds("PV  %d / %d" % [u.get("hp",0),u.get("max_hp",1)],Vector2(tx,y+52),19,TEXT)
			_bar(Rect2(tx,y+60,158,6),hp_fraction,NEON)
			_ds("PA  %d" % u.get("ap",0),Vector2(tx,y+87),19,NEON)
			_ds("STRESS  %d %%" % u.get("stress",0),Vector2(tx,y+113),17,TEXT)
		else:
			_bar(Rect2(x+5,y+112,w-10,5),hp_fraction,NEON)
			var ap := mini(6,int(u.get("ap",0)))
			for n in range(ap): draw_rect(Rect2(x+5+n*11,y+119,8,3),NEON)
		if int(u.get("hp",0)) <= 0:
			draw_rect(rect,Color(0,0,0,0.75))
			_ds("K.I.A.",Vector2(x+8,y+65),20,ENEMY_COL)
		x += w+7.0

func _portrait(tex: Texture2D, rect: Rect2) -> void:
	var image_size := tex.get_size()
	var crop := image_size
	var aspect := rect.size.x/rect.size.y
	if image_size.x/image_size.y > aspect: crop.x = image_size.y*aspect
	else: crop.y = image_size.x/aspect
	draw_texture_rect_region(tex,rect,Rect2(Vector2((image_size.x-crop.x)*0.5,0),crop))

func _bar(rect: Rect2, fraction: float, color: Color) -> void:
	draw_rect(rect, Color(0.08, 0.15, 0.18))
	draw_rect(Rect2(rect.position, Vector2(rect.size.x * clampf(fraction, 0, 1), rect.size.y)), color)

func _draw_target() -> void:
	if target_info.is_empty(): return
	var x := size.x-380.0
	_panel(Rect2(x,182,364,170),ENEMY_COL)
	var portrait := target_info.get("portrait",null) as Texture2D
	if portrait != null: _portrait(portrait,Rect2(x+12,194,74,80))
	_ds(_fit(str(target_info.get("name","CONTACT")),254,23),Vector2(x+98,218),23,TEXT)
	_ds("PV  %d / %d" % [target_info.get("hp",0),target_info.get("max_hp",1)],Vector2(x+98,246),20,TEXT)
	_bar(Rect2(x+98,257,250,6),float(target_info.get("hp",0))/maxf(1,float(target_info.get("max_hp",1))),ENEMY_COL)
	_ds(_fit(str(target_info.get("detail","")),332,17),Vector2(x+16,299),17,TEXT)
	_ds(_fit(str(target_info.get("chance_label","")),332,24),Vector2(x+16,334),24,WARN)

func _draw_combat_log() -> void:
	var rect := Rect2(16,204,minf(690,size.x-32),minf(280,_roster_y-230))
	_panel(rect,NEON)
	_ds("JOURNAL DE COMBAT",rect.position+Vector2(14,30),20,NEON)
	var count := mini(combat_log.size(),7)
	for i in range(count):
		_ds(_fit(combat_log[combat_log.size()-count+i],rect.size.x-28,17),rect.position+Vector2(14,59+i*28),17,TEXT)

func _input(event: InputEvent) -> void:
	if event is not InputEventMouseButton or event.button_index != MOUSE_BUTTON_LEFT: return
	if not event.pressed and _portrait_press_index >= 0:
		_portrait_press_index = -1
		get_viewport().set_input_as_handled()
		return
	var local: Vector2 = get_global_transform_with_canvas().affine_inverse()*event.position
	for i in range(_portrait_rects.size()):
		if _portrait_rects[i].has_point(local):
			if event.pressed:
				_portrait_press_index = i
				CombatSignals.unit_clicked.emit(i,false)
			get_viewport().set_input_as_handled()
			return

func blocks_map_input(point: Vector2) -> bool:
	var local: Vector2 = get_global_transform_with_canvas().affine_inverse()*point
	for rect: Rect2 in _portrait_rects:
		if rect.has_point(local): return true
	for child: Node in get_children():
		if child is Button and child.visible:
			var button := child as Button
			var button_point := button.get_global_transform_with_canvas().affine_inverse()*point
			if Rect2(Vector2.ZERO,button.size).has_point(button_point): return true
	return false

func _ensure_action_buttons(actions: Array[String]) -> void:
	super._ensure_action_buttons(actions)
	for action: String in actions:
		var btn := _action_btns[action] as Button
		if btn.has_node("Glyph") or action in _SYSTEM_ACTIONS: continue
		var key := "fire"
		var name_lower := action.to_lower()
		if "move" in name_lower: key = "move"
		elif "defend" in name_lower: key = "defend"
		elif "psi" in name_lower: key = "psi"
		elif "slash" in name_lower or "blade" in name_lower or "punch" in name_lower: key = "melee"
		elif "patch" in name_lower: key = "heal"
		elif "overwatch" in name_lower: key = "watch"
		elif "missile" in name_lower: key = "missile"
		# Runtime SVG decoding also works on a fresh source checkout, before editor import.
		var icon := Image.new()
		if icon.load_svg_from_string(FileAccess.get_file_as_string("res://icons/%s.svg" % key),2.0) == OK:
			var glyph := TextureRect.new()
			glyph.name = "Glyph"
			glyph.texture = ImageTexture.create_from_image(icon)
			glyph.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			glyph.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			glyph.mouse_filter = Control.MOUSE_FILTER_IGNORE
			btn.add_child(glyph)
			var caption := Label.new()
			caption.name = "Caption"
			caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			caption.add_theme_font_size_override("font_size",18)
			caption.mouse_filter = Control.MOUSE_FILTER_IGNORE
			btn.add_child(caption)

func _update_button_styles() -> void:
	for action: String in _action_btns:
		var btn := _action_btns[action] as Button
		if btn.visible:
			var active := action.to_upper() == selected_action.to_upper() and action not in _SYSTEM_ACTIONS
			_style_btn(btn,active,turn_side != "player")
			if btn.has_node("Glyph"):
				(btn.get_node("Glyph") as TextureRect).modulate = WARN if active else NEON
			if btn.has_node("Caption"):
				(btn.get_node("Caption") as Label).add_theme_color_override("font_color",WARN if active else TEXT)

func _set_utility_icon(btn: Button, key: String, tip: String) -> void:
	var svg := Image.new()
	if svg.load_svg_from_string(FileAccess.get_file_as_string("res://icons/%s.svg" % key)) == OK:
		btn.text = ""
		btn.icon = ImageTexture.create_from_image(svg)
		btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
		btn.tooltip_text = tip
