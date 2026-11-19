extends Control
class_name PhaseBanner
## Animated turn-change announcement that slides in from the top, holds, then
## slides out.  CombatRoot calls show_banner(side, turn_number).

const NEON       := Color(0.10, 0.95, 0.72, 1.0)
const ENEMY_COL  := Color(1.00, 0.34, 0.30, 1.0)
const TEXT       := Color(0.84, 0.95, 0.92, 1.0)
const WARN       := Color(1.00, 0.72, 0.22, 1.0)

const HOLD_DURATION  := 1.3
const SLIDE_DURATION := 0.28

var _label_text : String = ""
var _label_col  : Color  = NEON
var _bar_col    : Color  = NEON
var _slide_y    : float  = -80.0   # current Y of the banner rect
var _active     : bool   = false

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE

func show_banner(side: String, turn_num: int) -> void:
	_active = true
	if side == "player":
		_label_text = "PLAYER TURN — %02d" % turn_num
		_label_col  = NEON
		_bar_col    = NEON
	elif side == "enemy":
		_label_text = "ENEMY TURN — %02d" % turn_num
		_label_col  = ENEMY_COL
		_bar_col    = ENEMY_COL
	else:
		_label_text = "MISSION COMPLETE"
		_label_col  = WARN
		_bar_col    = WARN

	visible   = true
	_slide_y  = -80.0
	var mid_y := size.y * 0.5 - 28.0

	var tw := create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
	tw.tween_property(self, "_slide_y", mid_y, SLIDE_DURATION)
	tw.tween_interval(HOLD_DURATION)
	tw.set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_QUAD)
	tw.tween_property(self, "_slide_y", -80.0, SLIDE_DURATION)
	tw.tween_callback(_on_slide_done)
	tw.tween_property(self, "modulate:a", 1.0, 0.0)  # ensure visible on next show
	queue_redraw()

func _on_slide_done() -> void:
	visible = false
	_active = false

func _draw() -> void:
	if not _active:
		return
	var bw := size.x * 0.55
	var bh := 56.0
	var bx := (size.x - bw) * 0.5
	# Shadow
	draw_rect(Rect2(bx + 4, _slide_y + 4, bw, bh), Color(0, 0, 0, 0.55), true)
	# Panel
	draw_rect(Rect2(bx, _slide_y, bw, bh), Color(0.02, 0.05, 0.08, 0.96), true)
	draw_rect(Rect2(bx, _slide_y, bw, bh), _bar_col, false, 2.5)
	# Side accent lines
	draw_line(Vector2(bx - 24, _slide_y + bh * 0.5),
			  Vector2(bx - 4,  _slide_y + bh * 0.5), _bar_col, 2.0)
	draw_line(Vector2(bx + bw + 4,  _slide_y + bh * 0.5),
			  Vector2(bx + bw + 24, _slide_y + bh * 0.5), _bar_col, 2.0)
	# Text
	draw_string(ThemeDB.fallback_font,
			Vector2(size.x * 0.5, _slide_y + bh * 0.5 + 7.0),
			_label_text, HORIZONTAL_ALIGNMENT_CENTER, -1, 18, _label_col)
