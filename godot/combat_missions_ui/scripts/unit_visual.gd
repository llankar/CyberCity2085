extends "res://scripts/unit_token.gd"
## Grounded art; genuine atlas frames only. Missing clips keep static source art.
const HUMAN_HEIGHT_PER_TILE := 0.286

var visual_key := ""
var animation_root := ""
var atlas: Texture2D
var manifest: Dictionary = {}
var facing := 0
var clip := "idle"
var frame_time := 0.0
var frame_index := 0
var _moving: Tween
var _death := false
var _art_rect := Rect2()
var _hit_image: Image
var _portrait_bounds_uv := Rect2(0,0,1,1)
var _active_bounds_uv := Rect2(0,0,1,1)
var _frame_bounds: Dictionary = {}
static var _atlas_cache: Dictionary = {}

func _ready() -> void:
	super._ready()
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR

func configure_animation(key: String, root: String) -> void:
	visual_key = key
	animation_root = root
	var path := root.path_join("assets/combat_visual/animations/%s.json" % key)
	if _atlas_cache.has(path):
		var cached: Dictionary = _atlas_cache[path]
		manifest = cached.get("manifest", {})
		atlas = cached.get("atlas", null)
		_frame_bounds = cached.get("frame_bounds", {})
		return
	if FileAccess.file_exists(path):
		var raw: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		if raw is Dictionary:
			manifest = raw
			var image := Image.load_from_file(root.path_join(str(manifest.get("texture", ""))))
			if image != null:
				atlas = ImageTexture.create_from_image(image)
				var frame_size: Array = manifest.get("frame_size",[256,256])
				_frame_bounds = _measure_atlas_bounds(image,Vector2i(int(frame_size[0]),int(frame_size[1])))
	_atlas_cache[path] = {"manifest": manifest, "atlas": atlas, "frame_bounds": _frame_bounds}

func play_action(action: String, toward: Vector2 = Vector2.ZERO) -> bool:
	if toward != Vector2.ZERO:
		var delta := toward - position
		facing = posmod(int(round(atan2(delta.y * 2.0, delta.x) / (TAU / 8.0))), 8)
	if not (manifest.get("animations", {}) as Dictionary).has(action): return false
	clip = action
	frame_time = 0
	frame_index = 0
	return true

func _process(delta: float) -> void:
	_elapsed += delta
	_pulse = sin(_elapsed * 3.0) * 0.5 + 0.5
	if not manifest.is_empty() and atlas != null:
		var anim: Dictionary = (manifest.get("animations", {}) as Dictionary).get(clip, {})
		if not anim.is_empty():
			var rows: Array = anim.get("rows", [])
			if rows.size() == 8:
				var frames: Array = rows[facing]
				frame_time += delta
				var tick := int(frame_time * float(anim.get("fps", 8)))
				frame_index = tick % maxi(1, frames.size()) if bool(anim.get("loop", false)) else mini(tick, frames.size()-1)
				if tick >= frames.size() and not bool(anim.get("loop", false)) and not _death: play_action("idle")
	queue_redraw()

func set_active(active: bool) -> void:
	is_active = active
	queue_redraw()

func move_to(target_pos: Vector2, updated_data: Dictionary) -> void:
	move_route([target_pos], updated_data)

func move_route(points: Array[Vector2], updated_data: Dictionary) -> void:
	unit_data = updated_data.duplicate()
	if _moving: _moving.kill()
	_moving = create_tween()
	for p: Vector2 in points:
		_moving.tween_callback(play_action.bind("move", p))
		_moving.tween_property(self, "position", p, 0.13)
	_moving.tween_callback(play_action.bind("idle"))
	CombatSignals.audio_event.emit("move")

func attack_lunge(target_pos: Vector2) -> void:
	# Legacy API: no displacement masquerading as a character animation.
	play_action("fire", target_pos)

func play_hit(damage: int, hit: bool) -> void:
	if hit:
		play_action("hit")
		CombatSignals.fx_at.emit("impact",position-Vector2(0,_sh*0.5))
	_spawn_float_text("-%d" % damage if hit else "MISS", ENEMY_COL if hit else TEXT)

func play_death() -> void:
	_death = true
	play_action("death")
	CombatSignals.audio_event.emit("death")

func _draw() -> void:
	var dead := int(unit_data.get("hp", 0)) <= 0
	if dead and (not _death or clip != "death"): return
	var rc := ENEMY_COL if is_enemy else Color(0.10,0.95,1.0)
	var footprint := cell_size.x * 0.10 * minf(_visual_size_scale(),3.0) * TOKEN_PRESENTATION_SCALE
	draw_set_transform(Vector2(4, 3), 0, Vector2(1, 0.32))
	draw_circle(Vector2.ZERO, footprint, Color(0, 0, 0, 0.34))
	draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)
	if is_active or has_defend or has_overwatch:
		var radius := maxf(footprint,cell_size.x*0.21) if is_active else footprint
		var ring := PackedVector2Array([Vector2(0,-radius*0.5),Vector2(radius,0),Vector2(0,radius*0.5),Vector2(-radius,0),Vector2(0,-radius*0.5)])
		draw_colored_polygon(ring, Color(rc, 0.08))
		if is_active:
			draw_polyline(ring,Color(rc,0.12),10*_screen_pixel().x,true)
		draw_polyline(ring,Color(rc,0.9),2*_screen_pixel().x,true)
	var tex := sprite.texture if sprite != null else null
	if tex == null: return
	var height := _body_height()
	var source := Rect2(Vector2.ZERO, tex.get_size())
	_active_bounds_uv = _portrait_bounds_uv
	if atlas != null and not manifest.is_empty():
		var anim: Dictionary = (manifest.get("animations", {}) as Dictionary).get(clip, {})
		var rows: Array = anim.get("rows", [])
		if rows.size() == 8 and not (rows[facing] as Array).is_empty():
			var fs: Array = manifest.get("frame_size", [256,256])
			var fsize := Vector2(float(fs[0]), float(fs[1]))
			var idx := int(rows[facing][clampi(frame_index, 0, rows[facing].size()-1)])
			var columns := maxi(1, int(atlas.get_width() / fsize.x))
			source = Rect2(Vector2(idx % columns, idx / columns) * fsize, fsize)
			tex = atlas
			_active_bounds_uv = _frame_bounds.get(idx,Rect2(0,0,1,1))
	var width := height * source.size.x / maxf(1, source.size.y)
	_art_rect = Rect2(-width * 0.5, -height, width, height)
	draw_texture_rect_region(tex, _art_rect, source, Color(0.36,0.4,0.44) if dead else Color.WHITE)
	_card_w = width
	_card_h = height
	_sh = height
	if dead: return
	_draw_segmented_health(rc)
	if is_targeted:
		var r := _art_rect.grow(5)
		for p: Vector2 in [r.position, Vector2(r.end.x,r.position.y), r.end, Vector2(r.position.x,r.end.y)]:
			var dx := 1.0 if p.x < 0 else -1.0
			var dy := 1.0 if p.y < r.get_center().y else -1.0
			draw_line(p, p+Vector2(dx*10,0), ENEMY_COL, 2, true)
			draw_line(p, p+Vector2(0,dy*10), ENEMY_COL, 2, true)
	if has_defend or has_overwatch:
		_ds("DEF" if has_defend else "OW", Vector2(width*0.5,-height*0.5), 9, rc)

func setup(data: Dictionary, id: int, enemy: bool, tex: Texture2D, c_size: Vector2) -> void:
	super.setup(data,id,enemy,tex,c_size)
	if tex != null:
		_hit_image = tex.get_image()
		if _hit_image != null:
			var used := _hit_image.get_used_rect()
			var dimensions := Vector2(_hit_image.get_size())
			_portrait_bounds_uv = Rect2(Vector2(used.position)/dimensions,Vector2(used.size)/dimensions)
			_active_bounds_uv = _portrait_bounds_uv
	_recalc_dims()

func _recalc_dims() -> void:
	super._recalc_dims()
	var tex: Texture2D = sprite.texture if sprite != null else null
	var height := _body_height()
	var aspect := float(tex.get_width()) / maxf(1,float(tex.get_height())) if tex != null else 0.7
	_card_w = height*aspect
	_card_h = height
	_sh = height
	_art_rect = Rect2(-_card_w*0.5,-height,_card_w,height)

func _unhandled_input(event: InputEvent) -> void:
	if unit_id >= 1000 or int(unit_data.get("hp",0)) <= 0: return
	if event is not InputEventMouseButton and event is not InputEventMouseMotion: return
	var local := to_local(get_viewport().get_canvas_transform().affine_inverse()*event.position)
	if not _art_rect.has_point(local): return
	if _hit_image != null and atlas == null:
		var uv := (local-_art_rect.position)/_art_rect.size
		var pixel := Vector2i(int(uv.x*_hit_image.get_width()),int(uv.y*_hit_image.get_height()))
		if _hit_image.get_pixelv(pixel).a < 0.15: return
	if event is InputEventMouseButton:
		if not event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			CombatSignals.unit_clicked.emit(unit_id,is_enemy)
			get_viewport().set_input_as_handled()
	else:
		CombatSignals.unit_hovered.emit(unit_id,is_enemy)

func _visual_size_scale() -> float:
	var role := str(unit_data.get("role",""))
	var theme := str(unit_data.get("enemy_theme",""))
	if role in ["power_armor","heavy_armor"] or "power_armor" in theme: return 1.15
	return clampf(float(unit_data.get("size_scale",1)),0.5,3.5)

func _spawn_float_text(text: String, color: Color) -> void:
	var zoom := maxf(0.05,get_global_transform_with_canvas().get_scale().x)
	var factor := clampf(get_viewport_rect().size.y/1080.0,0.85,2.5)/zoom
	var label := Label.new()
	label.text = text
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_font_size_override("font_size",21)
	label.add_theme_color_override("font_color",color)
	label.add_theme_color_override("font_outline_color",Color(0.01,0.02,0.03))
	label.add_theme_constant_override("outline_size",5)
	label.scale = Vector2.ONE*factor
	label.position = Vector2(-20*factor,-_sh-12*factor)
	label.z_index = 60
	add_child(label)
	var tween := create_tween()
	tween.tween_property(label,"position:y",label.position.y-30*factor,1.1)
	tween.parallel().tween_property(label,"modulate:a",0.0,0.65).set_delay(0.45)
	tween.tween_callback(label.queue_free)

func _body_height() -> float:
	# Terrain scale, independent of HUD size, window resolution and camera zoom.
	return cell_size.x * HUMAN_HEIGHT_PER_TILE * _visual_size_scale() * TOKEN_PRESENTATION_SCALE

func hit_test_screen(screen_point: Vector2) -> bool:
	if unit_id >= 1000 or int(unit_data.get("hp",0)) <= 0: return false
	var local := get_global_transform_with_canvas().affine_inverse()*screen_point
	var bounds := _art_rect
	if _hit_image != null and atlas == null:
		var used := _hit_image.get_used_rect()
		var image_size := Vector2(_hit_image.get_width(),_hit_image.get_height())
		bounds = Rect2(_art_rect.position+Vector2(used.position)/image_size*_art_rect.size,Vector2(used.size)/image_size*_art_rect.size)
	var zoom := maxf(0.05,get_global_transform_with_canvas().get_scale().x)
	var padding := 5.0*clampf(get_viewport_rect().size.y/1080.0,0.85,2.5)/zoom
	return bounds.grow(padding).has_point(local)

func _screen_pixel() -> Vector2:
	var zoom := get_global_transform_with_canvas().get_scale().abs()
	return Vector2(1.0/maxf(0.01,zoom.x),1.0/maxf(0.01,zoom.y))

func _visible_body_rect() -> Rect2:
	return Rect2(_art_rect.position+_active_bounds_uv.position*_art_rect.size,_active_bounds_uv.size*_art_rect.size)

func _health_bar_rect() -> Rect2:
	var pixel := _screen_pixel()
	var body := _visible_body_rect()
	var width := clampf(body.size.y/pixel.y*1.05,48,108)*pixel.x
	return Rect2(Vector2(body.get_center().x-width*0.5,body.position.y-14*pixel.y),Vector2(width,6*pixel.y))

func _health_segment_fills() -> Array[float]:
	var maximum := maxf(1,float(unit_data.get("max_hp",1)))
	var count := clampi(ceili(maximum/6.0),3,10)
	var fraction := clampf(float(unit_data.get("hp",0))/maximum,0,1)
	var result: Array[float] = []
	for i in range(count): result.append(clampf(fraction*count-i,0,1))
	return result

func _health_bevel(rect: Rect2,slant: float) -> PackedVector2Array:
	slant = minf(slant,rect.size.x*0.35)
	return PackedVector2Array([rect.position+Vector2(slant,0),Vector2(rect.end.x,rect.position.y),rect.end-Vector2(slant,0),Vector2(rect.position.x,rect.end.y)])

func _draw_segmented_health(color: Color) -> void:
	var pixel := _screen_pixel()
	var bar := _health_bar_rect()
	var fills := _health_segment_fills()
	var gap := 1.5*pixel.x
	var width := (bar.size.x-gap*(fills.size()-1))/fills.size()
	for i in range(fills.size()):
		var segment := Rect2(bar.position+Vector2(i*(width+gap),0),Vector2(width,bar.size.y))
		var shape := _health_bevel(segment,2*pixel.x)
		draw_colored_polygon(shape,Color(0.005,0.015,0.02,0.95))
		if fills[i] > 0:
			var fill := segment
			fill.size.x *= fills[i]
			draw_colored_polygon(_health_bevel(fill,2*pixel.x),color)
		shape.append(shape[0])
		draw_polyline(shape,Color(0.005,0.015,0.02,1),pixel.x,true)

func _measure_atlas_bounds(image: Image, frame_size: Vector2i) -> Dictionary:
	# Cache tiny normalized rectangles, not another copy of the full atlas.
	var result: Dictionary = {}
	if frame_size.x <= 0 or frame_size.y <= 0: return result
	var columns := image.get_width()/frame_size.x
	var rows := image.get_height()/frame_size.y
	for y in range(rows):
		for x in range(columns):
			var used := image.get_region(Rect2i(Vector2i(x,y)*frame_size,frame_size)).get_used_rect()
			result[y*columns+x] = Rect2(Vector2(used.position)/Vector2(frame_size),Vector2(used.size)/Vector2(frame_size))
	return result
