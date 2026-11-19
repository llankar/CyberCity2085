extends "res://scripts/battlefield.gd"
## Original tactical board and geometry APIs; presentation overrides only.
var top_down := true
var human_height_ratio := .035
var quality := 2
var weather := "rain"
var _depth_props: Array[Node2D] = []
var _redraw_clock := 0.0

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
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
		draw_colored_polygon(corners,Color(ROUTE_COLOR,0.16))
		corners.append(corners[0])
		draw_polyline(corners,Color(.005,.02,.025,.70),4.0*pixel,true)
		draw_polyline(corners,Color(ROUTE_COLOR,0.85),2.0*pixel,true)
	for cell: Vector2i in attack_range_cells:
		draw_colored_polygon(_iso_corners_inner(cell,MOVE_MARKER_SCALE),Color(1,0.2,0.18,0.075))

func _route_preview_geometry() -> Dictionary:
	if path_cells.size() < 2: return {}
	var points := PackedVector2Array()
	for cell: Vector2i in path_cells: points.append(cell_to_world(cell))
	var center := points[-1]
	var direction := (center-points[-2]).normalized()
	var radius := 1.0 / (absf(direction.x)/(iso_tw*DESTINATION_SCALE)+absf(direction.y)/(iso_th*DESTINATION_SCALE))
	if top_down:radius=minf(iso_tw*DESTINATION_SCALE/maxf(.0001,absf(direction.x)),iso_th*DESTINATION_SCALE/maxf(.0001,absf(direction.y)))
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
	if quality > 0:
		# Moving light beads follow the actual route, without inventing waypoints.
		for segment in range(points.size()-1):
			var travel := fmod(_elapsed*1.15-float(segment)*.12+10.0,1.0)
			var bead := points[segment].lerp(points[segment+1],travel)
			draw_circle(bead,4.5*pixel,Color(ROUTE_COLOR,.13))
			draw_circle(bead,1.8*pixel,Color(.78,1,1,.85))
	for i in range(1,points.size()-1):
		draw_set_transform(points[i],0,Vector2(1,0.55))
		draw_circle(Vector2.ZERO,6.5*pixel,ROUTE_COLOR)
	draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
	draw_colored_polygon(preview["arrow"],ROUTE_COLOR)
	var dest := _iso_corners_inner(path_cells[-1],DESTINATION_SCALE)
	draw_colored_polygon(dest,Color(ROUTE_COLOR,0.10+sin(_elapsed*3.5)*.025))
	dest.append(dest[0])
	draw_polyline(dest,Color(ROUTE_COLOR,0.10),10*pixel,true)
	draw_polyline(dest,Color(0.5,1,1),2*pixel,true)
	var text := "%d AP" % int(preview["cost"])
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
		var p := uv_to_world(Vector2(u,v))
		if weather == "rain":
			draw_line(p,p+Vector2(-3,14),Color(0.5,0.8,1,0.18),0.8,true)
		elif weather == "dust":
			draw_circle(p,1.2,Color(0.8,0.65,0.4,0.15))
		elif weather == "interior":
			draw_circle(p,0.7,Color(0.3,0.8,1,0.1))

# Visual 2.1: the catalogue images already contain isometric architecture.
# Their surveys explicitly use texture_top_left coordinates. Map that same UV
# plane without a second shear; tactical cells/A*/LOS remain the original IDs.
var source_rect := Rect2()
var _row_scale := 1.0
var _u_axis := Vector2.ZERO
var _v_axis := Vector2.ZERO

func _compute_rect() -> void:
	if top_down:
		var width := maxf(300.0,viewport_size.x-LEFT_MARGIN*2.0)
		var ratio := float(map_texture.get_height())/float(map_texture.get_width()) if map_texture!=null else 9.0/16.0
		iso_origin=Vector2(LEFT_MARGIN,TOP_BAR_H+8)
		_u_axis=Vector2(width,0)
		_v_axis=Vector2(0,width*ratio)
		_row_scale=float(GRID_COLS)*ratio/float(GRID_ROWS)
		iso_tw=width/float(GRID_COLS)*.5
		iso_th=width*ratio/float(GRID_ROWS)*.5
		source_rect=Rect2(iso_origin,Vector2(width,width*ratio))
		battlefield_rect=source_rect
		return
	# Calibrate the two isometric axes to actual source pixels, not 40:28 by fiat.
	# Equal source-pixel distances have equal projected scale on either axis.
	var width := maxf(300.0,viewport_size.x-LEFT_MARGIN*2.0)
	var ratio := float(map_texture.get_height())/float(map_texture.get_width()) if map_texture!=null else 9.0/16.0
	_row_scale=float(GRID_COLS)*ratio/float(GRID_ROWS)
	iso_tw=width/(float(GRID_COLS)+float(GRID_ROWS)*_row_scale)
	iso_th=iso_tw*.5
	iso_origin=Vector2(LEFT_MARGIN+float(GRID_ROWS)*_row_scale*iso_tw,TOP_BAR_H+8)
	_u_axis=Vector2(GRID_COLS*iso_tw,GRID_COLS*iso_th)
	_v_axis=Vector2(-GRID_ROWS*_row_scale*iso_tw,GRID_ROWS*_row_scale*iso_th)
	source_rect=Rect2(Vector2(LEFT_MARGIN,TOP_BAR_H+8),Vector2(width,width*.5))
	battlefield_rect=source_rect

func uv_to_world(uv: Vector2) -> Vector2:
	return iso_origin+uv.x*_u_axis+uv.y*_v_axis

func cell_to_world(cell: Vector2i) -> Vector2:
	return uv_to_world((Vector2(cell)+Vector2(.5,.5))/Vector2(GRID_COLS,GRID_ROWS))

func world_to_cell(point: Vector2) -> Vector2i:
	var local:=point-iso_origin
	if top_down:
		return Vector2i(clampi(floori(local.x/_u_axis.x*GRID_COLS),0,GRID_COLS-1),clampi(floori(local.y/_v_axis.y*GRID_ROWS),0,GRID_ROWS-1))
	var column: float=(local.x/iso_tw+local.y/iso_th)*.5
	var row: float=(local.y/iso_th-local.x/iso_tw)*.5/_row_scale
	return Vector2i(clampi(floori(column),0,GRID_COLS-1),clampi(floori(row),0,GRID_ROWS-1))

func _iso_corners(cell: Vector2i) -> PackedVector2Array:
	if top_down:
		var uv := Vector2(cell)/Vector2(GRID_COLS,GRID_ROWS)
		var step := Vector2.ONE/Vector2(GRID_COLS,GRID_ROWS)
		return PackedVector2Array([uv_to_world(uv),uv_to_world(uv+Vector2(step.x,0)),uv_to_world(uv+step),uv_to_world(uv+Vector2(0,step.y))])
	var center:=cell_to_world(cell)
	return PackedVector2Array([center+Vector2(0,-iso_th),center+Vector2(iso_tw,0),center+Vector2(0,iso_th),center+Vector2(-iso_tw,0)])

func _draw_map() -> void:
	var quad:=PackedVector2Array([uv_to_world(Vector2.ZERO),uv_to_world(Vector2(1,0)),uv_to_world(Vector2.ONE),uv_to_world(Vector2(0,1))])
	if map_texture!=null:draw_polygon(quad,PackedColorArray([Color.WHITE]),PackedVector2Array([Vector2.ZERO,Vector2(1,0),Vector2.ONE,Vector2(0,1)]),map_texture)
	else:draw_colored_polygon(quad,Color(.025,.055,.065))
	for prop: Node2D in _depth_props:
		if is_instance_valid(prop) and prop.visible: prop.draw_ground(self,quality)

func _draw_cover_nodes() -> void:
	var seen: Dictionary={}
	for cover: Dictionary in cover_nodes:
		if bool(cover.get("solid",false)):
			if not debug_walls_visible:continue
			var id:=str(cover.get("wall_id",""))
			if seen.has(id):continue
			seen[id]=true
			var polygon:=PackedVector2Array()
			for uv: Array in cover.get("outline_uv",[]):polygon.append(uv_to_world(Vector2(uv[0],uv[1])))
			if polygon.size()<3:continue
			draw_colored_polygon(polygon,Color(1,.1,.5,.22))
			polygon.append(polygon[0]);draw_polyline(polygon,Color(1,.8,.15),2*_screen_unit(),true)
		else:
			var center:=cell_to_world(cover.get("cell",Vector2i.ZERO))
			var pixel:=_screen_unit()
			draw_arc(center,13*pixel,PI,TAU,12,Color(.3,.9,1,.7),2*pixel,true)
			draw_line(center-Vector2(9,0)*pixel,center+Vector2(9,0)*pixel,Color(.3,.9,1,.7),2*pixel,true)

func _draw_objective() -> void:
	var center:=cell_to_world(objective_cell)
	var pixel:=_screen_unit()
	var ring:=_iso_corners_inner(objective_cell,.62)
	draw_colored_polygon(ring,Color(1,.72,.18,.10))
	ring.append(ring[0])
	draw_polyline(ring,Color(1,.72,.18,.12),8*pixel,true)
	draw_polyline(ring,Color(1,.8,.3),2*pixel,true)
	draw_line(center-Vector2(0,8*pixel),center-Vector2(0,35*pixel),Color(1,.72,.18,.8),2*pixel,true)
	draw_string(ThemeDB.fallback_font,center+Vector2(9,-24)*pixel,"OBJ",HORIZONTAL_ALIGNMENT_LEFT,-1,maxi(1,roundi(14*pixel)),Color(1,.8,.3))

func set_depth_props(props: Array[Node2D]) -> void:
	_depth_props=props.duplicate()
	queue_redraw()

func token_terrain_scale() -> float:
	# Presentation only: never rescale cells, PA costs, pathfinding or LOS.
	if not top_down:return 1.0
	return source_rect.size.x*human_height_ratio/maxf(.001,iso_tw*2.0*.70*1.10)
