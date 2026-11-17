extends Node2D
## Re-layer surveyed baked art, never invent facades from roof/floor texture strips.
## The survey is a texture-space silhouette, not a 3D footprint/height survey.
var top := PackedVector2Array()
var ground := PackedVector2Array()
var uvs := PackedVector2Array()
var map_texture: Texture2D
var height := 0.0
var fade := false
var _bounds := Rect2()
var _alpha := 1.0

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR

func configure(wall: Dictionary, board, texture: Texture2D) -> void:
	map_texture=texture
	top.clear();ground.clear();uvs.clear()
	var raw: Array=wall.get("outline_uv",[])
	if raw.size()<3:return
	var points:=PackedVector2Array()
	var anchor:=Vector2(-INF,-INF)
	for pair: Array in raw:
		var uv:=Vector2(float(pair[0]),float(pair[1]))
		uvs.append(uv)
		var p: Vector2=board.uv_to_world(uv)
		points.append(p)
		if p.y>anchor.y:anchor=p
	position=anchor
	for p: Vector2 in points:
		ground.append(p-anchor)
		top.append(p-anchor)
	_bounds=Rect2(top[0],Vector2.ZERO)
	for p: Vector2 in top:_bounds=_bounds.expand(p)
	queue_redraw()

func update_occlusion(world_position: Vector2) -> void:
	update_occlusion_for_units([Rect2(world_position-Vector2(12,48),Vector2(24,48))])

func update_occlusion_for_units(bodies: Array[Rect2]) -> void:
	fade=false
	if top.size()<3:return
	for body: Rect2 in bodies:
		var local:=Rect2(body.position-position,body.size)
		if body.end.y>position.y+1 or not _bounds.intersects(local):continue
		var corners:=PackedVector2Array([local.position,Vector2(local.end.x,local.position.y),local.end,Vector2(local.position.x,local.end.y)])
		if not Geometry2D.intersect_polygons(top,corners).is_empty():
			fade=true;break

func _process(delta: float) -> void:
	_alpha=move_toward(_alpha,0.16 if fade else 1.0,delta*5)
	modulate.a=_alpha

func _draw() -> void:
	if top.size()<3:return
	if map_texture!=null:
		draw_polygon(top,PackedColorArray([Color.WHITE]),uvs,map_texture)
