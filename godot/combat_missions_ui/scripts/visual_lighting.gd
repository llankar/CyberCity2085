extends Node2D
## Local emissive pools sampled from actual art; no global wash hiding geometry.
var points: Array[Dictionary]=[]
var glow: Texture2D
var board
func configure(texture: Texture2D, battlefield, weather: String) -> void:
	board=battlefield
	if texture==null:return
	var source:=texture.get_image().duplicate() as Image
	source.resize(96,54,Image.INTERPOLATE_BILINEAR)
	var candidates: Array[Dictionary]=[]
	for y in range(2,52):
		for x in range(2,94):
			var color:=source.get_pixel(x,y)
			if color.v>.58 and color.s>.30:
				candidates.append({"uv":Vector2(x/96.0,y/54.0),"color":color,"energy":color.v*color.s})
	candidates.sort_custom(func(a,b):return a.energy>b.energy)
	for candidate: Dictionary in candidates:
		var separated:=true
		for existing: Dictionary in points:
			if candidate.uv.distance_to(existing.uv)<.14:separated=false;break
		if separated:points.append(candidate)
		if points.size()>=(6 if weather=="dust" else 10):break
	var image:=Image.create(64,64,false,Image.FORMAT_RGBA8)
	for y in range(64):
		for x in range(64):
			var distance:=Vector2(x-31.5,y-31.5).length()/32.0
			image.set_pixel(x,y,Color(1,1,1,pow(maxf(0,1-distance),2)*.16))
	glow=ImageTexture.create_from_image(image)
	var mat:=CanvasItemMaterial.new();mat.blend_mode=CanvasItemMaterial.BLEND_MODE_ADD;material=mat
	queue_redraw()
func _draw() -> void:
	if glow==null:return
	for point: Dictionary in points:
		var center: Vector2=board.uv_to_world(point.uv)
		var radius: float=board.iso_tw*2.6
		draw_texture_rect(glow,Rect2(center-Vector2(radius,radius*.6),Vector2(radius*2,radius*1.2)),false,point.color)
