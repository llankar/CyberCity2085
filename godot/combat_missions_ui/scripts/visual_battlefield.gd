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

func _draw_range_highlights() -> void:
	for cell: Vector2i in move_range_cells:
		var corners := _iso_corners_inner(cell,0.42)
		draw_colored_polygon(corners,Color(0.1,0.9,0.95,0.07))
		corners.append(corners[0])
		draw_polyline(corners,Color(0.1,0.85,0.95,0.4),1.0,true)
	for cell: Vector2i in attack_range_cells:
		draw_colored_polygon(_iso_corners_inner(cell,0.42),Color(1,0.2,0.18,0.075))

func _draw_path_preview() -> void:
	if path_cells.size() < 2: return
	var points := PackedVector2Array()
	for cell: Vector2i in path_cells: points.append(cell_to_world(cell))
	draw_polyline(points,Color(0.05,0.95,1,0.12),10,true)
	draw_polyline(points,Color(0.1,0.95,1,0.95),2.6,true)
	for p: Vector2 in points: draw_circle(p,3,Color(0.1,0.95,1))
	var dest := _iso_corners_inner(path_cells[-1],0.46)
	dest.append(dest[0])
	draw_polyline(dest,Color(0.1,0.95,1),2,true)
	var label := points[-1]+Vector2(10,-14)
	draw_rect(Rect2(label-Vector2(4,16),Vector2(64,23)),Color(0.01,0.06,0.08,0.94))
	draw_string(ThemeDB.fallback_font,label,"%d PA" % (path_cells.size()-1),HORIZONTAL_ALIGNMENT_LEFT,-1,14,NEON)

func _draw_hover() -> void:
	if hovered_cell.x < 0: return
	var corners := _iso_corners_inner(hovered_cell,0.46)
	corners.append(corners[0])
	draw_polyline(corners,Color(0.7,1,1,0.7),1.5,true)

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
