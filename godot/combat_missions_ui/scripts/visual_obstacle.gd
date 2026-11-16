extends Node2D
## Extrusion from the existing UV footprint; never modifies tactical geometry.
var top := PackedVector2Array()
var ground := PackedVector2Array()
var uvs := PackedVector2Array()
var map_texture: Texture2D
var height := 20.0
var fade := false
var tint := Color(0.75,0.82,0.88)
var outline := Color(0.22,0.3,0.34,0.28)

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR

func configure(wall: Dictionary, board, texture: Texture2D) -> void:
	map_texture = texture
	var raw: Array = wall.get("outline_uv", [])
	if raw.size() < 3: return
	var points := PackedVector2Array()
	var anchor := Vector2.ZERO
	for pair: Array in raw:
		var uv := Vector2(float(pair[0]),float(pair[1]))
		uvs.append(uv)
		var p: Vector2 = board.iso_origin + Vector2((uv.x*40.0-uv.y*28.0)*board.iso_tw,(uv.x*40.0+uv.y*28.0)*board.iso_th)
		points.append(p)
		if p.y > anchor.y: anchor = p
	position = anchor
	height = board.iso_tw * (0.72 if bool(wall.get("high", true)) else 0.28)
	for p: Vector2 in points:
		ground.append(p-anchor)
		top.append(p-anchor-Vector2(0,height))
	queue_redraw()

func update_occlusion(world_position: Vector2) -> void:
	# Fade the foreground obstacle when its projected silhouette covers the agent.
	if top.is_empty(): return
	var p := world_position - position - Vector2(0,height*0.35)
	var bounds := Rect2(top[0],Vector2.ZERO)
	for point: Vector2 in top: bounds = bounds.expand(point)
	for point: Vector2 in ground: bounds = bounds.expand(point)
	var next := bounds.grow(12).has_point(p) and world_position.y <= position.y
	if next != fade:
		fade = next
		modulate.a = 0.28 if fade else 1.0

func _draw() -> void:
	if top.size() < 3: return
	# Wrap an inward strip of the object's own image down each side.
	# Both UV rows stay inside the surveyed object instead of sampling the floor.
	var center_uv := Vector2.ZERO
	for uv: Vector2 in uvs: center_uv += uv
	center_uv /= float(uvs.size())
	for i in range(top.size()):
		var j := (i+1)%top.size()
		var face := PackedVector2Array([ground[i],ground[j],top[j],top[i]])
		var side_uv := PackedVector2Array([uvs[i].lerp(center_uv,0.22),uvs[j].lerp(center_uv,0.22),uvs[j],uvs[i]])
		var light := 0.72 if ground[j].x > ground[i].x else 0.52
		if map_texture != null:
			draw_polygon(face,PackedColorArray([Color(light,light,light)]),side_uv,map_texture)
		else:
			draw_colored_polygon(face,Color(0.05,0.06,0.07))
	if map_texture != null:
		draw_polygon(top,PackedColorArray([tint]),uvs,map_texture)
	else:
		draw_colored_polygon(top,Color(0.12,0.17,0.19))
	var edge := top.duplicate()
	edge.append(top[0])
	draw_polyline(edge,outline,0.8,true)
