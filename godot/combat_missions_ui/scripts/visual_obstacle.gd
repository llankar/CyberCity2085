extends Node2D
## Survey-aligned 2.5D props, with an exact flat 2.2 fallback.
## Facades use independent repeating materials, never stretched roof pixels.
var top := PackedVector2Array()
var ground := PackedVector2Array()
var uvs := PackedVector2Array()
var map_texture: Texture2D
var height := 0.0
var fade := false
var _bounds := Rect2()
var _alpha := 1.0
var parts: Array[Dictionary] = []
var floor: Dictionary = {}
var _occluders: Array[PackedVector2Array] = []
var _shadow_polygons: Array[PackedVector2Array] = []
var _floor_uvs := PackedVector2Array()

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED

func configure(wall: Dictionary, board, texture: Texture2D, depth = null) -> void:
	map_texture=texture
	parts.clear();floor.clear();_occluders.clear()
	height=0
	_shadow_polygons.clear();_floor_uvs.clear()
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
	if depth != null:
		var volume: Dictionary = depth.build_volume(wall,uvs,position)
		height=float(volume.height)
		parts.assign(volume.parts)
		floor=volume.floor
		for i in range(top.size()): top[i]-=Vector2(0,height)
	if parts.is_empty(): _occluders.append(top)
	else:
		for part: Dictionary in parts:
			_occluders.append(part.cap)
			for face: Dictionary in part.faces: _occluders.append(face.points)
	_bounds=Rect2(ground[0],Vector2.ZERO)
	for polygon: PackedVector2Array in _occluders:
		for p: Vector2 in polygon: _bounds=_bounds.expand(p)
	if height>0:
		var polygon := PackedVector2Array()
		for point: Vector2 in ground:polygon.append(point+position)
		var offset := Vector2(height*.24,height*.12)
		for layer in range(3,0,-1):
			for shadow: PackedVector2Array in Geometry2D.offset_polygon(polygon,height*.025*layer):
				var shifted := PackedVector2Array()
				for point: Vector2 in shadow:shifted.append(point+offset)
				_shadow_polygons.append(shifted)
		if not floor.is_empty():
			for uv: Vector2 in uvs:_floor_uvs.append(uv*Vector2(floor.scale)+Vector2(floor.get("offset",Vector2.ZERO)))
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
		for polygon: PackedVector2Array in _occluders:
			if not Geometry2D.intersect_polygons(polygon,corners).is_empty():
				fade=true
				return

func _process(delta: float) -> void:
	_alpha=move_toward(_alpha,0.16 if fade else 1.0,delta*5)
	modulate.a=_alpha

func _draw() -> void:
	if top.size()<3:return
	if parts.is_empty():
		if map_texture!=null: draw_polygon(top,PackedColorArray([Color.WHITE]),uvs,map_texture)
		return
	var pixel := 1.0/maxf(.01,get_global_transform_with_canvas().get_scale().x)
	for part: Dictionary in parts:
		for face: Dictionary in part.faces:
			draw_polygon(face.points,PackedColorArray([face.color]),face.uvs,part.material)
		if part.textured and map_texture!=null:
			draw_polygon(part.cap,PackedColorArray([Color.WHITE]),part.uvs,map_texture)
		else: draw_colored_polygon(part.cap,part.tint)
		# One material lip per edge, without neon outlines on scenery.
		for face: Dictionary in part.faces:
			draw_line(face.points[2],face.points[3],Color(.58,.68,.72,.46),pixel,true)
			draw_line(face.points[0],face.points[1],Color(0,0,0,.22),pixel,true)

func draw_ground(canvas: CanvasItem, quality: int) -> void:
	if height<=0:return
	var polygon := PackedVector2Array()
	for point: Vector2 in ground:polygon.append(point+position)
	if not floor.is_empty():
		canvas.draw_polygon(polygon,PackedColorArray([Color.WHITE]),_floor_uvs,floor.texture)
	if quality<=0:return
	# Cached static ground shadows do not move when the prop fades.
	for index in range(_shadow_polygons.size()):
		if quality==1 and index>0:break
		canvas.draw_colored_polygon(_shadow_polygons[index],Color(.005,.008,.018,.045 if quality==2 else .10))
	canvas.draw_colored_polygon(polygon,Color(0,0,0,.12))
