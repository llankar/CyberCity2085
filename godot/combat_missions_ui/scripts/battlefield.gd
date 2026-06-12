extends Node2D
class_name Battlefield
## Draws the battle map in isometric 3D perspective, plus tactical grid, cover
## nodes, objective marker, and all cell-highlight overlays.
## Also owns AStar2D pathfinding and Bresenham line-of-sight checks.
## Mouse input is handled here and forwarded via CombatSignals.

# ── Layout (must match HudController) ────────────────────────────────────────
const GRID_COLS    := 40
const GRID_ROWS    := 28
const TOP_BAR_H    : float = 44.0
const RIGHT_PANEL_W: float = 340.0
const STRIP_H      : float = 158.0
const LEFT_MARGIN  : float = 70.0

# ── Palette ───────────────────────────────────────────────────────────────────
const NEON       := Color(0.10, 0.95, 0.72, 1.0)
const PLAYER_COL := Color(0.10, 0.95, 0.72, 1.0)
const WARN       := Color(1.00, 0.72, 0.22, 1.0)
const MOVE_RANGE_SCALE := 0.50
const MOVE_RANGE_STEP_SCALE := 0.56

# ── State ─────────────────────────────────────────────────────────────────────
var viewport_size   : Vector2 = Vector2(1280.0, 720.0)
var battlefield_rect: Rect2   = Rect2()
var map_texture     : Texture2D = null
var cover_nodes     : Array[Dictionary] = []
var objective_cell  : Vector2i = Vector2i(6, 3)

var move_range_cells  : Array[Vector2i] = []
var move_range_anchor : Vector2i = Vector2i(-1, -1)
var attack_range_cells: Array[Vector2i] = []
var path_cells        : Array[Vector2i] = []
var hovered_cell      : Vector2i = Vector2i(-1, -1)
var selected_cell     : Vector2i = Vector2i(-1, -1)

var _elapsed    : float = 0.0
var _astar      := AStar2D.new()
var _blocked    : Array[Vector2i] = []
var pan_lock    : bool = false   # set by CombatRoot while camera pan is active

# ── Isometric parameters ──────────────────────────────────────────────────────
# iso_origin  = screen position of the TOP vertex of the diamond grid (tile 0,0 top)
# iso_tw      = half tile width   (moving +1 col → screen.x += iso_tw, screen.y += iso_th)
# iso_th      = half tile height  (standard 2:1 ratio: iso_th = iso_tw * 0.5)
var iso_origin : Vector2 = Vector2.ZERO
var iso_tw     : float   = 40.0
var iso_th     : float   = 20.0

# ─────────────────────────────────────────────────────────────────────────────

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	set_process(true)

func _process(delta: float) -> void:
	_elapsed += delta
	queue_redraw()

func configure(vp_size: Vector2, map_tex: Texture2D,
			   covers: Array[Dictionary], obj_cell: Vector2i) -> void:
	viewport_size  = vp_size
	map_texture    = map_tex
	cover_nodes    = covers
	objective_cell = obj_cell
	_compute_rect()
	_rebuild_astar()
	queue_redraw()

func resize(new_vp_size: Vector2) -> void:
	viewport_size = new_vp_size
	_compute_rect()
	queue_redraw()

# ── Layout ────────────────────────────────────────────────────────────────────

func _compute_rect() -> void:
	var bw := maxf(300.0, viewport_size.x - RIGHT_PANEL_W - LEFT_MARGIN - 10.0)
	var bh := maxf(200.0, viewport_size.y - TOP_BAR_H   - STRIP_H     - 20.0)
	battlefield_rect = Rect2(LEFT_MARGIN, TOP_BAR_H + 8.0, bw, bh)

	# iso_tw fills the available world width — grid always covers the play area.
	# Visual tile size on screen is controlled by the camera zoom, not by this value.
	iso_tw = bw / float(GRID_COLS + GRID_ROWS)
	iso_th = iso_tw * 0.5          # classic 2:1 isometric ratio

	# Origin = top vertex of the diamond grid
	iso_origin = Vector2(
		battlefield_rect.position.x + float(GRID_ROWS) * iso_tw,
		battlefield_rect.position.y + 4.0
	)

# ── Coordinate transforms ─────────────────────────────────────────────────────

func cell_to_world(cell: Vector2i) -> Vector2:
	## Returns the screen-space CENTER of an isometric tile.
	return iso_origin + Vector2(
		float(cell.x - cell.y) * iso_tw,
		float(cell.x + cell.y) * iso_th + iso_th   # +iso_th shifts to diamond centre
	)

func world_to_cell(pos: Vector2) -> Vector2i:
	## Inverse isometric transform — maps a screen point to the nearest tile.
	var local := pos - iso_origin
	var col   := (local.x / iso_tw + local.y / iso_th) * 0.5
	var row   := (local.y / iso_th - local.x / iso_tw) * 0.5
	return Vector2i(
		clampi(int(floor(col)), 0, GRID_COLS - 1),
		clampi(int(floor(row)), 0, GRID_ROWS - 1)
	)

func _iso_corners(cell: Vector2i) -> PackedVector2Array:
	## Returns the 4 screen-space corners of a tile diamond [top, right, bot, left].
	var top  := iso_origin + Vector2(float(cell.x - cell.y) * iso_tw,
									 float(cell.x + cell.y) * iso_th)
	return PackedVector2Array([
		top,                                      # top
		top + Vector2( iso_tw,  iso_th),          # right
		top + Vector2(    0.0, iso_th * 2.0),     # bottom
		top + Vector2(-iso_tw,  iso_th),          # left
	])

func _iso_corners_inner(cell: Vector2i, scale_f: float) -> PackedVector2Array:
	## Like _iso_corners but scaled toward the tile centre by scale_f (0..1).
	## Used for range highlights so adjacent cells stay visually separate.
	var center  := cell_to_world(cell)
	var corners := _iso_corners(cell)
	var result  := PackedVector2Array()
	for c: Vector2 in corners:
		result.append(center + (c - center) * scale_f)
	return result

func _move_highlight_corners(cell: Vector2i) -> PackedVector2Array:
	## Keeps move diamonds the same size while drawing them on a tighter
	## preview lattice, so compact highlights do not leave full-cell gutters.
	var corners := _iso_corners_inner(cell, MOVE_RANGE_SCALE)
	if move_range_anchor.x < 0:
		return corners
	var actual_center  := cell_to_world(cell)
	var anchor_center  := cell_to_world(move_range_anchor)
	var preview_center := anchor_center + (actual_center - anchor_center) * MOVE_RANGE_STEP_SCALE
	var delta := preview_center - actual_center
	var result := PackedVector2Array()
	for c: Vector2 in corners:
		result.append(c + delta)
	return result

# ── Range / path highlighting ─────────────────────────────────────────────────

func show_move_range(cells: Array[Vector2i], anchor_cell: Vector2i = Vector2i(-1, -1)) -> void:
	move_range_cells   = cells
	move_range_anchor  = anchor_cell
	attack_range_cells = []
	path_cells         = []
	queue_redraw()

func show_attack_range(cells: Array[Vector2i]) -> void:
	attack_range_cells = cells
	move_range_cells   = []
	move_range_anchor  = Vector2i(-1, -1)
	path_cells         = []
	queue_redraw()

func show_path(cells: Array[Vector2i]) -> void:
	path_cells = cells
	queue_redraw()

func clear_highlights() -> void:
	move_range_cells   = []
	move_range_anchor  = Vector2i(-1, -1)
	attack_range_cells = []
	path_cells         = []
	selected_cell      = Vector2i(-1, -1)
	queue_redraw()

# ── AStar2D pathfinding ───────────────────────────────────────────────────────

func _cell_id(cell: Vector2i) -> int:
	return cell.y * GRID_COLS + cell.x

func set_blocked(cells: Array[Vector2i]) -> void:
	_blocked = cells
	_rebuild_astar()

func _rebuild_astar() -> void:
	_astar.clear()
	for y in range(GRID_ROWS):
		for x in range(GRID_COLS):
			_astar.add_point(_cell_id(Vector2i(x, y)), Vector2(float(x), float(y)))
	for y in range(GRID_ROWS):
		for x in range(GRID_COLS):
			var cell := Vector2i(x, y)
			if _blocked.has(cell):
				_astar.set_point_disabled(_cell_id(cell), true)
				continue
			for nb: Vector2i in [Vector2i(x+1,y), Vector2i(x-1,y),
								  Vector2i(x,y+1), Vector2i(x,y-1)]:
				if nb.x < 0 or nb.x >= GRID_COLS or nb.y < 0 or nb.y >= GRID_ROWS:
					continue
				if not _blocked.has(nb):
					var a := _cell_id(cell)
					var b := _cell_id(nb)
					if not _astar.are_points_connected(a, b):
						_astar.connect_points(a, b)

func find_path(from_cell: Vector2i, to_cell: Vector2i) -> Array[Vector2i]:
	var raw := _astar.get_point_path(_cell_id(from_cell), _cell_id(to_cell))
	var result: Array[Vector2i] = []
	for p: Vector2 in raw:
		result.append(Vector2i(int(p.x), int(p.y)))
	return result

func reachable_cells(from_cell: Vector2i, max_steps: int) -> Array[Vector2i]:
	var result : Array[Vector2i] = []
	var visited: Dictionary       = {}
	var queue  : Array            = [[from_cell, 0]]
	visited[from_cell] = true
	while not queue.is_empty():
		var item : Array    = queue.pop_front()
		var cell : Vector2i = item[0]
		var dist : int      = item[1]
		if cell != from_cell:
			result.append(cell)
		if dist >= max_steps:
			continue
		for nb: Vector2i in [Vector2i(cell.x+1,cell.y), Vector2i(cell.x-1,cell.y),
							  Vector2i(cell.x,cell.y+1), Vector2i(cell.x,cell.y-1)]:
			if nb.x < 0 or nb.x >= GRID_COLS or nb.y < 0 or nb.y >= GRID_ROWS:
				continue
			if visited.has(nb) or _blocked.has(nb):
				continue
			visited[nb] = true
			queue.append([nb, dist + 1])
	return result

# ── Line of Sight ─────────────────────────────────────────────────────────────

func has_los(from_cell: Vector2i, to_cell: Vector2i,
			 high_cover_cells: Array[Vector2i]) -> bool:
	var dx  := absi(to_cell.x - from_cell.x)
	var dy  := absi(to_cell.y - from_cell.y)
	var sx  := signi(to_cell.x - from_cell.x)
	var sy  := signi(to_cell.y - from_cell.y)
	var x   := from_cell.x
	var y   := from_cell.y
	var err := dx - dy
	while x != to_cell.x or y != to_cell.y:
		var e2 := err * 2
		if e2 > -dy: err -= dy; x += sx
		if e2 <  dx: err += dx; y += sy
		var cur := Vector2i(x, y)
		if cur != to_cell and high_cover_cells.has(cur):
			return false
	return true

# ── Input ─────────────────────────────────────────────────────────────────────

func _unhandled_input(event: InputEvent) -> void:
	if pan_lock: return
	# Camera2D is active: convert viewport pixels → canvas/world coordinates.
	var inv := get_viewport().get_canvas_transform().affine_inverse()
	if event is InputEventMouseMotion:
		var pos := inv * (event as InputEventMouseMotion).position
		if battlefield_rect.has_point(pos):
			var cell := world_to_cell(pos)
			if cell != hovered_cell:
				hovered_cell = cell
				CombatSignals.cell_hovered.emit(cell)
				queue_redraw()
		else:
			if hovered_cell != Vector2i(-1, -1):
				hovered_cell = Vector2i(-1, -1)
				queue_redraw()
	elif event is InputEventMouseButton:
		var mbe := event as InputEventMouseButton
		if not mbe.pressed and mbe.button_index == MOUSE_BUTTON_LEFT:
			var pos := inv * mbe.position
			if battlefield_rect.has_point(pos):
				selected_cell = world_to_cell(pos)
				CombatSignals.cell_clicked.emit(selected_cell)
				queue_redraw()

# ── Drawing ───────────────────────────────────────────────────────────────────

func _draw() -> void:
	_draw_map()
	_draw_atmosphere()
	_draw_range_highlights()
	_draw_grid_overlay()
	_draw_vignette()
	_draw_cover_nodes()
	_draw_objective()
	_draw_path_preview()
	_draw_hover()

# ── Map ───────────────────────────────────────────────────────────────────────

func _draw_map() -> void:
	# Full-grid diamond corners (outer edges of the entire grid)
	var top  := iso_origin
	var rght := iso_origin + Vector2( float(GRID_COLS) * iso_tw,  float(GRID_COLS) * iso_th)
	var bot  := iso_origin + Vector2( float(GRID_COLS - GRID_ROWS) * iso_tw,
									  float(GRID_COLS + GRID_ROWS) * iso_th)
	var left := iso_origin + Vector2(-float(GRID_ROWS) * iso_tw,  float(GRID_ROWS) * iso_th)

	var quad := PackedVector2Array([top, rght, bot, left])

	if map_texture != null:
		# Map the rectangular texture onto the isometric ground plane.
		# UVs: top→(0,0)  right→(1,0)  bottom→(1,1)  left→(0,1)
		draw_polygon(quad,
				PackedColorArray([Color(0.88, 0.88, 0.88, 1.0),
								  Color(0.88, 0.88, 0.88, 1.0),
								  Color(0.88, 0.88, 0.88, 1.0),
								  Color(0.88, 0.88, 0.88, 1.0)]),
				PackedVector2Array([Vector2(0,0), Vector2(1,0), Vector2(1,1), Vector2(0,1)]),
				map_texture)
	else:
		# Fallback: solid dark diamond
		draw_polygon(quad, PackedColorArray([Color(0.03, 0.08, 0.10, 0.95)]))

# ── Atmosphere ────────────────────────────────────────────────────────────────

func _draw_atmosphere() -> void:
	var cx := cell_to_world(Vector2i(GRID_COLS / 2, GRID_ROWS / 2))
	var bw := iso_tw * float(GRID_COLS) * 1.5
	# Cool blue tactical spotlight
	draw_circle(cx + Vector2(-iso_tw * 1.5, -iso_th * 2.0), bw * 0.55, Color(0.22, 0.62, 0.95, 0.036))
	draw_circle(cx + Vector2(-iso_tw * 1.5, -iso_th * 2.0), bw * 0.28, Color(0.30, 0.72, 1.00, 0.042))
	draw_circle(cx + Vector2(-iso_tw * 1.5, -iso_th * 2.0), bw * 0.12, Color(0.48, 0.88, 1.00, 0.038))
	# Warm industrial accent
	draw_circle(cx + Vector2( iso_tw * 3.0,  iso_th * 2.5), bw * 0.38, Color(0.95, 0.74, 0.28, 0.030))
	draw_circle(cx + Vector2( iso_tw * 3.0,  iso_th * 2.5), bw * 0.16, Color(1.00, 0.88, 0.48, 0.026))
	# Secondary cold fill
	draw_circle(cx + Vector2(-iso_tw * 3.0,  iso_th * 3.0), bw * 0.30, Color(0.18, 0.55, 0.82, 0.026))

# ── Range highlights ─────────────────────────────────────────────────────────

func _draw_range_highlights() -> void:
	for cell: Vector2i in move_range_cells:
		var c := _move_highlight_corners(cell)
		draw_polygon(c, PackedColorArray([Color(0.10, 0.95, 0.72, 0.35)]))
		draw_polyline(PackedVector2Array([c[0], c[1], c[2], c[3], c[0]]),
					  Color(0.10, 0.95, 0.72, 0.70), 1.0)
	for cell: Vector2i in attack_range_cells:
		var c := _iso_corners(cell)
		draw_polygon(c, PackedColorArray([Color(1.00, 0.34, 0.30, 0.35)]))
		draw_polyline(PackedVector2Array([c[0], c[1], c[2], c[3], c[0]]),
					  Color(1.00, 0.34, 0.30, 0.70), 1.0)

# ── Grid ─────────────────────────────────────────────────────────────────────

func _draw_grid_overlay() -> void:
	# Dark tint over the full diamond
	var top  := iso_origin
	var rght := iso_origin + Vector2( float(GRID_COLS) * iso_tw,  float(GRID_COLS) * iso_th)
	var bot  := iso_origin + Vector2( float(GRID_COLS - GRID_ROWS) * iso_tw,
									  float(GRID_COLS + GRID_ROWS) * iso_th)
	var left := iso_origin + Vector2(-float(GRID_ROWS) * iso_tw,  float(GRID_ROWS) * iso_th)
	draw_polygon(PackedVector2Array([top, rght, bot, left]),
				 PackedColorArray([Color(0.0, 0.0, 0.0, 0.12)]))

	# Individual tile diamonds
	var gc := Color(0.12, 0.45, 0.38, 0.22)
	for y in range(GRID_ROWS):
		for x in range(GRID_COLS):
			var d := _iso_corners(Vector2i(x, y))
			draw_polyline(PackedVector2Array([d[0], d[1], d[2], d[3], d[0]]), gc, 0.8)

	# Neon border of full grid diamond
	draw_polyline(PackedVector2Array([top, rght, bot, left, top]), NEON, 1.5)

# ── Vignette ─────────────────────────────────────────────────────────────────

func _draw_vignette() -> void:
	var r  := battlefield_rect
	var d  := minf(r.size.x, r.size.y) * 0.13
	var vc := Color(0.0, 0.0, 0.0, 0.22)
	draw_rect(Rect2(r.position.x, r.position.y,          r.size.x, d),    vc, true)
	draw_rect(Rect2(r.position.x, r.end.y - d,           r.size.x, d),    vc, true)
	draw_rect(Rect2(r.position.x, r.position.y,          d,        r.size.y), vc, true)
	draw_rect(Rect2(r.end.x - d,  r.position.y,          d,        r.size.y), vc, true)

# ── Cover nodes ───────────────────────────────────────────────────────────────

func _draw_cover_nodes() -> void:
	for node: Dictionary in cover_nodes:
		var cell := node.get("cell", Vector2i.ZERO) as Vector2i
		var high := bool(node.get("high", false))
		var d    := _iso_corners_inner(cell, 0.25)
		var al   := 0.75 if high else 0.50
		var col  := Color(0.72, 0.88, 0.32, al)
		draw_polygon(d, PackedColorArray([Color(0.72, 0.88, 0.32, 0.18)]))
		draw_polyline(PackedVector2Array([d[0], d[1], d[2], d[3], d[0]]), col, 1.5)
		var center := cell_to_world(cell)
		draw_string(ThemeDB.fallback_font,
				center + Vector2(-4.0, 5.0),
				"H" if high else "L", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, col)

# ── Objective ─────────────────────────────────────────────────────────────────

func _draw_objective() -> void:
	var center := cell_to_world(objective_cell)
	var pulse  := 0.70 + 0.30 * sin(_elapsed * 2.2)
	var ring   := 14.0 + 4.0 * pulse
	draw_arc(center, ring, 0.0, TAU, 48, PLAYER_COL, 2.0)
	draw_rect(Rect2(center.x - 7, center.y - 7, 14, 14),
			  Color(PLAYER_COL.r, PLAYER_COL.g, PLAYER_COL.b, 0.18), true)
	draw_rect(Rect2(center.x - 9, center.y - 9, 18, 18), PLAYER_COL, false, 1.5)
	draw_string(ThemeDB.fallback_font, center + Vector2(-9, -20),
			"OBJ", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, PLAYER_COL)

# ── Path preview ──────────────────────────────────────────────────────────────

func _draw_path_preview() -> void:
	if path_cells.size() < 2:
		return
	var prev := cell_to_world(path_cells[0])
	for i in range(1, path_cells.size()):
		var next := cell_to_world(path_cells[i])
		draw_dashed_line(prev, next, Color(0.10, 0.95, 0.72, 0.72), 2.0, 9.0)
		draw_circle(next, 3.0, Color(0.10, 0.95, 0.72, 0.55))
		prev = next

# ── Hover ─────────────────────────────────────────────────────────────────────

func _draw_hover() -> void:
	if hovered_cell.x < 0:
		return
	var d := _iso_corners_inner(hovered_cell, 0.20)
	draw_polygon(d, PackedColorArray([Color(1.0, 1.0, 1.0, 0.11)]))
	draw_polyline(PackedVector2Array([d[0], d[1], d[2], d[3], d[0]]),
				  Color(1.0, 1.0, 1.0, 0.50), 1.5)
