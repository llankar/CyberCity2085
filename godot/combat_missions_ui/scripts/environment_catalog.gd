extends RefCounted
## Explicit, image-reviewed render annotations. Collision names never imply a mesh.
const PATH := "res://art/environment/natural_geometry.json"
const FAMILIES := ["sofa","armchair","table","bench","console","crate","machine","wall","partition"]
static var _maps: Dictionary = {}
static var _hashes: Dictionary = {}
static var _art: Dictionary = {}

static func maps() -> Dictionary:
	if _maps.is_empty():
		if not FileAccess.file_exists(PATH):return {}
		var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(PATH))
		if data is Dictionary and int(data.get("schema_version",0))==1:
			_maps=data.get("maps",{})
	return _maps

static func annotation(map_path: String, wall: Dictionary) -> Dictionary:
	var record: Dictionary=maps().get(map_path.get_file(),{})
	var id := str(wall.get("id",wall.get("wall_id","")))
	var entry: Dictionary=record.get("props",{}).get(id,{})
	if str(entry.get("family","")) not in FAMILIES:return {}
	for key in ["origin","axis_u","axis_v"]:
		if entry.get(key,[]).size()!=2:return {}
	if str(entry.get("material","")) not in ["fabric","metal","wood","stone"]:return {}
	var origin:=Vector2(entry.origin[0],entry.origin[1])
	var u:=Vector2(entry.axis_u[0],entry.axis_u[1]);var v:=Vector2(entry.axis_v[0],entry.axis_v[1])
	if absf(u.cross(v))<.000001:return {}
	for point: Vector2 in [origin,origin+u,origin+v,origin+u+v]:
		if point.x<0 or point.y<0 or point.x>1 or point.y>1:return {}
	if float(entry.get("height",.2))<=0 or float(entry.get("height",.2))>.32:return {}
	if entry.family in ["sofa","armchair"]:
		for key in ["material_sample_uv","cushion_sample_uv","back_sample_uv"]:
			var sample: Array=entry.get(key,[])
			if sample.size()!=4:return {}
			if float(sample[0])<0 or float(sample[1])<0 or float(sample[2])>1 or float(sample[3])>1:return {}
			if float(sample[2])<=float(sample[0]) or float(sample[3])<=float(sample[1]):return {}
	return entry

static func matches_source(map_path: String, source_path: String, size: Vector2i) -> bool:
	var record: Dictionary=maps().get(map_path.get_file(),art_maps().get(map_path.get_file(),{}))
	if record.is_empty() or source_path.is_empty() or not FileAccess.file_exists(source_path):return false
	var dimensions: Array=record.get("image_size",[])
	if dimensions.size()!=2 or size!=Vector2i(int(dimensions[0]),int(dimensions[1])):return false
	# Cache per file version; replacing art invalidates its render annotations.
	var key := source_path+":"+str(FileAccess.get_modified_time(source_path))
	if not _hashes.has(key):_hashes[key]=FileAccess.get_sha256(source_path)
	return str(_hashes[key])==str(record.get("image_sha256",""))

static func art_maps() -> Dictionary:
	if _art.is_empty():
		var path: String="res://art/environment/environment_art.json"
		if not FileAccess.file_exists(path):return {}
		var data: Variant=JSON.parse_string(FileAccess.get_file_as_string(path))
		if data is Dictionary and int(data.get("schema_version",0))==1:_art=data.get("maps",{})
	return _art

static func art_annotation(map_path: String, wall: Dictionary) -> Dictionary:
	for entry: Dictionary in art_maps().get(map_path.get_file(),{}).get("props",[]):
		if entry.get("id","")==str(wall.get("id",wall.get("wall_id",""))) and bool(entry.get("enabled",false)):
			var bounds: Array=entry.get("bounds_uv",[])
			if bounds.size()==4 and float(bounds[0])>=0 and float(bounds[1])>=0 and float(bounds[2])<=1 and float(bounds[3])<=1 and float(bounds[2])>float(bounds[0]) and float(bounds[3])>float(bounds[1]):return entry
	return {}

static func art_walls(map_path: String) -> Array[Dictionary]:
	var walls: Array[Dictionary]=[]
	for entry: Dictionary in art_maps().get(map_path.get_file(),{}).get("props",[]):
		if not bool(entry.get("enabled",false)):continue
		var b: Array=entry.bounds_uv
		walls.append({"id":entry.id,"wall_id":entry.id,"source_object_id":entry.source_object_id,"outline_uv":[[b[0],b[1]],[b[2],b[1]],[b[2],b[3]],[b[0],b[3]]]})
	return walls
