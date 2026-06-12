extends Control
class_name HudController
## Draws all HUD panels: full dark background, top bar, right panel (initiative +
## action buttons), portrait strip, optional combat log.
## Action bar uses real Button nodes for hover/click; everything else is drawn
## via _draw() to keep the custom neon aesthetic.

# ── Palette ──────────────────────────────────────────────────────────────────
const PANEL       := Color(0.02, 0.05, 0.08, 0.94)
const NEON        := Color(0.10, 0.95, 0.72, 1.0)
const TEXT        := Color(0.84, 0.95, 0.92, 1.0)
const WARN        := Color(1.00, 0.72, 0.22, 1.0)
const PLAYER_COL  := Color(0.10, 0.95, 0.72, 1.0)
const ENEMY_COL   := Color(1.00, 0.34, 0.30, 1.0)
const ROLE_SNIPER  := Color(0.56, 0.88, 1.00, 1.0)
const ROLE_PSI     := Color(0.76, 0.56, 1.00, 1.0)
const ROLE_SAMURAI := Color(0.28, 1.00, 0.74, 1.0)

# ── Layout ───────────────────────────────────────────────────────────────────
const TOP_BAR_H    : float = 44.0
const RIGHT_PANEL_W: float = 340.0
const STRIP_H      : float = 158.0
const LEFT_MARGIN  : float = 70.0
const CARD_W       : float = 80.0
const CARD_GAP     : float = 4.0

# System actions always shown; agent combat actions come from active unit's available_actions.
const _SYSTEM_ACTIONS: Array[String] = ["NEXT", "END TURN"]

# ── State ─────────────────────────────────────────────────────────────────────
var player_units      : Array[Dictionary] = []
var enemy_units       : Array[Dictionary] = []
var initiative_entries: Array[Dictionary] = []
var active_player_idx : int    = 0
var selected_action   : String = "MOVE"
var turn_side         : String = "player"
var turn_number       : int    = 1
var combat_log        : Array[String] = []
var show_log          : bool   = false
var portrait_textures : Dictionary = {}
var status_line       : String = ""
var _elapsed          : float  = 0.0
var _hovered_portrait : int    = -1

# ── Action buttons ────────────────────────────────────────────────────────────
var _action_btns   : Dictionary      = {}   # action name → Button
var _visible_actions: Array[String]  = []   # current ordered display list

# ─────────────────────────────────────────────────────────────────────────────

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST  # crisp pixel-art portraits
	mouse_filter = Control.MOUSE_FILTER_PASS
	set_process(true)
	# Defer button creation until size is known
	call_deferred("_build_action_buttons")

func _process(delta: float) -> void:
	_elapsed += delta
	queue_redraw()

func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		_reposition_buttons()

# ── Public API (called by CombatRoot) ─────────────────────────────────────────

func update_state(
		p_units: Array[Dictionary],
		e_units: Array[Dictionary],
		init_e : Array[Dictionary],
		act_idx: int, action: String,
		side: String, turn_num: int,
		log: Array[String], portraits: Dictionary,
		s_line: String
) -> void:
	player_units       = p_units
	enemy_units        = e_units
	initiative_entries = init_e
	active_player_idx  = act_idx
	selected_action    = action
	turn_side          = side
	turn_number        = turn_num
	combat_log         = log
	portrait_textures  = portraits
	status_line        = s_line
	_rebuild_agent_actions()
	_update_button_styles()
	queue_redraw()

# ── Button management ─────────────────────────────────────────────────────────

func _build_action_buttons() -> void:
	# Buttons are created lazily on first update_state — nothing to do here.
	_reposition_buttons()

func _rebuild_agent_actions() -> void:
	# Derive the current agent's action list; fall back to a generic set.
	var agent_actions: Array[String] = []
	if not player_units.is_empty() and active_player_idx < player_units.size():
		var agent := player_units[active_player_idx] as Dictionary
		var raw: Variant = agent.get("available_actions", null)
		if typeof(raw) == TYPE_ARRAY:
			for a: Variant in raw as Array:
				agent_actions.append(str(a))
	if agent_actions.is_empty():
		agent_actions = ["Move", "Defend", "Rifle Burst", "Pistol Shot", "Overwatch"]
	# Always append system actions at the bottom.
	var full: Array[String] = []
	full.assign(agent_actions)
	for s in _SYSTEM_ACTIONS:
		if s not in full:
			full.append(s)
	_visible_actions = full
	_ensure_action_buttons(_visible_actions)
	# Hide buttons that are no longer in the visible list.
	for key in _action_btns.keys():
		(_action_btns[key] as Button).visible = key in _visible_actions
	_reposition_buttons()

func _ensure_action_buttons(actions: Array[String]) -> void:
	for action in actions:
		if _action_btns.has(action):
			continue
		var btn := Button.new()
		btn.text         = action
		btn.focus_mode   = Control.FOCUS_NONE
		btn.mouse_filter = Control.MOUSE_FILTER_STOP
		btn.pressed.connect(_on_action_pressed.bind(action))
		_style_btn(btn, false, false)
		add_child(btn)
		_action_btns[action] = btn

func _reposition_buttons() -> void:
	if size.x == 0.0:
		return
	var rp_x  := size.x - RIGHT_PANEL_W + 8.0
	var pw    := RIGHT_PANEL_W - 16.0
	var y0    := TOP_BAR_H + 4.0 + 186.0
	var y_max := size.y - STRIP_H - 8.0
	# Only lay out currently visible buttons.
	var visible: Array[String] = []
	for a in _visible_actions:
		if _action_btns.has(a) and (_action_btns[a] as Button).visible:
			visible.append(a)
	var n := float(visible.size())
	if n == 0:
		return
	var step  := clampf((y_max - y0) / n, 28.0, 42.0)
	var btn_h := step - 4.0
	var by    := y0
	for action: String in visible:
		var btn := _action_btns[action] as Button
		btn.position = Vector2(rp_x, by)
		btn.size     = Vector2(pw, btn_h)
		by          += step

func _style_btn(btn: Button, active: bool, disabled: bool) -> void:
	var bg  := Color(0.08, 0.22, 0.28, 0.96) if active else Color(0.04, 0.10, 0.14, 0.92)
	var bdr := WARN if active else NEON
	for state in ["normal", "hover", "pressed", "disabled", "focus"]:
		var s := StyleBoxFlat.new()
		s.bg_color     = bg if state != "hover" else Color(0.10, 0.30, 0.38, 0.96)
		s.border_color = bdr if state != "disabled" else Color(0.3, 0.3, 0.3, 0.45)
		s.set_border_width_all(2)
		for c in [0, 1, 2, 3]:
			s.set_corner_radius(c, 2)
		btn.add_theme_stylebox_override(state, s)
	btn.add_theme_color_override("font_color",          WARN if active else TEXT)
	btn.add_theme_color_override("font_hover_color",    NEON)
	btn.add_theme_color_override("font_pressed_color",  WARN)
	btn.add_theme_color_override("font_disabled_color", Color(0.35, 0.35, 0.35, 0.5))
	btn.add_theme_font_size_override("font_size", 12)
	btn.disabled = disabled

func _update_button_styles() -> void:
	var is_player := turn_side == "player"
	for action: String in _action_btns.keys():
		var btn := _action_btns[action] as Button
		if not btn.visible:
			continue
		# System actions (NEXT, END TURN) are never "selected" — keep them neutral.
		var is_selected := action == selected_action and action not in _SYSTEM_ACTIONS
		_style_btn(btn, is_selected, not is_player)

func _on_action_pressed(action: String) -> void:
	CombatSignals.action_pressed.emit(action)
	CombatSignals.audio_event.emit("ui_click")

# ── Input (portrait hover) ────────────────────────────────────────────────────

func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		var mme    := event as InputEventMouseMotion
		var strip_y := size.y - STRIP_H
		var start_x := LEFT_MARGIN + 4.0
		var prev    := _hovered_portrait
		_hovered_portrait = -1
		for i in range(player_units.size()):
			var rx := start_x + float(i) * (CARD_W + CARD_GAP)
			if Rect2(rx, strip_y, CARD_W, STRIP_H - 12.0).has_point(mme.position):
				_hovered_portrait = i
				break
		if _hovered_portrait != prev:
			queue_redraw()

# ── Drawing ───────────────────────────────────────────────────────────────────

func _draw() -> void:
	_draw_background()
	_draw_top_bar()
	_draw_right_panel_bg()
	_draw_initiative()
	_draw_portrait_strip()
	_draw_status_line()
	if show_log:
		_draw_combat_log()

func _draw_background() -> void:
	pass  # Individual rows and buttons draw their own backgrounds.

func _draw_top_bar() -> void:
	var alive_p: int = 0
	for u: Dictionary in player_units:
		if int(u.get("hp", 0)) > 0: alive_p += 1
	var alive_e: int = 0
	for u: Dictionary in enemy_units:
		if int(u.get("hp", 0)) > 0: alive_e += 1

	draw_rect(Rect2(42, 36, size.x - 84.0, TOP_BAR_H), Color(0, 0, 0, 0.80), true)
	draw_line(Vector2(42, 36 + TOP_BAR_H), Vector2(size.x - 42, 36 + TOP_BAR_H), NEON, 2.0)

	var cy := 36.0 + TOP_BAR_H * 0.5 + 5.0
	_ds("SQUAD %d" % alive_p, Vector2(90.0, cy), 12, PLAYER_COL)
	_ds_center(str(turn_side.to_upper()) + " — TURN %02d" % turn_number,
			   Vector2(size.x * 0.5, cy), 13, TEXT, 320.0)
	_ds("ENEMIES %d" % alive_e, Vector2(size.x - 150.0, cy), 12, ENEMY_COL)

func _draw_right_panel_bg() -> void:
	pass  # Already drawn in _draw_background; action buttons are real nodes

func _draw_initiative() -> void:
	if initiative_entries.is_empty():
		return
	var rp_x := size.x - RIGHT_PANEL_W + 8.0
	var pw   := RIGHT_PANEL_W - 16.0
	var y    := TOP_BAR_H + 12.0

	_ds("INITIATIVE", Vector2(rp_x, y + 12.0), 10, NEON)
	y += 22.0

	var max_show := mini(initiative_entries.size(), 6)
	for i in range(max_show):
		var entry : Dictionary = initiative_entries[i]
		var name  := str(entry.get("name", "?")).split(" ")[0].to_upper().substr(0, 9)
		var enemy : bool = bool(entry.get("is_enemy", false))
		var col   := ENEMY_COL if enemy else PLAYER_COL
		var active := bool(entry.get("active", false))

		if active:
			draw_rect(Rect2(rp_x, y, pw, 22.0), Color(col.r, col.g, col.b, 0.18), true)
			draw_rect(Rect2(rp_x, y, pw, 22.0), col, false, 1.0)
			_ds("▶", Vector2(rp_x + 4.0, y + 15.0), 10, col)
		else:
			draw_rect(Rect2(rp_x, y, pw, 22.0), Color(0, 0, 0, 0.0), false)
			draw_line(Vector2(rp_x, y + 21.0), Vector2(rp_x + pw, y + 21.0),
					  Color(col.r, col.g, col.b, 0.18), 1.0)
			_ds("·", Vector2(rp_x + 4.0, y + 15.0), 10, Color(col.r, col.g, col.b, 0.5))

		_ds(name, Vector2(rp_x + 20.0, y + 15.0), 11, col)

		# HP mini-bar
		var hp      : int   = int(entry.get("hp", 0))
		var max_hp  : int   = maxi(1, int(entry.get("max_hp", 1)))
		var hp_frac : float = clampf(float(hp) / float(max_hp), 0.0, 1.0)
		var hp_col  : Color = PLAYER_COL if hp_frac > 0.5 else (WARN if hp_frac > 0.25 else ENEMY_COL)
		var bar_x   := rp_x + pw - 46.0
		draw_rect(Rect2(bar_x, y + 8.0, 40.0, 5.0), Color(0.05, 0.10, 0.12, 1.0), true)
		draw_rect(Rect2(bar_x, y + 8.0, 40.0 * hp_frac, 5.0), hp_col, true)
		y += 26.0

func _draw_portrait_strip() -> void:
	if player_units.is_empty():
		return
	var strip_y := size.y - STRIP_H
	var card_h  := STRIP_H - 12.0
	var start_x := LEFT_MARGIN + 4.0

	var bf_w := maxf(300.0, size.x - RIGHT_PANEL_W - LEFT_MARGIN - 10.0)

	for i in range(player_units.size()):
		var unit   : Dictionary = player_units[i]
		var x      := start_x + float(i) * (CARD_W + CARD_GAP)
		var active := i == active_player_idx and turn_side == "player"
		var dead   := int(unit.get("hp", 0)) <= 0
		var role   := str(unit.get("role", "agent")).to_lower()
		var rc     := _role_color_for(role, false)

		draw_rect(Rect2(x, strip_y + 2.0, CARD_W, card_h - 2.0),
				  Color(0.12, 0.28, 0.36, 0.95) if active else Color(0.04, 0.10, 0.14, 0.88), true)
		draw_line(Vector2(x, strip_y + 2.0), Vector2(x + CARD_W, strip_y + 2.0),
				  rc if active else Color(rc.r, rc.g, rc.b, 0.28), 2.0)
		# Hover highlight
		if i == _hovered_portrait and not active:
			draw_rect(Rect2(x, strip_y + 2.0, CARD_W, card_h - 2.0),
					  Color(rc.r, rc.g, rc.b, 0.08), true)

		if dead:
			draw_rect(Rect2(x, strip_y + 2.0, CARD_W, card_h - 2.0), Color(0, 0, 0, 0.72), true)
			_ds_center("K.I.A.", Vector2(x + CARD_W * 0.5, strip_y + card_h * 0.5 + 4.0),
					   10, ENEMY_COL, CARD_W)
			continue

		# Portrait image (40×52) or placeholder
		var pr    := Rect2(x + 4.0, strip_y + 8.0, 40.0, 52.0)
		var pname := str(unit.get("name", ""))
		var ptex  := portrait_textures.get(pname, null) as Texture2D
		if ptex != null:
			draw_texture_rect(ptex, pr, false)
		else:
			draw_rect(pr, Color(0.08, 0.18, 0.24, 0.95), true)
			_ds_center(str(unit.get("role", "?")).to_upper().substr(0, 1),
					   Vector2(x + 24.0, strip_y + 36.0), 14, rc, 40.0)
		draw_rect(pr, rc, false, 1.0)

		# Active glow ring
		if active:
			var pulse := 0.7 + 0.3 * sin(_elapsed * 3.0)
			draw_arc(Vector2(x + 24.0, strip_y + 34.0), 28.0,
					 0.0, TAU, 48, Color(rc.r, rc.g, rc.b, pulse), 1.5)

		# Name + role text
		_ds(str(unit.get("name", "Agent")).substr(0, 7).to_upper(),
			Vector2(x + 48.0, strip_y + 20.0), 8, TEXT)
		_ds(role.to_upper().substr(0, 5), Vector2(x + 48.0, strip_y + 33.0), 7, rc)

		# HP bar
		var hp_frac : float = clampf(
				float(int(unit.get("hp", 0))) / float(maxi(1, int(unit.get("max_hp", 1)))),
				0.0, 1.0)
		var hp_col  : Color = PLAYER_COL if hp_frac > 0.5 else (WARN if hp_frac > 0.25 else ENEMY_COL)
		var bar_y   := strip_y + 64.0
		draw_rect(Rect2(x + 4.0, bar_y,        CARD_W - 8.0,            5.0),
				  Color(0.05, 0.10, 0.12, 1.0), true)
		draw_rect(Rect2(x + 4.0, bar_y, (CARD_W - 8.0) * hp_frac, 5.0), hp_col, true)

		# Stress bar
		var str_frac : float = clampf(float(int(unit.get("stress", 0))) / 100.0, 0.0, 1.0)
		var str_col  : Color = Color(0.28, 0.72, 1.0, 0.8) if str_frac < 0.5 else \
				(WARN if str_frac < 0.8 else ENEMY_COL)
		draw_rect(Rect2(x + 4.0, bar_y + 7.0, CARD_W - 8.0,                  3.0),
				  Color(0.05, 0.10, 0.12, 1.0), true)
		draw_rect(Rect2(x + 4.0, bar_y + 7.0, (CARD_W - 8.0) * str_frac, 3.0), str_col, true)

		# AP pips
		var ap     := int(unit.get("ap", 0))
		for d in range(2):
			draw_rect(Rect2(x + 4.0 + float(d) * 12.0, bar_y + 13.0, 9.0, 5.0),
					  PLAYER_COL if d < ap else Color(0.08, 0.16, 0.22, 1.0), true)

func _draw_status_line() -> void:
	if status_line.is_empty():
		return
	_ds(status_line, Vector2(LEFT_MARGIN, size.y - STRIP_H - 8.0), 12, NEON)

func _draw_combat_log() -> void:
	var lw  := 360.0
	var lh  := 200.0
	var lx  := size.x - RIGHT_PANEL_W - lw - 8.0
	var ly  := size.y - STRIP_H - lh - 8.0
	draw_rect(Rect2(lx, ly, lw, lh), Color(0.01, 0.03, 0.05, 0.94), true)
	draw_rect(Rect2(lx, ly, lw, lh), NEON, false, 1.5)
	_ds("COMBAT LOG", Vector2(lx + 8.0, ly + 14.0), 10, NEON)
	draw_line(Vector2(lx, ly + 20.0), Vector2(lx + lw, ly + 20.0), NEON, 1.0)
	var ty := ly + 32.0
	var max_lines := mini(combat_log.size(), 8)
	for i in range(max_lines):
		var line := str(combat_log[combat_log.size() - max_lines + i])
		_ds(line, Vector2(lx + 8.0, ty), 9, TEXT)
		ty += 18.0

# ── Draw helpers ─────────────────────────────────────────────────────────────

func _ds(text: String, pos: Vector2, sz: int, col: Color) -> void:
	draw_string(ThemeDB.fallback_font, pos, text,
			HORIZONTAL_ALIGNMENT_LEFT, -1, sz, col)

func _ds_center(text: String, pos: Vector2, sz: int, col: Color, max_w: float = -1.0) -> void:
	draw_string(ThemeDB.fallback_font, pos, text,
			HORIZONTAL_ALIGNMENT_CENTER, int(max_w), sz, col)

func _role_color_for(role: String, is_enemy: bool) -> Color:
	if is_enemy: return ENEMY_COL
	match role:
		"sniper": return ROLE_SNIPER
		"psi":    return ROLE_PSI
		_:        return ROLE_SAMURAI
