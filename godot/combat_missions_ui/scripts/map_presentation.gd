extends RefCounted
## Explicit art-scale data, independent of the tactical grid and texture resolution.
const PATH := "res://art/environment/map_presentation.json"
static var _maps: Dictionary={}
static func entry_for(map_data: Dictionary) -> Dictionary:
	if _maps.is_empty() and FileAccess.file_exists(PATH):
		var data: Variant=JSON.parse_string(FileAccess.get_file_as_string(PATH))
		if data is Dictionary and int(data.get("schema_version",0))==1:_maps=data.get("maps",{})
	var filename:=str(map_data.get("path","")).replace("\\","/").get_file()
	return _maps.get(filename,{})

static func human_height_ratio(map_data: Dictionary) -> float:
	var entry := entry_for(map_data)
	# This is the single global entity-scale base for the map. Agents, enemies,
	# robots, armors and vehicles all consume it; their intrinsic type multiplier
	# preserves relative silhouette differences without recalibrating the map.
	# A handoff can override one map's presentation without touching surveys.
	var override: Dictionary=map_data.get("presentation",{})
	return clampf(float(override.get("human_height_ratio",entry.get("human_height_ratio",.035))),.015,.10)
