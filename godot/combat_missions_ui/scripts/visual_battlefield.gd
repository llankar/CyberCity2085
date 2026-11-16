extends "res://scripts/battlefield.gd"
## Original tactical board and geometry APIs; presentation overrides only.
var quality := 2
var weather := "rain"
var _redraw_clock := 0.0

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	debug_walls_visible = false

func _process(delta: float) -> void:
	_elapsed += delta
	_redraw_clock += delta
	if _redraw_clock >= 1.0 / (30.0 if quality > 0 else 15.0):
		_redraw_clock = 0
		queue_redraw()

func _draw_vignette() -> void:
	pass

func _draw_grid_overlay() -> void:
	# No giant lattice over the scenery. Compact markers below retain real cell centers.
	pass

const MOVE_MARKER_SCALE := 0.42
const DESTINATION_SCALE := 0.46
const ROUTE_COLOR := Color(0.10, 0.95, 1.0)

func _screen_unit() -> float:
	return 1.0 / maxf(0.01, absf(get_global_transform_with_canvas().get_scale().x))

func _draw_range_highlights() -> void:
	var pixel := _screen_unit()
	for cell: Vector2i in move_range_cells:
		var corners := _iso_corners_inner(cell,MOVE_MARKER_SCALE)
		draw_colored_polygon(corners,Color(ROUTE_COLOR,0.045))
		corners.append(corners[0])
		draw_polyline(corners,Color(ROUTE_COLOR,0.40),1.2*pixel,true)
	for cell: Vector2i in attack_range_cells:
		draw_colored_polygon(_iso_corners_inner(cell,MOVE_MARKER_SCALE),Color(1,0.2,0.18,0.075))

func _route_preview_geometry() -> Dictionary:
	if path_cells.size() < 2: return {}
	var points := PackedVector2Array()
	for cell: Vector2i in path_cells: points.append(cell_to_world(cell))
	var center := points[-1]
	var direction := (center-points[-2]).normalized()
	var radius := 1.0 / (absf(direction.x)/(iso_tw*DESTINATION_SCALE)+absf(direction.y)/(iso_th*DESTINATION_SCALE))
	var tip := center-direction*radius
	points[-1] = tip
	var pixel := _screen_unit()
	var base := tip-direction*12.0*pixel
	var wing := direction.orthogonal()*5.5*pixel
	return {"points":points,"arrow":PackedVector2Array([tip,base+wing,base-wing]),"cost":path_cells.size()-1}

func _draw_path_preview() -> void:
	var preview := _route_preview_geometry()
	if preview.is_empty(): return
	var pixel := _screen_unit()
	var points: PackedVector2Array = preview["points"]
	draw_polyline(points,Color(ROUTE_COLOR,0.07),14*pixel,true)
	draw_polyline(points,Color(ROUTE_COLOR,0.16),8*pixel,true)
	draw_polyline(points,ROUTE_COLOR,3*pixel,true)
	for i in range(1,points.size()-1):
		draw_set_transform(points[i],0,Vector2(1,0.55))
		draw_circle(Vector2.ZERO,6.5*pixel,ROUTE_COLOR)
	draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
	draw_colored_polygon(preview["arrow"],ROUTE_COLOR)
	var dest := _iso_corners_inner(path_cells[-1],DESTINATION_SCALE)
	draw_colored_polygon(dest,Color(ROUTE_COLOR,0.12))
	dest.append(dest[0])
	draw_polyline(dest,Color(ROUTE_COLOR,0.10),10*pixel,true)
	draw_polyline(dest,Color(0.5,1,1),2*pixel,true)
	var text := "%d PA" % int(preview["cost"])
	var font_size := maxi(1,roundi(18*pixel))
	var width := maxf(62*pixel,ThemeDB.fallback_font.get_string_size(text,HORIZONTAL_ALIGNMENT_LEFT,-1,font_size).x+20*pixel)
	var top := cell_to_world(path_cells[-1])-Vector2(0,iso_th*DESTINATION_SCALE)
	var rect := Rect2(top-Vector2(width*0.5,40*pixel),Vector2(width,30*pixel))
	var cut := 5*pixel
	var badge := PackedVector2Array([rect.position+Vector2(cut,0),Vector2(rect.end.x-cut,rect.position.y),Vector2(rect.end.x,rect.position.y+cut),rect.end-Vector2(0,cut),rect.end-Vector2(cut,0),Vector2(rect.position.x+cut,rect.end.y),Vector2(rect.position.x,rect.end.y-cut),rect.position+Vector2(0,cut)])
	draw_colored_polygon(badge,Color(0.01,0.05,0.06,0.95))
	badge.append(badge[0])
	draw_polyline(badge,ROUTE_COLOR,1.5*pixel,true)
	draw_string(ThemeDB.fallback_font,rect.position+Vector2(10*pixel,21*pixel),text,HORIZONTAL_ALIGNMENT_LEFT,-1,font_size,ROUTE_COLOR)

func _draw_hover() -> void:
	if hovered_cell.x < 0: return
	if not path_cells.is_empty() and hovered_cell == path_cells[-1]: return
	var corners := _iso_corners_inner(hovered_cell,DESTINATION_SCALE)
	corners.append(corners[0])
	draw_polyline(corners,Color(0.7,1,1,0.85),2*_screen_unit(),true)

func _draw_atmosphere() -> void:
	if quality == 0: return
	var count := 90 if quality == 2 else 32
	for i in range(count):
		var u := fmod(float(i)*0.61803398875,1.0)
		var v := fmod(float(i)*0.754877666 + _elapsed*(0.085 if weather == "rain" else 0.008),1.0)
		var p := iso_origin + Vector2((u*GRID_COLS-v*GRID_ROWS)*iso_tw,(u*GRID_COLS+v*GRID_ROWS)*iso_th)
		if weather == "rain":
			draw_line(p,p+Vector2(-3,14),Color(0.5,0.8,1,0.18),0.8,true)
		elif weather == "dust":
			draw_circle(p,1.2,Color(0.8,0.65,0.4,0.15))
		elif weather == "interior":
			draw_circle(p,0.7,Color(0.3,0.8,1,0.1))
