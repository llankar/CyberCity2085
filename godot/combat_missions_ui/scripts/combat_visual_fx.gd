extends Node2D
## Bounded transient effects, driven only after accepted combat actions.
var quality := 2
var effects: Array[Dictionary] = []
const LIMIT := 64

func burst(kind: String, origin: Vector2, target: Vector2) -> void:
	if effects.size() >= LIMIT: effects.pop_front()
	effects.append({"kind":kind,"from":origin,"to":target,"age":0.0,"life":2.0 if kind == "smoke" else (0.7 if kind in ["explosion","psi","heal"] else 0.3)})
	if kind == "explosion" and quality > 0: burst("smoke",target,target)
	set_process(true)

func _process(delta: float) -> void:
	for effect: Dictionary in effects: effect["age"] += delta
	effects = effects.filter(func(e: Dictionary): return e["age"] < e["life"])
	queue_redraw()
	if effects.is_empty(): set_process(false)

func _draw() -> void:
	for e: Dictionary in effects:
		var t: float = float(e["age"]) / float(e["life"])
		var a: Vector2 = e["from"]
		var b: Vector2 = e["to"]
		var kind: String = e["kind"]
		var col := Color(1,0.72,0.22,1-t)
		if kind in ["psi","heal"]: col = Color(0.55,0.4,1,1-t) if kind == "psi" else Color(0.15,1,0.7,1-t)
		if kind == "smoke":
			for i in range(5):
				var drift := Vector2(sin(float(i)*2.4)*t*18,-t*(20+float(i)*7))
				draw_circle(b+drift,5+t*(10+float(i)*3),Color(0.12,0.15,0.18,(1-t)*0.16))
		elif kind == "fire":
			var tip := a.lerp(b,minf(1,t*2.5))
			draw_line(tip.lerp(a,0.12),tip,col,2,true)
			if t < 0.25:
				draw_circle(a,8*(1-t*4),col)
		elif kind == "melee":
			draw_arc(b,12+t*14,-PI*0.8,PI*0.3,16,col,3,true)
		elif kind == "explosion":
			draw_circle(b,14+45*t,Color(1,0.2+0.4*t,0.03,(1-t)*0.35))
			draw_arc(b,10+55*t,0,TAU,32,col,2,true)
		else:
			draw_arc(b,5+32*t,0,TAU,32,col,2,true)
		if quality > 0 and kind not in ["fire","smoke"]:
			var count := 16 if quality == 2 else 6
			for i in range(count):
				var angle := float(i)*2.39996
				var drift := Vector2(cos(angle),sin(angle)*0.55)
				var p := b+drift*t*(18+float(i%5)*9)+Vector2(0,-12*t+14*t*t)
				draw_line(p,p-drift*4,col,1,true)
