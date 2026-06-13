extends RefCounted
## EncounterGenerator — analyses mission handoff data and produces a complete,
## data-driven encounter: enemy units (with scaled stats, roles, optional giant
## modifier, and tactical placement) plus an objective record.
##
## Usage (from CombatRoot._seed_combat_state):
##   var enc := EncounterGenerator.new()
##   var result := enc.generate(handoff, GRID_COLS, GRID_ROWS)
##   enemy_units = result["enemy_units"]
##   objective   = result["objective"]

# ──────────────────────────────────────────────────────────────────────────────
# Location classification
# Maps map.environment, map.key, and mission.district to a canonical location
# type used to select enemy pools and placement zones.
# ──────────────────────────────────────────────────────────────────────────────

func classify_location(mission: Dictionary, map: Dictionary) -> String:
	var env      := str(map.get("environment",  "city")).to_lower()
	var map_key  := str(map.get("key",          "")).to_lower()
	var district := str(mission.get("district", "")).to_lower()
	if "sewer"      in map_key or "sewer"      in district: return "sewer"
	if "industrial" in map_key or "industrial" in district: return "industrial"
	if "lab"        in map_key or "laboratory" in map_key:  return "lab"
	if "bunker"     in map_key or "bunker"     in district: return "bunker"
	if "facility"   in map_key or "facility"   in district: return "corporate_facility"
	if "ruin"       in map_key or "ruin"       in district: return "ruins"
	if env == "wasteland":                                   return "wasteland"
	return "city"

# ──────────────────────────────────────────────────────────────────────────────
# Theme category
# Collapses the detailed enemy_theme string (e.g. "corp_samurai_power_armor")
# to a broad category for pool selection and giant eligibility.
# ──────────────────────────────────────────────────────────────────────────────

func theme_category(theme: String) -> String:
	if theme.begins_with("corp"):     return "corp"
	if theme.begins_with("mutant"):   return "mutant"
	if theme.begins_with("raider"):   return "raider"
	if theme.begins_with("starver"):  return "starver"
	if "robot" in theme:              return "robot"
	return "generic"

# ──────────────────────────────────────────────────────────────────────────────
# Briefing analysis
# Extracts all encounter-shaping signals from mission + map data.
# ──────────────────────────────────────────────────────────────────────────────

func analyze_briefing(mission: Dictionary, map: Dictionary) -> Dictionary:
	var obj_text := str(mission.get("objective_text", "")).to_lower()
	var title    := str(mission.get("title",          "")).to_lower()
	var risk     := int(mission.get("risk_level",      5))
	var theme    := str(mission.get("enemy_theme",    "generic")).to_lower()
	var obj_type := str(mission.get("objective_type", "")).to_lower()
	var location := classify_location(mission, map)

	# Story missions get harder compositions and a giant chance boost.
	var is_story := risk >= 8 \
		or "story" in title or "priority" in title \
		or "vip"   in title or "command"  in title

	# Derive enemy behavior tags from objective text keywords.
	var tags: Array[String] = []
	if "ambush"    in obj_text or "trap"      in obj_text: tags.append("ambush")
	if "patrol"    in obj_text or "sweep"     in obj_text: tags.append("patrol")
	if "guard"     in obj_text or "protect"   in obj_text: tags.append("guard")
	if "defend"    in obj_text or "hold"      in obj_text: tags.append("defend")
	if "sniper"    in obj_text or "overwatch" in obj_text: tags.append("sniper_nest")
	if "swarm"     in obj_text or "horde"     in obj_text: tags.append("swarm")
	if tags.is_empty(): tags.append("patrol")   # default behaviour

	return {
		"location": location,
		"theme":    theme,
		"category": theme_category(theme),
		"risk":     risk,
		"is_story": is_story,
		"tags":     tags,
		"obj_type": obj_type,
	}

# ──────────────────────────────────────────────────────────────────────────────
# Enemy count
# ──────────────────────────────────────────────────────────────────────────────

func enemy_count(risk: int, is_story: bool) -> int:
	# Scales from 2 (risk 1) to 8 (risk 10); story missions add two extra.
	var base := 2 + int(float(risk) * 0.65)
	if is_story: base += 2
	return clampi(base, 2, 10)

# ──────────────────────────────────────────────────────────────────────────────
# Subtype roster
# Each difficulty bracket has a role pool; we walk it cyclically for the count.
# Story missions override with a fully varied roster.
# ──────────────────────────────────────────────────────────────────────────────

func select_subtypes(count: int, risk: int, is_story: bool) -> Array[String]:
	var pool: Array[String]
	if   risk <= 3: pool = ["grunt", "grunt",  "heavy",    "grunt",   "grunt",    "heavy"  ]
	elif risk <= 6: pool = ["grunt", "heavy",  "grunt",    "sniper",  "elite",    "grunt"  ]
	elif risk <= 8: pool = ["grunt", "heavy",  "sniper",   "elite",   "psi",      "commander", "grunt", "heavy"]
	else:           pool = ["sniper","elite",  "psi",      "commander","heavy",   "elite",     "grunt", "sniper","commander","psi"]
	# Story missions always field the full mixed roster for narrative weight.
	if is_story:    pool = ["grunt", "heavy",  "sniper",   "elite",   "psi",      "commander", "sniper","elite", "heavy",    "grunt"]
	var result: Array[String] = []
	for i in range(count):
		result.append(pool[i % pool.size()])
	return result

# ──────────────────────────────────────────────────────────────────────────────
# Base stats per subtype
# These are the minimum values at risk = 1, before difficulty scaling.
# ──────────────────────────────────────────────────────────────────────────────

func base_stats(subtype: String) -> Dictionary:
	match subtype:
		"grunt":     return {"hp": 12, "defense": 4, "initiative": 14, "ap": 2}
		"heavy":     return {"hp": 22, "defense": 7, "initiative": 10, "ap": 2}
		"sniper":    return {"hp": 10, "defense": 3, "initiative": 17, "ap": 2}
		"elite":     return {"hp": 18, "defense": 6, "initiative": 15, "ap": 2}
		"commander": return {"hp": 26, "defense": 8, "initiative": 18, "ap": 2}
		"psi":       return {"hp": 11, "defense": 3, "initiative": 16, "ap": 2}
		_:           return {"hp": 12, "defense": 4, "initiative": 14, "ap": 2}

# ──────────────────────────────────────────────────────────────────────────────
# Difficulty scaling
# HP and defense scale 0%–60% above base across risk 1–10.
# Story missions add a further 20% on top.
# ──────────────────────────────────────────────────────────────────────────────

func scale_stats(b: Dictionary, risk: int, is_story: bool) -> Dictionary:
	var s := 1.0 + float(risk - 1) / 9.0 * 0.6
	if is_story: s += 0.2
	return {
		"hp":         maxi(1, int(float(b["hp"])      * s)),
		"defense":    maxi(1, int(float(b["defense"])  * s)),
		"initiative": b["initiative"],
		"ap":         b["ap"],
	}

# ──────────────────────────────────────────────────────────────────────────────
# Giant decision
# Non-humanoid categories — robots, starvers, and mutants — are eligible.
# Corp (including power armor), raider, and generic humanoids are never giant;
# their larger-looking artwork is purely aesthetic, not a physical size change.
# Vehicles handle their own giant logic in build_vehicles(). At most one giant per encounter.
# ──────────────────────────────────────────────────────────────────────────────

func should_be_giant(_subtype: String, category: String,
					  risk: int, is_story: bool, giant_used: bool) -> bool:
	if giant_used: return false   # one giant per encounter at most
	# Power armor and human corps are excluded even though they have bulky sprites;
	# they are still human-sized combatants.
	var eligible := category in ["robot", "starver", "mutant"]
	if not eligible: return false
	var p := 0.0
	if   is_story:  p = 0.50
	elif risk >= 8:  p = 0.30
	elif risk >= 6:  p = 0.14
	return randf() < p

func apply_giant(u: Dictionary) -> Dictionary:
	# Giants: 3× HP, 2× defense, -3 initiative (slow), 3.5× visual scale.
	u["hp"]         = u["hp"]     * 3
	u["max_hp"]     = u["max_hp"] * 3
	u["defense"]    = int(float(u["defense"]) * 2.0)
	u["initiative"] = maxi(1, int(u["initiative"]) - 3)
	u["size_scale"] = 3.5
	u["is_giant"]   = true
	return u

# ──────────────────────────────────────────────────────────────────────────────
# Enemy placement
# Assigns a non-overlapping grid cell to each unit based on subtype role and
# the behavior tags extracted from the briefing.
# ──────────────────────────────────────────────────────────────────────────────

func place_enemies(units: Array[Dictionary], obj_cell: Vector2i,
				   tags: Array, grid_cols: int, grid_rows: int) -> Array[Dictionary]:
	var occupied: Array[Vector2i] = []
	var result:   Array[Dictionary] = []
	var guard_obj   := "guard"       in tags or "defend" in tags
	var sniper_nest := "sniper_nest" in tags
	var swarm       := "swarm"       in tags
	var ambush      := "ambush"      in tags
	for i in range(units.size()):
		var u    := units[i].duplicate()
		var sub  := str(u.get("enemy_subtype", "grunt"))
		var cell := _find_cell(sub, i, u.get("is_giant", false),
							   obj_cell, guard_obj, sniper_nest, swarm, ambush,
							   occupied, grid_cols, grid_rows)
		occupied.append(cell)
		u["position"] = cell
		result.append(u)
	return result

func _find_cell(subtype: String, idx: int, _is_giant: bool,
				obj_cell: Vector2i, guard_obj: bool, sniper_nest: bool,
				swarm: bool, ambush: bool,
				occupied: Array[Vector2i], grid_cols: int, grid_rows: int) -> Vector2i:
	# Default spawn zone: enemy half of the grid (far ~45%).
	var x_min := int(grid_cols * 0.55)
	var x_max := grid_cols - 3
	var y_min := 2
	var y_max := grid_rows - 3

	# Subtype-specific positioning
	match subtype:
		"sniper":
			if sniper_nest:
				# Far corners — snipers nest at maximum depth.
				x_min = grid_cols - 7; x_max = grid_cols - 3
				if idx % 2 == 0: y_max = 8
				else:             y_min = grid_rows - 9
			else:
				x_min = int(grid_cols * 0.68)
		"commander":
			# Commanders stay behind the line.
			x_min = int(grid_cols * 0.72); x_max = grid_cols - 3
		"heavy":
			# Heavies anchor the front line.
			x_min = int(grid_cols * 0.55); x_max = int(grid_cols * 0.72)
		"psi":
			# PSI units hang back for range.
			x_min = int(grid_cols * 0.65)
		"grunt":
			if swarm:  x_min = int(grid_cols * 0.45)  # swarm surges forward
			if ambush: x_max = int(grid_cols * 0.62)  # ambush units wait mid-map

	if guard_obj and subtype in ["grunt", "heavy", "elite"]:
		# Guards cluster around the objective cell.
		var ox := obj_cell.x; var oy := obj_cell.y
		x_min = maxi(int(grid_cols * 0.50), ox - 5)
		x_max = mini(grid_cols - 3,          ox + 5)
		y_min = maxi(2,                       oy - 5)
		y_max = mini(grid_rows - 3,           oy + 5)

	# Try 60 random slots, then fall back to linear scan.
	for _a in range(60):
		var x := x_min + randi() % maxi(1, x_max - x_min + 1)
		var y := y_min + randi() % maxi(1, y_max - y_min + 1)
		var c := Vector2i(x, y)
		if c not in occupied: return c
	for x in range(x_min, x_max + 1):
		for y in range(y_min, y_max + 1):
			var c := Vector2i(x, y)
			if c not in occupied: return c
	return Vector2i(grid_cols - 3, 2 + idx)   # last-resort fallback

# ──────────────────────────────────────────────────────────────────────────────
# Objective record
# Maps the mission's objective_type to a visual label, an action key, and
# progress tracking. Elimination missions need no map marker.
# ──────────────────────────────────────────────────────────────────────────────

func build_objective(obj_type: String, grid_cols: int, grid_rows: int) -> Dictionary:
	# Place the objective in the far 62–82% of the X axis, random Y band.
	var ox := int(grid_cols * 0.62) + randi() % maxi(1, int(grid_cols * 0.20))
	var oy := int(grid_rows * 0.20) + randi() % maxi(1, int(grid_rows * 0.60))

	var label:           String
	var action_key:      String
	var progress_needed: int  = 1
	var needs_marker:    bool = true

	match obj_type:
		"data_with_detour", "data_theft", "data_extract", "intel_gather":
			label = "Hack Terminal";  action_key = "HACK"
		"extraction", "extract_vip":
			label = "Extract VIP";    action_key = "EXTRACT"
		"rescue_hostage", "rescue":
			label = "Free Hostage";   action_key = "RESCUE"
		"sabotage", "demolition", "destroy_target":
			label = "Sabotage";       action_key = "SABOTAGE"
		"assassination", "elimination", "kill_all":
			needs_marker = false;     label = "";  action_key = ""
		"steal_prototype", "theft", "heist":
			label = "Retrieve";       action_key = "RETRIEVE"
		"plant_explosive", "bomb_plant":
			label = "Plant Bomb";     action_key = "PLANT"
		"investigate", "search", "patrol":
			label = "Investigate";    action_key = "SEARCH"; progress_needed = 3
		"repair", "fix":
			label = "Repair";         action_key = "REPAIR"
		"activate", "access":
			label = "Activate";       action_key = "ACTIVATE"
		_:
			needs_marker = false;     label = "";  action_key = ""

	return {
		"cell":             Vector2i(ox, oy),
		"type":             obj_type,
		"label":            label,
		"action_key":       action_key,
		"progress_needed":  progress_needed,
		"needs_marker":     needs_marker,
		"interact_range":   2,   # grid cells within which the player can interact
	}

# ──────────────────────────────────────────────────────────────────────────────
# Vehicle system
# One agent VTOL + one faction-appropriate enemy vehicle per mission.
# Military faction vehicles may become Giant combat units instead of scenery.
# Mechs and drones are NOT vehicles (they are already enemy unit subtypes).
# ──────────────────────────────────────────────────────────────────────────────

func _is_military_faction(theme: String) -> bool:
	for fac: String in ["corp_37", "corp_samurai"]:
		if theme.begins_with(fac): return true
	return false

func _enemy_vehicle_texture_key(theme: String) -> String:
	if theme.begins_with("corp_samurai"): return "vehicle_enemy_corp_samurai"
	if theme.begins_with("corp_37"):      return "vehicle_enemy_corp_37"
	if theme.begins_with("raider"):       return "vehicle_enemy_raider"
	return ""   # mutant / starver have no vehicles

func _enemy_vehicle_subtype_label(theme: String) -> String:
	if theme.begins_with("corp_samurai"): return "TANK"
	if theme.begins_with("corp_37"):      return "APC"
	if theme.begins_with("raider"):       return "HAULER"
	return "VEHICLE"

func build_vehicles(analysis: Dictionary, giant_used: bool,
					grid_cols: int, grid_rows: int) -> Dictionary:
	var theme    := analysis["theme"]    as String
	var risk     := analysis["risk"]     as int
	var is_story := analysis["is_story"] as bool
	var mid_row  := grid_rows / 2

	# Agent VTOL — always present, decorative, left edge.
	# scale 3.5 so it looks impressively large without dominating the screen.
	var agent_vtol: Dictionary = {
		"name":        "VTOL",
		"role":        "vehicle",
		"kind":        "player",
		"hp":          60,
		"max_hp":      60,
		"stress":      0,
		"ap":          0,
		"defense":     10,
		"initiative":  0,
		"size_scale":  3.5,
		"is_vehicle":  true,
		"is_giant":    false,
		"vehicle_key": "vehicle_agent_vtol",
		"position":    Vector2i(2, mid_row),
	}

	var vkey := _enemy_vehicle_texture_key(theme)
	if vkey == "":
		# Non-vehicle factions — agent VTOL only.
		return {"agent_vehicle": agent_vtol, "enemy_vehicle": {}}

	# Decide whether the military vehicle becomes a Giant combat unit.
	var becomes_giant := false
	if _is_military_faction(theme) and not giant_used:
		if   is_story:   becomes_giant = randf() < 0.60
		elif risk >= 8:  becomes_giant = randf() < 0.40
		elif risk >= 6:  becomes_giant = randf() < 0.20

	var vh_hp  := 40 + risk * 8 + (20 if is_story else 0)
	var vh_def := 10 + risk

	# Decorative vehicles use scale 3.5; giant combat vehicles use 5.0.
	var enemy_veh: Dictionary = {
		"name":           "%s %s" % [theme.replace("_", " ").to_upper(), _enemy_vehicle_subtype_label(theme)],
		"role":           "vehicle",
		"kind":           "enemy",
		"hp":             vh_hp,
		"max_hp":         vh_hp,
		"stress":         0,
		"ap":             2,
		"defense":        vh_def,
		"initiative":     8,
		"size_scale":     5.0 if becomes_giant else 3.5,
		"is_vehicle":     true,
		"is_giant":       becomes_giant,
		"enemy_subtype":  _enemy_vehicle_subtype_label(theme).to_lower(),
		"enemy_theme":    theme,
		"status_effects": [],
		"vehicle_key":    vkey,
		"position":       Vector2i(grid_cols - 4, mid_row),
	}
	# If the vehicle fights it uses heavy subtype stats.
	if becomes_giant:
		enemy_veh["enemy_subtype"] = "heavy"

	return {"agent_vehicle": agent_vtol, "enemy_vehicle": enemy_veh}

# ──────────────────────────────────────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────────────────────────────────────

func generate(handoff: Dictionary, grid_cols: int, grid_rows: int) -> Dictionary:
	var mission: Dictionary = handoff.get("mission", {}) as Dictionary
	var map:     Dictionary = handoff.get("map",     {}) as Dictionary
	var analysis := analyze_briefing(mission, map)

	var risk:     int     = analysis["risk"]     as int
	var is_story: bool    = analysis["is_story"] as bool
	var theme:    String  = analysis["theme"]    as String
	var category: String  = analysis["category"] as String
	var tags:     Array   = analysis["tags"]     as Array
	var obj_type: String  = analysis["obj_type"] as String

	var count    := enemy_count(risk, is_story)
	var subtypes := select_subtypes(count, risk, is_story)

	var units:      Array[Dictionary] = []
	var giant_used := false

	# Base visual scale by category so sprites feel appropriately sized.
	# Power-armor corp units have bulkier art; reduce their token slightly so
	# they read as human-sized. Robot corps are mechanically larger than humans.
	var base_scale: float
	match category:
		"corp":
			# Distinguish power-armor (visually oversized art) from regular corp.
			if "power_armor" in theme: base_scale = 0.82
			elif "robot" in theme:     base_scale = 1.15
			else:                      base_scale = 1.0
		"robot":   base_scale = 1.2
		"mutant":  base_scale = 1.1
		_:         base_scale = 1.0

	for i in range(count):
		var sub   := subtypes[i]
		var b     := base_stats(sub)
		var stats := scale_stats(b, risk, is_story)
		var giant := should_be_giant(sub, category, risk, is_story, giant_used)
		if giant: giant_used = true

		var u: Dictionary = {
			"name":           "%s %02d" % [theme.replace("_", " ").to_upper(), i + 1],
			"role":           "enemy",
			"hp":             stats["hp"],
			"max_hp":         stats["hp"],
			"stress":         0,
			"ap":             stats["ap"],
			"initiative":     stats["initiative"],
			"kind":           "enemy",
			"enemy_subtype":  sub,
			"enemy_theme":    theme,
			"status_effects": [],
			"defense":        stats["defense"],
			"size_scale":     base_scale,
			"is_giant":       false,
			"position":       Vector2i.ZERO,
		}
		if giant:
			u = apply_giant(u)
		units.append(u)

	var objective := build_objective(obj_type, grid_cols, grid_rows)
	var placed    := place_enemies(units, objective["cell"] as Vector2i,
								  tags, grid_cols, grid_rows)

	# Build vehicles — enemy vehicle may become a Giant combat unit.
	var vehicles   := build_vehicles(analysis, giant_used, grid_cols, grid_rows)
	var enemy_veh  := vehicles.get("enemy_vehicle", {}) as Dictionary
	if not enemy_veh.is_empty() and enemy_veh.get("is_giant", false):
		# Vehicle enters combat as a Giant — add to enemy_units, not scenery.
		placed.append(enemy_veh)
		vehicles["enemy_vehicle"] = {}   # nothing left to show as decorative token

	return {"enemy_units": placed, "objective": objective, "vehicles": vehicles}
