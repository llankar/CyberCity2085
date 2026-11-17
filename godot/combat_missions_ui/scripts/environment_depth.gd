extends RefCounted
## Natural 2.5D: explicit source-verified components or an unchanged baked scene.
const Catalog=preload("res://scripts/environment_catalog.gd")
const Materials=preload("res://scripts/natural_materials.gd")
const Shapes=preload("res://scripts/natural_prop_shapes.gd")
var board
var _path := ""
var _verified := false
static var _sprite_cache: Dictionary = {}
var _surfaces = preload("res://scripts/environment_depth_legacy.gd").new()

func prepare(texture: Texture2D, battlefield, map_path: String="", source_path: String="") -> void:
	board=battlefield;_path=map_path
	_verified=texture!=null and not texture is PlaceholderTexture2D and Catalog.matches_source(map_path,source_path,Vector2i(texture.get_size()))
	if _verified:_surfaces.prepare(texture,board,map_path)

func visual_anchor(wall: Dictionary, fallback: Vector2) -> Vector2:
	var entry:=Catalog.annotation(_path,wall) if _verified else {}
	if entry.is_empty():return fallback
	var anchor:=Vector2(-INF,-INF)
	for corner: Vector2 in [Vector2.ZERO,Vector2.RIGHT,Vector2.ONE,Vector2.DOWN]:
		var ground: Vector2=board.uv_to_world(Shapes.uv(entry,corner))
		if ground.y>anchor.y:anchor=ground
	return anchor

static func profile(wall: Dictionary, map_path: String="") -> Dictionary:
	var entry:=Catalog.annotation(map_path,wall)
	if entry.is_empty():return {"kind":"baked","height":0.0,"material":"source"}
	return {"kind":entry.family,"height":float(entry.get("height",Shapes.HEIGHTS[entry.family])),"material":entry.material}

func build_volume(wall: Dictionary, _collision_uvs: PackedVector2Array, anchor: Vector2) -> Dictionary:
	var entry:=Catalog.annotation(_path,wall) if _verified else {}
	if board.top_down:return _sprite_volume(wall,anchor)
	var empty: Dictionary={"height":0.0,"parts":[],"floor":{},"ground_shapes":[],"baked_only":true}
	if entry.is_empty():return empty
	var tile: float=board.iso_tw*2
	var parts: Array[Dictionary]=[]
	var patches: Array[Dictionary]=[]
	var contact: Array[PackedVector2Array]=[]
	var height:=0.0
	for spec: Dictionary in Shapes.pieces(entry):
		var uvs:=PackedVector2Array()
		for point: Vector2 in spec.polygon:uvs.append(Shapes.uv(entry,point))
		# Each part samples only its own source material, not the bounding collision.
		_surfaces._surface_uvs=uvs
		if entry.has("material_sample_uv"):
			var sample: Array=entry.material_sample_uv
			_surfaces._surface_uvs=_surfaces.rect_uv(Rect2(float(sample[0]),float(sample[1]),float(sample[2])-float(sample[0]),float(sample[3])-float(sample[1])))
		var part: Dictionary=_surfaces.prism(uvs,float(spec.low)*tile,float(spec.high)*tile,anchor,_surfaces.cap_tint(uvs),str(spec.material),bool(spec.textured),Rect2(),_surfaces.material_texture(str(spec.material)))
		part["role"]=spec.role;part["material_kind"]=spec.material
		# Real screens stay on top. Side materials never repeat miniature UI,
		# floor decals or entire roofs across vertical structural faces.
		part.material=_surfaces.material_texture(str(spec.material))
		var body_color: Color=Materials.body_tint(_surfaces.source,uvs)
		if spec.material!="fabric":
			for face: Dictionary in part.faces:face.color=face.color*body_color
		if spec.material=="fabric":
			# Reuse a complete, real upholstery panel once; do not tile decorative
			# creases across the whole sofa or paste a rug onto armrests/sides.
			part.material=_surfaces.material_texture("fabric")
			var material_uv: Array=entry.material_sample_uv
			var leather: Color=_surfaces.source.get_pixelv(Vector2i(Vector2((float(material_uv[0])+float(material_uv[2]))*.5,(float(material_uv[1])+float(material_uv[3]))*.5)*Vector2(_surfaces.source.get_size())))
			part.tint=leather
			for face: Dictionary in part.faces:face.color=face.color*Color(leather.r,leather.g,leather.b,1)
			if spec.role in ["cushion","back"]:
				var sample: Array=entry.cushion_sample_uv if spec.role=="cushion" else entry.back_sample_uv
				var bounds:=Rect2(spec.polygon[0],Vector2.ZERO)
				for point: Vector2 in spec.polygon:bounds=bounds.expand(point)
				var cap_uv:=PackedVector2Array()
				for point: Vector2 in spec.polygon:cap_uv.append(Vector2(sample[0],sample[1])+(point-bounds.position)/bounds.size*Vector2(float(sample[2])-float(sample[0]),float(sample[3])-float(sample[1])))
				part["cap_material_uvs"]=cap_uv
				part["source_panel"]=true
				if spec.role=="back" and not part.faces.is_empty():
					var front: Dictionary=part.faces[0]
					for face: Dictionary in part.faces:
						if face.points[0].distance_to(face.points[1])>front.points[0].distance_to(front.points[1]):front=face
					front["source_panel"]=true
					front.uvs=PackedVector2Array([Vector2(sample[0],sample[3]),Vector2(sample[2],sample[3]),Vector2(sample[2],sample[1]),Vector2(sample[0],sample[1])])
					front.color=Color(.84,.84,.84)
			else:
				part.textured=false
		if spec.has("slope"):
			var old: PackedVector2Array=part.cap.duplicate()
			for i in range(part.cap.size()):
				part.cap[i].y+=float(spec.slope)*tile*float(spec.polygon[i].y)
			for face: Dictionary in part.faces:
				for i in [2,3]:
					var index:=old.find(face.points[i])
					if index>=0:face.points[i]=part.cap[index]
		# Matte upholstery and restrained metal edge responses; no global glow.
		for face: Dictionary in part.faces:
			if spec.material=="fabric":face.color=face.color*Color(.87,.84,.81,1)
			elif spec.material=="metal":face.color=face.color*Color(.92,.97,1,1)
		if spec.material=="metal" and entry.family in ["console","machine"]:_source_reflection(part,uvs,anchor)
		if spec.role in ["arm","back","cushion"]:_upholstery_crown(part,tile)
		if float(spec.low)==0:contact.append(uvs)
		parts.append(part)
		height=maxf(height,float(spec.high)*tile)
	# Erase/complete only the actual authored silhouette, never a whole collision.
	var silhouette:=PackedVector2Array()
	if entry.has("source_silhouette_uv"):
		for pair: Array in entry.source_silhouette_uv:silhouette.append(Vector2(pair[0],pair[1]))
	else:
		for point: Vector2 in Shapes.outline(Rect2(.015,.015,.97,.97),.09):silhouette.append(Shapes.uv(entry,point))
	var patch: Dictionary=_surfaces.floor_patch(silhouette).duplicate()
	patch["uvs"]=silhouette
	patches.append(patch)
	# Assembly order is explicit: a lower seat frame must never paint over its
	# higher cushions, nor a front foot over a tabletop. Global unit/prop Y-sort
	# remains unchanged.
	var order: Array=["foot","leg","mount","seat_frame","cabinet","back","cushion","arm","top","sloped_screen","cylinder","wall","partition","crate"]
	parts.sort_custom(func(a,b):return order.find(a.role)<order.find(b.role))
	return {"height":height,"parts":parts,"floor":{"patches":patches},"ground_shapes":contact,"shadow_shapes":[silhouette],"baked_only":false,"fade_alpha":.50 if entry.family in ["sofa","armchair","table","bench"] else .16}

func _upholstery_crown(part: Dictionary, tile: float) -> void:
	# A small rounded shoulder gives upholstery a soft cross-section. This is
	# real cached surface geometry, not a glow or an outline over a box.
	var cap: PackedVector2Array=part.cap
	var center:=Vector2.ZERO
	for p: Vector2 in cap:center+=p/float(cap.size())
	var inner:=PackedVector2Array()
	var inner_uv:=PackedVector2Array()
	var source_uv: PackedVector2Array=part.get("cap_material_uvs",PackedVector2Array())
	var uv_center:=Vector2.ZERO
	for uv: Vector2 in source_uv:uv_center+=uv/float(source_uv.size())
	for i in range(cap.size()):
		inner.append(center.lerp(cap[i],.84)-Vector2(0,tile*.012))
		if not source_uv.is_empty():inner_uv.append(uv_center.lerp(source_uv[i],.84))
	var rims: Array[Dictionary]=[]
	for i in range(cap.size()):
		var j: int=(i+1)%cap.size()
		var tex_uv:=PackedVector2Array()
		if not source_uv.is_empty():tex_uv=PackedVector2Array([source_uv[i],source_uv[j],inner_uv[j],inner_uv[i]])
		rims.append({"points":PackedVector2Array([cap[i],cap[j],inner[j],inner[i]]),"uvs":tex_uv})
	part["soft_cap"]=inner;part["soft_uvs"]=inner_uv;part["soft_rim"]=rims

func _source_reflection(part: Dictionary, uvs: PackedVector2Array, anchor: Vector2) -> void:
	# Local response comes from emissive pixels on the reviewed object itself.
	# No neon source is guessed from a collision ID, and nothing tints the floor.
	var bounds:=Rect2(uvs[0],Vector2.ZERO)
	for uv: Vector2 in uvs:bounds=bounds.expand(uv)
	var light:=Color.BLACK
	var emitter:=bounds.get_center()
	for y in range(1,6):
		for x in range(1,6):
			var uv:=bounds.position+bounds.size*Vector2(x/6.0,y/6.0)
			var pixel:=Vector2i(uv*Vector2(_surfaces.source.get_size()))
			var color: Color=_surfaces.source.get_pixelv(pixel)
			if color.s>.28 and color.v>.48 and color.v*color.s>light.v*light.s:
				light=color;emitter=uv
	if light==Color.BLACK:return
	var origin: Vector2=board.uv_to_world(emitter)-anchor
	for face: Dictionary in part.faces:
		var edge: Vector2=face.points[1]-face.points[0]
		var normal:=Vector2(edge.y,-edge.x).normalized()
		if Geometry2D.is_polygon_clockwise(part.base):normal=-normal
		var toward: Vector2=(origin-(face.points[0]+face.points[1])*.5).normalized()
		var response:=maxf(.15,normal.dot(toward))*.09
		face.color=Color(face.color.r+light.r*response,face.color.g+light.g*response,face.color.b+light.b*response,1)

func _sprite_volume(wall: Dictionary, anchor: Vector2) -> Dictionary:
	var empty: Dictionary={"height":0.0,"parts":[],"floor":{},"ground_shapes":[],"baked_only":true}
	if not _verified:return empty
	var entry:=Catalog.art_annotation(_path,wall)
	if entry.is_empty():
		# Source-preserving foreground layer, not an inferred object or extrusion.
		# It only restores the baked silhouette's depth ordering around units.
		if wall.get("outline_uv",[]).size()>=3 and bool(wall.get("high",true)):
			return {"height":0.0,"parts":[],"floor":{},"ground_shapes":[],"baked_only":false,"fade_alpha":.20,"source_layer":true}
		return empty
	var path: String="res://art/environment/props25/%s-%d.png"%[entry.asset,int(entry.get("yaw",0))]
	if not FileAccess.file_exists(path):return empty
	if not _sprite_cache.has(path):
		var image:=Image.load_from_file(path)
		if image==null:return empty
		var cropped:=image.get_region(image.get_used_rect())
		var bitmap:=BitMap.new();bitmap.create_from_image_alpha(cropped,.12)
		var shapes: Array[PackedVector2Array]=bitmap.opaque_to_polygons(Rect2i(Vector2i.ZERO,cropped.get_size()),2.0)
		var luminance:=0.0;var samples:=0
		for y in range(0,cropped.get_height(),8):
			for x in range(0,cropped.get_width(),8):
				var color:=cropped.get_pixel(x,y)
				if color.a>.8:luminance+=color.v;samples+=1
		_sprite_cache[path]={"texture":ImageTexture.create_from_image(cropped),"shapes":shapes,"luminance":luminance/maxi(1,samples)}
	var texture: Texture2D=_sprite_cache[path].texture
	var b: Array=entry.bounds_uv
	var origin: Vector2=board.uv_to_world(Vector2(b[0],b[1]))
	var end: Vector2=board.uv_to_world(Vector2(b[2],b[3]))
	var target:=Rect2(origin,end-origin)
	var fit:=minf(target.size.x/texture.get_width(),target.size.y/texture.get_height())
	var size:=Vector2(texture.get_size())*fit
	var rect:=Rect2(target.get_center()-size*.5-anchor,size)
	var silhouette:=PackedVector2Array()
	for pair: Array in wall.outline_uv:silhouette.append(Vector2(pair[0],pair[1]))
	# The baked source includes its old contact shadow outside the survey.
	# Complete that small visual margin too, without moving the object/collision.
	var pad:=Vector2(minf(.008,(float(b[2])-float(b[0]))*.15),minf(.008,(float(b[3])-float(b[1]))*.15))
	var erase_bounds: Array=entry.get("erase_bounds_uv",[maxf(0,float(b[0])-pad.x),maxf(0,float(b[1])-pad.y),minf(1,float(b[2])+pad.x),minf(1,float(b[3])+pad.y)])
	var erase:=PackedVector2Array([Vector2(erase_bounds[0],erase_bounds[1]),Vector2(erase_bounds[2],erase_bounds[1]),Vector2(erase_bounds[2],erase_bounds[3]),Vector2(erase_bounds[0],erase_bounds[3])])
	var patch: Dictionary=Materials.soft_floor_completion(_surfaces.floor_patch(erase),erase_bounds,_surfaces.source,board).duplicate();patch["uvs"]=erase
	var polygons: Array[PackedVector2Array]=[]
	var shadows: Array[PackedVector2Array]=[]
	for raw_shape: PackedVector2Array in _sprite_cache[path].shapes:
		var shape:=PackedVector2Array();var shadow:=PackedVector2Array()
		for point: Vector2 in raw_shape:
			var local:=rect.position+point*fit
			shape.append(local)
			shadow.append((local+anchor-board.source_rect.position)/board.source_rect.size)
		polygons.append(shape);shadows.append(shadow)
	var source_tint: Color=Materials.body_tint(_surfaces.source,silhouette)
	var exposure:=clampf(source_tint.v/maxf(.01,float(_sprite_cache[path].luminance)),.35,1.0)
	var material_color:=Color(exposure,exposure,exposure)
	return {"height":board.iso_th*.18,"parts":[],"floor":{"patches":[patch]},"ground_shapes":[],"shadow_shapes":shadows,"baked_only":false,"fade_alpha":.35,"sprite":{"texture":texture,"rect":rect,"silhouettes":polygons,"color":material_color}}
