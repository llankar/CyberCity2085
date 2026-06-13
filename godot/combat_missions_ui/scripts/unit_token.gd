extends Node2D
class_name UnitToken
## Per-unit visual rendered as a paper miniature standee: a rectangular card
## standing upright on a small isometric base, as seen in tabletop RPG setups.
## The Sprite2D child renders the character art on top of _draw() which paints
## the white card, team-colour border, HP bar, shadow, and base disc.

# ── Palette ──────────────────────────────────────────────────────────────────
const NEON         := Color(0.10, 0.95, 0.72, 1.0)
const TEXT         := Color(0.84, 0.95, 0.92, 1.0)
const WARN         := Color(1.00, 0.72, 0.22, 1.0)
const PLAYER_COL   := Color(0.10, 0.95, 0.72, 1.0)
const ENEMY_COL    := Color(1.00, 0.34, 0.30, 1.0)
const ROLE_SNIPER  := Color(0.56, 0.88, 1.00, 1.0)
const ROLE_PSI     := Color(0.76, 0.56, 1.00, 1.0)
const ROLE_SAMURAI := Color(0.28, 1.00, 0.74, 1.0)

# ── Identity ─────────────────────────────────────────────────────────────────
var unit_id  : int        = -1
var unit_data: Dictionary = {}
var is_enemy : bool       = false
var cell_size: Vector2    = Vector2(80.0, 80.0)

# ── Visual state ─────────────────────────────────────────────────────────────
var is_active    : bool  = false
var has_overwatch: bool  = false
var has_defend   : bool  = false
var is_targeted  : bool  = false
var _pulse       : float = 0.0
var _elapsed     : float = 0.0

# ── Card dimensions (world pixels) ───────────────────────────────────────────
var _card_w: float = 48.0   # card width
var _card_h: float = 72.0   # card height (taller than wide)
var _base_rx: float = 24.0  # ellipse half-width of the isometric base disc

# ── Compat aliases for callers that reference _sw/_sh ────────────────────────
var _sw: float = 24.0  # ≈ half card width — used for float-text positioning
var _sh: float = 72.0  # ≈ card height

# ── Children ─────────────────────────────────────────────────────────────────
var sprite: Sprite2D = null
var _active_tween: Tween = null

# ─────────────────────────────────────────────────────────────────────────────

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite = Sprite2D.new()
	sprite.centered  = true
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.name    = "Sprite2D"
	sprite.visible = false   # texture is drawn manually in _draw(); Sprite2D is data-only
	add_child(sprite)

func setup(data: Dictionary, id: int, enemy: bool,
		   tex: Texture2D, c_size: Vector2) -> void:
	unit_id   = id
	unit_data = data.duplicate()
	is_enemy  = enemy
	cell_size = c_size
	_recalc_dims()
	if tex != null:
		sprite.texture = tex   # stored here; drawn via draw_texture_rect in _draw()
	queue_redraw()

func update_data(data: Dictionary) -> void:
	unit_data = data.duplicate()
	_apply_damaged_shader()
	queue_redraw()

func _recalc_dims() -> void:
	# Giant units carry size_scale ≈ 3.5 in their unit_data; normal units = 1.0.
	var scale := clampf(float(unit_data.get("size_scale", 1.0)), 0.5, 5.0)
	_card_w  = cell_size.x * 0.30 * scale
	_card_h  = _card_w * 1.55
	_base_rx = _card_w * 0.46
	_sw      = _card_w * 0.5
	_sh      = _card_h
	if sprite != null:
		queue_redraw()   # texture drawn in _draw(); just trigger a redraw

func _apply_damaged_shader() -> void:
	pass   # hp tint is applied directly in _draw() via draw_texture_rect colour

# ── Process ──────────────────────────────────────────────────────────────────

func _process(delta: float) -> void:
	_elapsed += delta
	_pulse = sin(_elapsed * 4.0) * 0.5 + 0.5
	if is_active or is_targeted:
		queue_redraw()

# ── Active / targeting ───────────────────────────────────────────────────────

func set_active(active: bool) -> void:
	is_active = active
	if active:
		if _active_tween:
			_active_tween.kill()
		_active_tween = create_tween().set_loops()
		_active_tween.tween_property(self, "modulate:a", 0.85, 0.45)
		_active_tween.tween_property(self, "modulate:a", 1.0,  0.45)
	else:
		if _active_tween:
			_active_tween.kill()
			_active_tween = null
		modulate.a = 1.0
	queue_redraw()

func set_targeted(targeted: bool) -> void:
	is_targeted = targeted
	queue_redraw()

# ── Animations ───────────────────────────────────────────────────────────────

func move_to(target_pos: Vector2, updated_data: Dictionary) -> void:
	unit_data = updated_data.duplicate()
	var tw := create_tween().set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_QUAD)
	tw.tween_property(self, "position", target_pos, 0.18)
	CombatSignals.audio_event.emit("move")

func attack_lunge(target_pos: Vector2) -> void:
	var orig  := position
	var lunge := position.lerp(target_pos, 0.28)
	var tw    := create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
	tw.tween_property(self, "position", lunge, 0.10)
	tw.tween_property(self, "position", orig,  0.12)

func play_hit(damage: int, hit: bool) -> void:
	if hit:
		var tw := create_tween()
		tw.tween_property(self, "modulate", Color(1.0, 0.12, 0.12, 1.0), 0.05)
		tw.tween_property(self, "modulate", Color(1.0, 1.0,  1.0,  1.0), 0.18)
		_spawn_float_text("-%d" % damage, Color(1.0, 0.28, 0.18, 1.0))
		hp_canvas_redraw()
	else:
		var tw := create_tween()
		tw.tween_property(self, "modulate", Color(0.55, 0.55, 1.0, 1.0), 0.08)
		tw.tween_property(self, "modulate", Color(1.0,  1.0,  1.0, 1.0), 0.22)
		_spawn_float_text("MISS", Color(0.58, 0.68, 1.0, 1.0))

func hp_canvas_redraw() -> void:
	queue_redraw()

func play_death() -> void:
	var tw := create_tween()
	for _i in range(3):
		tw.tween_property(self, "modulate:a", 0.08, 0.07)
		tw.tween_property(self, "modulate:a", 0.9,  0.07)
	tw.set_parallel(false)
	tw.tween_property(self, "position:y", position.y + 14.0, 0.35)
	tw.parallel().tween_property(self, "modulate:a", 0.0, 0.35)
	tw.tween_callback(queue_free)
	CombatSignals.audio_event.emit("death")
	CombatSignals.fx_at.emit("death_dissolve", global_position)

func _spawn_float_text(text: String, col: Color) -> void:
	var lbl := Label.new()
	lbl.text = text
	lbl.add_theme_color_override("font_color", col)
	lbl.add_theme_font_size_override("font_size", 14)
	lbl.z_index = 20
	lbl.position = Vector2(-14.0, -_card_h - 8.0)
	add_child(lbl)
	var tw := create_tween().set_parallel(true)
	tw.tween_property(lbl, "position:y", lbl.position.y - 36.0, 0.90)
	tw.tween_property(lbl, "modulate:a", 0.0, 0.90)
	tw.chain().tween_callback(lbl.queue_free)

# ── Input ────────────────────────────────────────────────────────────────────

func _unhandled_input(event: InputEvent) -> void:
	if int(unit_data.get("hp", 0)) <= 0:
		return
	var inv := get_viewport().get_canvas_transform().affine_inverse()
	if event is InputEventMouseButton:
		var mbe   := event as InputEventMouseButton
		if not mbe.pressed and mbe.button_index == MOUSE_BUTTON_LEFT:
			var local := to_local(inv * mbe.position)
			if absf(local.x) <= _card_w * 0.5 and \
					local.y >= -_card_h and local.y <= 0.0:
				CombatSignals.unit_clicked.emit(unit_id, is_enemy)
				get_viewport().set_input_as_handled()
	elif event is InputEventMouseMotion:
		var local := to_local(inv * (event as InputEventMouseMotion).position)
		if absf(local.x) <= _card_w * 0.5 and \
				local.y >= -_card_h and local.y <= 0.0:
			CombatSignals.unit_hovered.emit(unit_id, is_enemy)

# ── Custom drawing ────────────────────────────────────────────────────────────
# Draw order (back to front):
#   shadow ellipse → isometric base disc → card glow (if active) →
#   character art (draw_texture_rect, always fills card exactly) →
#   HP bar strip → targeted chevrons → name label → status badges.

func _draw() -> void:
	if int(unit_data.get("hp", 0)) <= 0:
		return

	var rc := _role_color()
	var cw := _card_w
	var ch := _card_h

	# 1 — Ground shadow: very flat isometric ellipse offset below/behind the base.
	draw_set_transform(Vector2(3.0, 7.0), 0.0, Vector2(1.20, 0.28))
	draw_circle(Vector2.ZERO, _base_rx, Color(0.0, 0.0, 0.0, 0.44))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

	# 2 — Isometric base disc (the small black oval the standee sits on).
	draw_set_transform(Vector2.ZERO, 0.0, Vector2(1.0, 0.36))
	draw_circle(Vector2.ZERO, _base_rx,        Color(0.06, 0.06, 0.09, 0.97))
	draw_circle(Vector2.ZERO, _base_rx * 0.84, Color(0.18, 0.20, 0.26, 0.80))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

	# 3 — Active: soft glow behind the card (pulsing coloured halo).
	if is_active:
		var ga := 0.18 + 0.22 * _pulse
		var gw := cw * 0.14
		draw_rect(Rect2(-cw * 0.5 - gw, -ch - gw, cw + gw * 2.0, ch + gw * 2.0),
				  Color(rc.r, rc.g, rc.b, ga), true)

	# 4 — Character art: always fill the card rect exactly, no scale arithmetic.
	if sprite != null and sprite.texture != null:
		var hp_frac := float(int(unit_data.get("hp", 1))) / \
					   float(maxi(1, int(unit_data.get("max_hp", 1))))
		var art_col := Color.WHITE
		if hp_frac < 0.5:
			art_col = Color.WHITE.lerp(Color(1.0, 0.45, 0.35, 1.0), (0.5 - hp_frac) * 2.0)
		draw_texture_rect(sprite.texture,
						  Rect2(-cw * 0.5, -ch, cw, ch),
						  false, art_col)

	# 6 — HP bar: thin coloured strip just below the card bottom, on the base.
	var hp     := int(unit_data.get("hp",     0))
	var max_hp := maxi(1, int(unit_data.get("max_hp", 1)))
	var hp_frac := clampf(float(hp) / float(max_hp), 0.0, 1.0)
	var hp_col  := PLAYER_COL if hp_frac > 0.5 else (WARN if hp_frac > 0.25 else ENEMY_COL)
	var bar_y   := 4.0
	var bar_h   := 5.0
	draw_rect(Rect2(-cw * 0.5, bar_y, cw, bar_h),
			  Color(0.05, 0.06, 0.08, 0.88), true)
	if hp_frac > 0.01:
		draw_rect(Rect2(-cw * 0.5, bar_y, cw * hp_frac, bar_h), hp_col, true)
	draw_rect(Rect2(-cw * 0.5, bar_y, cw, bar_h),
			  Color(rc.r, rc.g, rc.b, 0.35), false, 1.0)

	# 7 — Targeted: spinning corner chevrons around the card.
	if is_targeted and not is_active:
		var spin := fmod(_elapsed * 1.8, 1.0)
		var corners : PackedVector2Array = PackedVector2Array([
			Vector2(-cw * 0.5, -ch),
			Vector2( cw * 0.5, -ch),
			Vector2( cw * 0.5,  0.0),
			Vector2(-cw * 0.5,  0.0),
		])
		var ti := int(spin * 4.0) % 4
		for di in range(2):
			var ci := (ti + di * 2) % 4
			draw_circle(corners[ci], 3.0, Color(WARN.r, WARN.g, WARN.b, 0.88))

	# 8 — Name label: small dark pill at the base of the sprite for readability.
	var display_name: String
	if is_enemy:
		display_name = str(unit_data.get("enemy_subtype", "ENEMY")).to_upper()
	else:
		display_name = str(unit_data.get("name", "?")).split(" ")[0].to_upper()
	var lbl_w := cw * 0.92
	draw_rect(Rect2(-lbl_w * 0.5, -18.0, lbl_w, 14.0),
			  Color(0.0, 0.0, 0.0, 0.62), true)
	_ds(display_name, Vector2(0.0, -7.0), 8, TEXT)

	# 9 — Status badges: top-right corner, outside card.
	var bx := cw * 0.5 + 4.0
	var by := -ch + 4.0
	if has_overwatch:
		_ds("OW",  Vector2(bx, by), 7, ROLE_SNIPER);  by += 11.0
	if has_defend:
		_ds("DEF", Vector2(bx, by), 7, ROLE_SAMURAI); by += 11.0
	if int(unit_data.get("stress", 0)) >= 70:
		_ds("SUP", Vector2(bx, by), 7, WARN)

func _ds(text: String, pos: Vector2, sz: int, col: Color) -> void:
	draw_string(ThemeDB.fallback_font, pos, text,
			HORIZONTAL_ALIGNMENT_CENTER, -1, sz, col)

func _role_color() -> Color:
	if is_enemy:
		return ENEMY_COL
	match str(unit_data.get("role", "")).to_lower():
		"sniper": return ROLE_SNIPER
		"psi":    return ROLE_PSI
		"robot":  return Color(1.0, 0.35, 0.20, 1.0)
		_:        return ROLE_SAMURAI
