extends RefCounted
## Render-only dimensions/materials. Surveyed tactical cells are never edited.
var board
var source: Image
var _map_path := ""
static var _floor_cache: Dictionary = {}
var _source_key := 0
static var _source_cache: Dictionary = {}
static var _materials: Dictionary = {}
static var _facade_cache: Dictionary = {}
var _surface_uvs := PackedVector2Array()

func prepare(texture: Texture2D, battlefield, map_path: String = "") -> void:
	board = battlefield
	_map_path=map_path.to_lower()
	if texture != null and not texture is PlaceholderTexture2D:
		var key := texture.get_instance_id()
		_source_key=key
		if not _source_cache.has(key):
			_source_cache.clear() # one source image, reused across viewport rebuilds
			_source_cache[key] = texture.get_image()
		source = _source_cache[key]

static func profile(wall: Dictionary, map_path: String = "") -> Dictionary:
	var id := str(wall.get("id",wall.get("wall_id",""))).to_lower()
	var location := map_path.get_file().to_lower()
	var exterior_wastes := "wasteland" in location and not ("inner" in location or "interior" in location or "tunnel" in location)
	var built_site := "bunker" in location or "fortress" in location or "compound" in location or "outpost" in location
	if exterior_wastes and not built_site:
		return {"kind":"baked","height":0.0,"material":"source"}
	var kind := "block"
	var elevation := .32
	var material := "metal"
	# Irregular baked silhouettes have no surveyed vertical facade. Preserve the
	# actual wreck/rock/debris art instead of putting its rectangle on a plinth.
	if "wreck" in id or "rock" in id or "rubble" in id or "ruin" in id or "debris" in id or "scrap" in id or "junk" in id:
		return {"kind":"baked","height":0.0,"material":"source"}
	if "water" in id or "pool" in id or "boundary" in id:
		return {"kind":"flat","height":0.0,"material":"stone"}
	if "edge" in id or "fountain" in id:
		elevation=.28 if "edge" in id else .12;material="stone"
	elif "sofa" in id or "chair" in id or "lounge" in id:
		kind="seat";elevation=.26 if "chair" in id else .22;material="fabric"
	elif "table" in id or "desk" in id or "bench" in id:
		kind="table";elevation=.22 if "coffee" in id else .36
	elif "bed" in id and "bedroom" not in id:
		elevation=.20;material="fabric"
	elif "wall" in id or "room" in id or "entry" in id or "cross" in id or "partition" in id:
		elevation=.68;material="stone"
	elif "building" in id or "tower" in id:
		elevation=.90;material="stone"
	elif "awning" in id or "stall" in id or "market" in id:
		kind="canopy";elevation=.56;material="fabric"
	elif "container" in id or "machine" in id or "reactor" in id or "rack" in id or "server" in id:
		elevation=.54
	return {"kind":kind,"height":elevation,"material":material}

func floor_patch(uvs: PackedVector2Array) -> Dictionary:
	if source == null: return {}
	if not _floor_cache.has(_source_key):
		if _floor_cache.size()>=2: _floor_cache.clear()
		_floor_cache[_source_key]={}
	var key := str(uvs)
	if _floor_cache[_source_key].has(key): return _floor_cache[_source_key][key]
	var bounds := Rect2(uvs[0],Vector2.ZERO)
	for uv: Vector2 in uvs: bounds=bounds.expand(uv)
	var image_size := Vector2(source.get_size())
	var rect := Rect2i(bounds.position*image_size,bounds.size*image_size).grow(96)
	rect=rect.intersection(Rect2i(Vector2i.ZERO,source.get_size()))
	var patch := source.get_region(rect)
	var factor := minf(1.0,192.0/maxf(patch.get_width(),patch.get_height()))
	patch.resize(maxi(2,roundi(patch.get_width()*factor)),maxi(2,roundi(patch.get_height()*factor)),Image.INTERPOLATE_BILINEAR)
	patch.convert(Image.FORMAT_RGBA8)
	var polygon := PackedVector2Array()
	for uv: Vector2 in uvs: polygon.append((uv*image_size-Vector2(rect.position))/Vector2(rect.size)*Vector2(patch.get_size()))
	# Push/pull completion preserves the surrounding floor at the boundary.
	# Only the visual footprint is reconstructed, never the actual map file.
	for y in range(patch.get_height()):
		for x in range(patch.get_width()):
			if Geometry2D.is_point_in_polygon(Vector2(x+.5,y+.5),polygon): patch.set_pixel(x,y,Color(0,0,0,0))
	var levels: Array[Image]=[patch]
	while levels[-1].get_width()>1 or levels[-1].get_height()>1:
		var previous: Image=levels[-1]
		var next := Image.create(maxi(1,previous.get_width()/2),maxi(1,previous.get_height()/2),false,Image.FORMAT_RGBA8)
		# Explicit box filtering keeps RGB premultiplied with the validity weight.
		# Image.resize performs alpha-aware filtering, unsuitable for this mask.
		for y in range(next.get_height()):
			for x in range(next.get_width()):
				var sum := Color(0,0,0,0)
				for dy in range(2):
					for dx in range(2):sum+=previous.get_pixel(mini(previous.get_width()-1,x*2+dx),mini(previous.get_height()-1,y*2+dy))
				next.set_pixel(x,y,sum*.25)
		levels.append(next)
	var filled: Image=levels[-1].duplicate()
	var average := filled.get_pixel(0,0)
	filled.fill(Color(average.r/average.a,average.g/average.a,average.b/average.a,1) if average.a>.001 else Color(.09,.10,.11))
	for index in range(levels.size()-2,-1,-1):
		var level: Image=levels[index]
		filled.resize(level.get_width(),level.get_height(),Image.INTERPOLATE_BILINEAR)
		for y in range(level.get_height()):
			for x in range(level.get_width()):
				var known := level.get_pixel(x,y)
				var background := filled.get_pixel(x,y)
				filled.set_pixel(x,y,Color(known.r+background.r*(1-known.a),known.g+background.g*(1-known.a),known.b+background.b*(1-known.a),1))
	var result := {"texture":ImageTexture.create_from_image(filled),"scale":image_size/Vector2(rect.size),"offset":-Vector2(rect.position)/Vector2(rect.size)}
	_floor_cache[_source_key][key]=result
	return result

func cap_tint(uvs: PackedVector2Array) -> Color:
	if source == null: return Color(.32,.37,.40)
	var color := Color(0,0,0,1)
	for uv: Vector2 in uvs:
		var pixel := Vector2i(uv*Vector2(source.get_size()))
		color += source.get_pixel(clampi(pixel.x,0,source.get_width()-1),clampi(pixel.y,0,source.get_height()-1))
	color /= float(uvs.size())
	return Color(clampf(color.r,.18,.65),clampf(color.g,.18,.65),clampf(color.b,.18,.65))

static func material_texture(kind: String) -> Texture2D:
	if _materials.has(kind): return _materials[kind]
	var image := Image.create(64,64,false,Image.FORMAT_RGBA8)
	for y in range(64):
		for x in range(64):
			var noise := float((x*37+y*19+x*y*3)%17)/170.0
			var value := .82+noise
			# Only used without source art; never invent tiled wall panels.
			if kind=="fabric": value=.78+float((x+y)%3)*.04+noise
			image.set_pixel(x,y,Color(value,value,value,1))
	_materials[kind] = ImageTexture.create_from_image(image)
	return _materials[kind]

func build_volume(wall: Dictionary, uvs: PackedVector2Array, anchor: Vector2) -> Dictionary:
	_surface_uvs=uvs
	var style := profile(wall,_map_path)
	var tile: float = board.iso_tw*2.0
	var height: float = tile*float(style.height)
	var parts: Array[Dictionary] = []
	if height<=0: return {"height":0.0,"parts":parts,"floor":{}}
	var tint := cap_tint(uvs)
	var bounds := Rect2(uvs[0],Vector2.ZERO)
	for uv: Vector2 in uvs: bounds=bounds.expand(uv)
	var cap_uvs := beveled_uv(bounds,.055) if style.kind in ["seat","table"] and uvs.size()==4 else uvs
	var chair := "chair" in str(wall.get("id",wall.get("wall_id","")))
	if style.kind=="canopy" and uvs.size()==4:
		for corner in [Vector2(.05,.05),Vector2(.89,.05),Vector2(.05,.89),Vector2(.89,.89)]:
			parts.append(prism(rect_uv(Rect2(bounds.position+bounds.size*corner,bounds.size*.06)),0,height,anchor,tint*.65,"metal",false))
		for half in range(2):
			var roof := Rect2(bounds.position+Vector2(0,bounds.size.y*.5*half),bounds.size*Vector2(1,.5))
			parts.append(prism(rect_uv(roof),height-tile*.035,height,anchor,tint,"fabric",true,bounds))
	elif (style.kind=="table" or chair) and uvs.size()==4:
		var leg_size := bounds.size*Vector2(.10,.12)
		for corner in [Vector2(.12,.12),Vector2(.78,.12),Vector2(.12,.76),Vector2(.78,.76)]:
			var leg := rect_uv(Rect2(bounds.position+bounds.size*corner,leg_size))
			parts.append(prism(leg,0,height-tile*.045,anchor,tint*.65,"metal",false))
		parts.append(prism(cap_uvs,height-tile*.045,height,anchor,tint,str(style.material),true))
	else:
		parts.append(prism(cap_uvs,0,height,anchor,tint,str(style.material),true))
	if style.kind=="seat" and uvs.size()==4:
		var back := Rect2(bounds.position,bounds.size*Vector2(1,.18))
		if str(wall.get("id",wall.get("wall_id",""))).ends_with("_e"):
			back=Rect2(bounds.position+bounds.size*Vector2(.82,0),bounds.size*Vector2(.18,1))
		parts.append(prism(rect_uv(back),height,height+tile*(.25 if chair else .19),anchor,tint,"fabric",true))
		for side in [0.0,.86]:
			var arm := Rect2(bounds.position+bounds.size*Vector2(side,.18),bounds.size*Vector2(.14,.82))
			parts.append(prism(rect_uv(arm),height,height+tile*.08,anchor,tint,"fabric",true))
	# Painter order within a prop follows its parts' actual ground depth.
	parts.sort_custom(func(a,b):return float(a.depth)<float(b.depth))
	return {"height":height+(tile*(.25 if chair else .19) if style.kind=="seat" else (tile*.14 if style.kind=="canopy" else 0.0)),"parts":parts,"floor":floor_patch(uvs)}

func prism(uvs: PackedVector2Array, low: float, high: float, anchor: Vector2, tint: Color, material: String, textured_cap: bool, roof_slope: Rect2 = Rect2()) -> Dictionary:
	var base := PackedVector2Array()
	var cap := PackedVector2Array()
	var depth := -INF
	for uv: Vector2 in uvs:
		var point: Vector2 = board.uv_to_world(uv)-anchor
		var ridge := 0.0
		if roof_slope.has_area():
			ridge=board.iso_tw*2*.14*maxf(0,1-absf(uv.y-roof_slope.get_center().y)/(roof_slope.size.y*.5))
		base.append(point-Vector2(0,low+ridge));cap.append(point-Vector2(0,high+ridge))
		depth=maxf(depth,point.y)
	var surface: Texture2D=facade_texture(material,_surface_uvs)
	var source_surface := source!=null and not _surface_uvs.is_empty()
	var span := Vector2.ONE*maxf(1,board.iso_tw*.8)
	if source_surface:
		# The facade keeps the source texel density in both axes.
		var texel: float=board._u_axis.length()/float(source.get_width())
		span=surface.get_size()*texel
	var faces: Array[Dictionary] = []
	var clockwise := Geometry2D.is_polygon_clockwise(base)
	for i in range(base.size()):
		var j := (i+1)%base.size()
		var edge := base[j]-base[i]
		var normal := Vector2(edge.y,-edge.x).normalized()
		if clockwise: normal=-normal
		if normal.y<=.01: continue
		var shade := .78+.18*normal.dot(Vector2(-.8,.6))
		var width: float = edge.length()/maxf(1,span.x)
		var rise: float = (high-low)/maxf(1,span.y)
		faces.append({"points":PackedVector2Array([base[i],base[j],cap[j],cap[i]]),"uvs":PackedVector2Array([Vector2(0,rise),Vector2(width,rise),Vector2(width,0),Vector2.ZERO]),"color":Color(shade,shade,shade,1) if source_surface else Color(tint.r*shade,tint.g*shade,tint.b*shade,1)})
	return {"base":base,"cap":cap,"uvs":uvs,"faces":faces,"material":surface,"source_material":source_surface,"textured":textured_cap,"tint":tint,"depth":depth}

static func rect_uv(rect: Rect2) -> PackedVector2Array:
	return PackedVector2Array([rect.position,Vector2(rect.end.x,rect.position.y),rect.end,Vector2(rect.position.x,rect.end.y)])

static func beveled_uv(rect: Rect2, fraction: float) -> PackedVector2Array:
	var x := rect.position.x
	var y := rect.position.y
	var r := rect.end.x
	var b := rect.end.y
	var cut := rect.size*clampf(fraction,0,.2)
	return PackedVector2Array([Vector2(x+cut.x,y),Vector2(r-cut.x,y),Vector2(r,y+cut.y),Vector2(r,b-cut.y),Vector2(r-cut.x,b),Vector2(x+cut.x,b),Vector2(x,b-cut.y),Vector2(x,y+cut.y)])

func facade_texture(fallback: String, uvs: PackedVector2Array) -> Texture2D:
	if source==null or uvs.is_empty(): return material_texture(fallback)
	if not _facade_cache.has(_source_key):
		if _facade_cache.size()>=2: _facade_cache.clear()
		_facade_cache[_source_key]={}
	var bounds := Rect2(uvs[0],Vector2.ZERO)
	for uv: Vector2 in uvs: bounds=bounds.expand(uv)
	var dimensions := Vector2i(clampi(roundi(bounds.size.x*source.get_width()*.65),8,96),clampi(roundi(bounds.size.y*source.get_height()*.65),8,96))
	var origin := Vector2i(bounds.get_center()*Vector2(source.get_size()))-dimensions/2
	origin.x=clampi(origin.x,0,source.get_width()-dimensions.x)
	origin.y=clampi(origin.y,0,source.get_height()-dimensions.y)
	var key := str(Rect2i(origin,dimensions))
	if not _facade_cache[_source_key].has(key):
		# Mirror the original pixels into a seamless repeat. No resize, generated
		# panel grid, flat recoloring or stretched roof strip is introduced.
		var patch := source.get_region(Rect2i(origin,dimensions))
		patch.convert(Image.FORMAT_RGBA8)
		var image := Image.create(dimensions.x*2,dimensions.y*2,false,Image.FORMAT_RGBA8)
		var region := Rect2i(Vector2i.ZERO,dimensions)
		image.blit_rect(patch,region,Vector2i.ZERO)
		patch.flip_x();image.blit_rect(patch,region,Vector2i(dimensions.x,0))
		patch.flip_y();image.blit_rect(patch,region,dimensions)
		patch.flip_x();image.blit_rect(patch,region,Vector2i(0,dimensions.y))
		_facade_cache[_source_key][key]=ImageTexture.create_from_image(image)
	return _facade_cache[_source_key][key]
