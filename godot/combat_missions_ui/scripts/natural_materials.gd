extends RefCounted
## Render-only material response from the reviewed object's actual colors.
static func body_tint(source: Image, uvs: PackedVector2Array) -> Color:
	var bounds:=Rect2(uvs[0],Vector2.ZERO)
	for uv: Vector2 in uvs:bounds=bounds.expand(uv)
	var samples: Array[Color]=[]
	for y in range(1,6):
		for x in range(1,6):
			var uv:=bounds.position+bounds.size*Vector2(x/6.0,y/6.0)
			var color:=source.get_pixelv(Vector2i(uv*Vector2(source.get_size())))
			# Emissive screens are light sources, not a pattern to tile on a side.
			if color.v>.04 and color.v<.48 and color.s<.58:samples.append(color)
	if samples.is_empty():return Color(.14,.15,.16)
	samples.sort_custom(func(a,b):return a.v<b.v)
	return samples[samples.size()/2]

static var _completion_cache: Dictionary={}
static func soft_floor_completion(patch: Dictionary, bounds: Array, source: Image, board) -> Dictionary:
	if not patch.has("texture"):return patch
	var key:=str(patch.texture.get_instance_id())+str(bounds)
	if _completion_cache.has(key):return _completion_cache[key]
	var image: Image=patch.texture.get_image()
	image.convert(Image.FORMAT_RGBA8)
	var scale: Vector2=patch.scale;var offset: Vector2=patch.offset
	var size:=Vector2(image.get_size())
	var donor:=_floor_donor(source,board,bounds)
	if donor!=null:
		var factor: float=size.x/(source.get_width()/scale.x)
		donor.resize(maxi(2,roundi(donor.get_width()*factor)),maxi(2,roundi(donor.get_height()*factor)),Image.INTERPOLATE_BILINEAR)
	var a: Vector2=(Vector2(bounds[0],bounds[1])*scale+offset)*size
	var b: Vector2=(Vector2(bounds[2],bounds[3])*scale+offset)*size
	for y in range(image.get_height()):
		for x in range(image.get_width()):
			var distance:=minf(minf(x+.5-a.x,b.x-x-.5),minf(y+.5-a.y,b.y-y-.5))
			var color:=donor.get_pixel(x%donor.get_width(),y%donor.get_height()) if donor!=null else image.get_pixel(x,y)
			color.a=smoothstep(0.0,clampf(minf(b.x-a.x,b.y-a.y)*.20,8.0,24.0),distance)
			image.set_pixel(x,y,color)
	var result:=patch.duplicate()
	result.texture=ImageTexture.create_from_image(image)
	if _completion_cache.size()>=32:_completion_cache.clear()
	_completion_cache[key]=result
	return result


static func _floor_donor(source: Image, board, bounds: Array) -> Image:
	# Sample real nearby unblocked ground, not a uniform blurred color. This is
	# texture completion only; it never classifies an object or changes a cell.
	var center:=Vector2((bounds[0]+bounds[2])*.5,(bounds[1]+bounds[3])*.5)
	var region:=Rect2(Vector2(bounds[0],bounds[1]),Vector2(bounds[2]-bounds[0],bounds[3]-bounds[1])).grow(.012)
	var candidates: Array[Dictionary]=[]
	for y in range(board.GRID_ROWS):
		for x in range(board.GRID_COLS):
			var cell:=Vector2i(x,y)
			var uv: Vector2=(Vector2(cell)+Vector2(.5,.5))/Vector2(board.GRID_COLS,board.GRID_ROWS)
			if board.is_wall(cell) or region.has_point(uv):continue
			candidates.append({"uv":uv,"distance":uv.distance_to(center)})
	candidates.sort_custom(func(a,b):return a.distance<b.distance)
	var selected: Image=null
	var best:=INF
	var source_size:=Vector2(source.get_size())
	var sample_size:=Vector2i(maxi(8,source.get_width()/board.GRID_COLS/2),maxi(8,source.get_height()/board.GRID_ROWS/2))
	for i in range(mini(12,candidates.size())):
		var uv: Vector2=candidates[i].uv
		var rect:=Rect2i(Vector2i(uv*source_size)-sample_size/2,sample_size).intersection(Rect2i(Vector2i.ZERO,source.get_size()))
		if rect.size.x<2 or rect.size.y<2:continue
		var sample:=source.get_region(rect)
		var total:=0.0;var square:=0.0
		for sy in range(1,5):
			for sx in range(1,5):
				var value:=sample.get_pixel(sx*sample.get_width()/5,sy*sample.get_height()/5).v
				total+=value;square+=value*value
		var mean:=total/16.0
		if mean<.035 or mean>.70:continue
		var variation:=maxf(0,square/16.0-mean*mean)
		var score: float=candidates[i].distance+variation*.8
		if score<best:best=score;selected=sample
	return selected
