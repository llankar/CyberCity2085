extends RefCounted
## Explicit art-scale data, independent of the tactical grid and texture resolution.
const PATH := "res://art/environment/map_presentation.json"
static var _maps: Dictionary={}
static func human_height_ratio(map_data: Dictionary) -> float:
	if _maps.is_empty() and FileAccess.file_exists(PATH):
		var data: Variant=JSON.parse_string(FileAccess.get_file_as_string(PATH))
		if data is Dictionary and int(data.get("schema_version",0))==1:_maps=data.get("maps",{})
	var filename:=str(map_data.get("path","")).replace("\\","/").get_file()
	var entry: Dictionary=_maps.get(filename,{})
	# A handoff can override a single map's presentation without touching surveys.
	var override: Dictionary=map_data.get("presentation",{})
	return clampf(float(override.get("human_height_ratio",entry.get("human_height_ratio",.035))),.015,.10)
