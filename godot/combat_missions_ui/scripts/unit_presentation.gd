extends RefCounted
## Visual calibration only. Never write stats, footprints, AP or encounter flags.
static func is_vehicle(data: Dictionary, key: String) -> bool:
	return not str(data.get("vehicle_key","")).is_empty() or key.begins_with("vehicle_")

static func is_aircraft(data: Dictionary, key: String) -> bool:
	return is_vehicle(data,key) and ("aerial" in key or "vtol" in key or "vtol" in str(data.get("vehicle_key","")))

static func body_scale(data: Dictionary, key: String) -> float:
	var requested:=clampf(float(data.get("size_scale",1)),.5,3.5)
	# Preserve deliberate giants and the established vehicle scale.
	if bool(data.get("is_giant",false)) or is_vehicle(data,key):return requested
	var role:=str(data.get("role",""))
	var theme:=str(data.get("enemy_theme",""))
	if role in ["power_armor","heavy_armor"] or "power_armor" in theme:return 1.15
	# The support handoff's 3.5 default is not a giant classification. A normal
	# combat robot remains larger than a human, without filling an apartment.
	if role=="robot" or "robot" in str(data.get("asset_type","")) or "robot" in key:
		return minf(requested,1.65)
	return requested

static func shadow_projection(data: Dictionary, key: String) -> Vector2:
	if is_aircraft(data,key):return Vector2(-.12,-.38)
	if is_vehicle(data,key):return Vector2(-.18,-.30)
	return Vector2(-.40,-.18)

static func shadow_opacity(data: Dictionary, key: String) -> float:
	return .16 if is_aircraft(data,key) else (.26 if is_vehicle(data,key) else .23)

static func contact_half_width(data: Dictionary, key: String, body_width: float, fallback: float) -> float:
	# Track/wheel contact spans the chassis, not a humanoid-sized dot.
	return maxf(fallback,body_width*.34) if is_vehicle(data,key) and not is_aircraft(data,key) else fallback
