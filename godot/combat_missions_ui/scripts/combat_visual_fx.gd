extends Node2D
## Actual action effects, scaled in screen pixels so zoom cannot hide a shot.
var quality := 2
var effects: Array[Dictionary] = []
const LIMIT := 64
const LIGHTING = preload("res://scripts/visual_lighting.gd")
var _glow: Texture2D

func _ready() -> void:
	_glow = LIGHTING.glow_texture()
	set_process(false)

func burst(kind: String, origin: Vector2, target: Vector2, delay: float = 0.0) -> void:
	if effects.size() >= LIMIT: effects.pop_front()
	var life := 0.65
	if kind == "smoke": life = 2.4
	elif kind in ["psi","heal","explosion"]: life = 1.15
	elif kind == "plasma": life = 0.85
	effects.append({"kind":kind,"from":origin,"to":target,"age":-delay,"life":life})
	if kind == "explosion" and quality > 0: burst("smoke",target,target,delay)
	set_process(true)
	queue_redraw()

func _process(delta: float) -> void:
	for effect: Dictionary in effects: effect["age"] += delta
	effects = effects.filter(func(e: Dictionary): return e["age"] < e["life"])
	queue_redraw()
	if effects.is_empty(): set_process(false)

func _draw() -> void:
	var zoom := maxf(0.05,get_global_transform_with_canvas().get_scale().x)
	var px := clampf(get_viewport_rect().size.y/1080.0,0.85,2.5)/zoom
	for e: Dictionary in effects:
		var age: float = e["age"]
		if age < 0: continue
		var t: float = age/float(e["life"])
		var a: Vector2 = e["from"]
		var b: Vector2 = e["to"]
		var kind: String = e["kind"]
		var col := Color(1,0.72,0.22,1-t)
		if kind in ["psi","heal"]: col = Color(0.7,0.35,1,1-t) if kind == "psi" else Color(0.1,1,0.65,1-t)
		elif kind == "plasma": col = Color(0.15,0.85,1,1-t)
		if quality > 0 and kind != "smoke":
			_draw_flash(a,b,kind,age,t,col,px)
		if kind == "smoke":
			for i in range(5):
				var drift := Vector2(sin(float(i)*2.4)*t*20,-t*(22+float(i)*8))*px
				draw_circle(b+drift,(5+t*(12+float(i)*3))*px,Color(0.12,0.15,0.18,(1-t)*0.22))
		elif kind in ["fire","plasma"]:
			var travel := clampf(age/0.24,0,1)
			var tip := a.lerp(b,travel)
			var tail := a.lerp(b,maxf(0,travel-0.20))
			if age < 0.32:
				draw_line(tail,tip,Color(col,0.16),12*px,true)
				draw_line(tail,tip,col,(4.0 if kind == "plasma" else 2.8)*px,true)
				draw_circle(tip,(4.5 if kind == "plasma" else 2.5)*px,Color(0.9,1,1,col.a))
			if quality > 0 and age >= .20:
				var impact_age := age-.20
				var sparks := 9 if quality == 2 else 4
				for index in range(sparks):
					var angle := float(index)*2.39996
					var direction := Vector2(cos(angle),sin(angle)*.65)
					var tip_spark := b+(direction*impact_age*(70+index*9)+Vector2(0,impact_age*impact_age*70))*px
					draw_line(tip_spark,tip_spark-direction*4*px,Color(col,(1-t)*.8),1.4*px,true)
			if age < 0.14:
				var radius := (14.0 if kind == "plasma" else 11.0)*(1-age/0.14)*px
				draw_circle(a,radius*1.8,Color(col,0.12))
				draw_circle(a,radius,Color(col,0.7))
				draw_line(a-Vector2(radius*1.4,0),a+Vector2(radius*1.4,0),Color(1,1,0.8),2*px,true)
		elif kind == "melee":
			var radius := (20+t*18)*px
			var start := (b-a).angle()-1.2+t*1.7
			draw_arc(b,radius,start,start+1.5,24,Color(col,0.2),13*px,true)
			draw_arc(b,radius,start,start+1.5,24,col,4*px,true)
		elif kind == "explosion":
			draw_circle(b,(14+48*t)*px,Color(1,0.2+0.4*t,0.03,(1-t)*0.38))
			draw_arc(b,(10+58*t)*px,0,TAU,48,col,3*px,true)
		elif kind == "psi":
			if a.distance_to(b) > 1:
				var points := PackedVector2Array()
				for i in range(17):
					var f := float(i)/16.0
					points.append(a.lerp(b,f)+Vector2(0,sin(f*TAU*3+age*20)*7*px*sin(f*PI)))
				draw_polyline(points,Color(col,0.17),12*px,true)
				draw_polyline(points,col,3*px,true)
			draw_arc(b,(10+38*t)*px,0,TAU,48,col,3*px,true)
		elif kind == "impact":
			draw_circle(b,(12*(1-t)+2)*px,Color(1,0.65,0.2,(1-t)*0.35))
			draw_arc(b,(4+20*t)*px,0,TAU,32,col,2*px,true)
		else:
			draw_arc(b,(5+32*t)*px,0,TAU,32,col,3*px,true)
		if quality > 0 and kind not in ["fire","plasma","smoke"]:
			var count := 18 if quality == 2 else 8
			for i in range(count):
				var angle := float(i)*2.39996
				var drift := Vector2(cos(angle),sin(angle)*0.65)
				var p := b+(drift*t*(20+float(i%5)*10)+Vector2(0,-18*t+22*t*t))*px
				draw_line(p,p-drift*6*px,col,1.8*px,true)

func _draw_flash(origin: Vector2, target: Vector2, kind: String, age: float, t: float, color: Color, px: float) -> void:
	if _glow == null: return
	var center := target
	var radius := 35.0
	var alpha := (1-t)*.55
	if kind in ["fire","plasma"]:
		center = origin if age < .14 else target
		alpha = maxf(0,1-age/.14)*1.3 if age < .14 else maxf(0,1-absf(age-.25)/.15)*.7
		radius = 46 if kind == "plasma" else 34
	elif kind == "explosion":
		radius = 85+45*t
		alpha = pow(1-t,2)*1.3
	elif kind in ["heal","psi"]:
		radius = 38+18*sin(t*PI)
		alpha = sin(t*PI)*.65
		if kind == "heal":
			for i in range(3 if quality == 2 else 1):
				var point := target+Vector2(sin(float(i)*2.4+t*4)*16,-t*55-i*10)*px
				draw_line(point-Vector2(4,0)*px,point+Vector2(4,0)*px,Color(color,1-t),2*px,true)
				draw_line(point-Vector2(0,4)*px,point+Vector2(0,4)*px,Color(color,1-t),2*px,true)
	# Reuse the same cached soft texture as the environment pools.
	draw_texture_rect(_glow,Rect2(center-Vector2(radius,radius*.65)*px,Vector2(radius*2,radius*1.3)*px),false,Color(color,alpha))
