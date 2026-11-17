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
