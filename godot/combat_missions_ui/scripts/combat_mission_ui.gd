extends Control
## CombatRoot — owns all game state, builds the scene tree programmatically,
## and coordinates Battlefield / UnitToken / HudController / PhaseBanner /
## AudioManager / MissionResults via CombatSignals.
## All combat logic (unit building, AI, damage, initiative) is preserved intact.

# ─── Palette ──────────────────────────────────────────────────────────────────
const PANEL      := Color(0.02, 0.05, 0.08, 0.94)
const NEON       := Color(0.10, 0.95, 0.72, 1.0)
const TEXT       := Color(0.84, 0.95, 0.92, 1.0)
const WARN       := Color(1.00, 0.72, 0.22, 1.0)
const PLAYER_COL := Color(0.10, 0.95, 0.72, 1.0)
const ENEMY_COL  := Color(1.00, 0.34, 0.30, 1.0)
const ROLE_SNIPER  := Color(0.56, 0.88, 1.0,  1.0)
const ROLE_PSI     := Color(0.76, 0.56, 1.0,  1.0)
const ROLE_SAMURAI := Color(0.28, 1.0,  0.74, 1.0)

const ACTIONS: Array[String] = ["MOVE", "MELEE", "FIRE", "PSI", "DEFEND", "OVERWATCH", "END TURN"]

# Named action → mechanics. Covers every action name that can appear in
# a squad member's available_actions list from the handoff JSON.
const _ACTION_DEFS: Dictionary = {
	"Move":          {"type": "MOVE",     "range": 0, "damage": 0, "heal": 0, "ap": 0},
	"Defend":        {"type": "DEFEND",   "range": 0, "damage": 0, "heal": 0, "ap": 1},
	"Overwatch":     {"type": "OVERWATCH","range": 0, "damage": 0, "heal": 0, "ap": 1},
	"Pistol Shot":   {"type": "FIRE",     "range": 3, "damage": 3, "heal": 0, "ap": 1},
	"Rifle Burst":   {"type": "FIRE",     "range": 6, "damage": 5, "heal": 0, "ap": 1},
	"Plasma Burst":  {"type": "FIRE",     "range": 5, "damage": 8, "heal": 0, "ap": 2},
	"Katana Slash":  {"type": "MELEE",    "range": 1, "damage": 7, "heal": 0, "ap": 1},
	"Blade Strike":  {"type": "MELEE",    "range": 1, "damage": 5, "heal": 0, "ap": 1},
	"Servo Punch":   {"type": "MELEE",    "range": 1, "damage": 9, "heal": 0, "ap": 1},
	"Psi Focus":     {"type": "PSI_HEAL", "range": 0, "damage": 0, "heal": 0, "ap": 1, "stress_relief": 25},
	"Trauma Patch":  {"type": "HEAL",     "range": 0, "damage": 0, "heal": 12,"ap": 1},
	"Missile Salvo": {"type": "FIRE_AOE", "range": 8, "damage": 6, "heal": 0, "ap": 2, "aoe_radius": 2},
}
const GRID_COLS := 40
const GRID_ROWS := 28
const TOP_BAR_H    : float = 44.0
const RIGHT_PANEL_W: float = 340.0
const STRIP_H      : float = 158.0
const LEFT_MARGIN  : float = 70.0

# ─── Script preloads (avoid class_name registration order issues) ─────────────
const _BFScript  = preload("res://scripts/battlefield.gd")
const _HUDScript = preload("res://scripts/hud_controller.gd")
const _BNRScript = preload("res://scripts/phase_banner.gd")
const _AUDScript = preload("res://scripts/audio_manager.gd")
const _RESScript = preload("res://scripts/mission_results.gd")
const _TOKScript = preload("res://scripts/unit_token.gd")
const _ENCScript = preload("res://scripts/encounter_generator.gd")

# ─── Component refs (untyped to avoid class-name scope errors) ────────────────
var _battlefield                 = null   # Battlefield
var _units_layer   : Node2D      = null
var _hud                         = null   # HudController
var _hud_layer     : CanvasLayer = null
var _banner                      = null   # PhaseBanner
var _audio                       = null   # AudioManager
var _results                     = null   # MissionResults
var _unit_tokens   : Dictionary  = {}    # "p0" / "e1" → UnitToken instance

# ─── Handoff + assets ─────────────────────────────────────────────────────────
var handoff         : Dictionary = {}
var handoff_path    := "runtime/godot_combat/mission_handoff.json"
var project_root    : String = ""
var unit_textures   : Dictionary = {}
var portrait_textures: Dictionary = {}
var map_texture     : Texture2D = null

# ─── Game state ───────────────────────────────────────────────────────────────
var status_line   := "Waiting for CyberCity handoff."
var battle_started: bool  = false
var battle_ended  : bool  = false
var elapsed_time  : float = 0.0
var selected_action: String = "MOVE"
var pending_end_turn_confirmation: bool = false
var show_combat_log: bool = false
var turn_side     : String = "player"
var turn_number   : int    = 1
var active_player_index: int = 0
var selected_target_index: int = 0
var enemy_turn_timer  : float = 0.0
var enemy_turn_duration: float = 0.9
var combat_log    : Array[String] = []
var deploy_rect   : Rect2 = Rect2()
var battlefield_rect: Rect2 = Rect2()
var objective           : Dictionary = {}   # cell, type, label, action_key, …
var objective_progress  : int        = 0
var objective_completed : bool       = false
var player_units    : Array[Dictionary] = []
var enemy_units     : Array[Dictionary] = []
var vehicle_units   : Array[Dictionary] = []   # decorative only; not in combat
var initiative_entries: Array[Dictionary] = []
var overwatch_indices: Array[int] = []
var defend_indices   : Array[int] = []
var cover_nodes      : Array[Dictionary] = []

# ─── Camera / zoom / pan ──────────────────────────────────────────────────────
const _ZOOM_MIN        := 0.25
const _ZOOM_MAX        := 3.0
const _DRAG_THRESHOLD  := 8.0   # pixels moved before a click becomes a pan
var _camera       : Camera2D  = null
var _map_root     : Node2D    = null
var _pan_active   : bool      = false
var _drag_started : bool      = false
var _pan_start_screen: Vector2 = Vector2.ZERO
var _pan_start_cam   : Vector2 = Vector2.ZERO

# ─── Lifecycle ────────────────────────────────────────────────────────────────

func _ready() -> void:
	set_process(true)
	mouse_filter = Control.MOUSE_FILTER_STOP
	# Set the scene clear colour here so it is unaffected by Camera2D transforms.
	# draw_rect inside _draw() is subject to the camera's world-space transform,
	# which makes it appear as a scaled rectangle rather than a full-screen fill.
	RenderingServer.set_default_clear_color(Color(0.005, 0.015, 0.025, 1.0))
	_read_args()
	_load_handoff()
	_load_unit_textures()
	_load_map_and_portraits()
	_build_children()
	_connect_signals()
	_seed_combat_state()
	call_deferred("_start_combat", "AUTO-DEPLOY")
	queue_redraw()

func _process(delta: float) -> void:
	if not battle_started:
		elapsed_time += delta
		queue_redraw()
		return
	elapsed_time += delta
	if turn_side == "enemy":
		enemy_turn_timer = maxf(0.0, enemy_turn_timer - delta)
		if enemy_turn_timer <= 0.0:
			_resolve_enemy_turn()

func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED and _battlefield != null and not battle_ended:
		_battlefield.resize(size * 2.0)
		if _hud != null:
			_hud.set_deferred("size", size)
			_hud.position = Vector2.ZERO
			_hud._reposition_buttons()
		# Re-centre the camera whenever the window is resized (e.g. Win32 overlay
		# repositions the window to match Arcade's client area).  iso_tw changes
		# with the new viewport size so the camera must be recalculated.
		if _camera != null:
			_camera.position = _battlefield.cell_to_world(Vector2i(GRID_COLS / 2, GRID_ROWS / 2))
			_camera.zoom = Vector2.ONE * _overview_zoom()
		if battle_started:
			_resize_tokens()
			_sync_display()

# ─── Child-node construction ──────────────────────────────────────────────────

func _build_children() -> void:
	# MapRoot: single transform node wrapping battlefield + units.
	# Camera2D lives here so zoom/pan affects only the map, not the HUD.
	_map_root = Node2D.new()
	_map_root.name = "MapRoot"
	add_child(_map_root)

	_camera = Camera2D.new()
	_camera.name = "Camera2D"
	_map_root.add_child(_camera)
	_camera.make_current()

	# Battlefield draws map + grid (behind units)
	_battlefield = _BFScript.new()
	_battlefield.name = "Battlefield"
	_map_root.add_child(_battlefield)

	# Units layer: parent for all UnitToken nodes
	_units_layer = Node2D.new()
	_units_layer.name = "UnitsLayer"
	_map_root.add_child(_units_layer)

	# HUD on CanvasLayer 1 — hidden until combat starts
	_hud_layer = CanvasLayer.new()
	_hud_layer.layer   = 1
	_hud_layer.visible = false
	add_child(_hud_layer)
	_hud = _HUDScript.new()
	_hud.name = "HudController"
	_hud_layer.add_child(_hud)

	# Phase banner on CanvasLayer 2
	var banner_layer := CanvasLayer.new()
	banner_layer.layer = 2
	add_child(banner_layer)
	_banner = _BNRScript.new()
	_banner.name = "PhaseBanner"
	banner_layer.add_child(_banner)

	# Audio manager (Node, no CanvasLayer needed)
	_audio = _AUDScript.new()
	_audio.name = "AudioManager"
	add_child(_audio)

	# Mission results on CanvasLayer 3
	var results_layer := CanvasLayer.new()
	results_layer.layer = 3
	add_child(results_layer)
	_results = _RESScript.new()
	_results.name    = "MissionResults"
	_results.visible = false
	results_layer.add_child(_results)

	# CRT post-FX on CanvasLayer 10
	var crt_layer := CanvasLayer.new()
	crt_layer.layer = 10
	add_child(crt_layer)
	var crt_rect := ColorRect.new()
	crt_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	crt_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var crt_shader := load("res://shaders/crt.gdshader")
	if crt_shader != null:
		var crt_mat := ShaderMaterial.new()
		crt_mat.shader = crt_shader as Shader
		crt_rect.material = crt_mat
	crt_layer.add_child(crt_rect)

func _connect_signals() -> void:
	CombatSignals.action_pressed.connect(_on_action_pressed)
	CombatSignals.cell_clicked.connect(_on_cell_clicked)
	CombatSignals.unit_clicked.connect(_on_unit_clicked)

# ─── Display sync ─────────────────────────────────────────────────────────────

func _sync_display() -> void:
	if battle_ended: return
	_refresh_initiative()

	# Objective proximity hint — overrides status line when actionable.
	if turn_side == "player" and not objective.is_empty() \
			and objective.get("needs_marker", false) and not objective_completed:
		var active := _current_active_player()
		if not active.is_empty() and int(active.get("ap", 0)) > 0:
			var apos     := _cell_position(active)
			var obj_cell := objective["cell"] as Vector2i
			var dist     := absi(obj_cell.x - apos.x) + absi(obj_cell.y - apos.y)
			var needed   := int(objective.get("progress_needed", 1))
			if dist <= int(objective.get("interact_range", 2)):
				status_line = "[%s] click objective to %s (%d/%d)" % [
					str(active.get("name", "Agent")),
					str(objective.get("label", "interact")),
					objective_progress, needed]

	# Battlefield range highlights
	if turn_side == "player":
		var active := _current_active_player()
		if not active.is_empty():
			var origin := _cell_position(active)
			var atype  := _action_type(selected_action)
			if atype == "MOVE":
				var budget := maxi(1, int(active.get("ap", 2)))
				_battlefield.show_move_range(_battlefield.reachable_cells(origin, budget), origin)
			elif atype in ["FIRE", "MELEE", "FIRE_AOE"]:
				var rng := _action_range(selected_action)
				if rng == 0:
					rng = _role_attack_range(str(active.get("role", "")), selected_action)
				_battlefield.show_attack_range(_battlefield.reachable_cells(origin, rng))
			else:
				_battlefield.clear_highlights()
		else:
			_battlefield.clear_highlights()
	else:
		_battlefield.clear_highlights()

	# Token data + flags (NOT position — position is managed by spawn/move code)
	for i in range(player_units.size()):
		var key := "p%d" % i
		if not _unit_tokens.has(key): continue
		var tok = _unit_tokens[key]
		if not is_instance_valid(tok): _unit_tokens.erase(key); continue
		var u   := player_units[i] as Dictionary
		tok.update_data(u)
		tok.set_active(i == active_player_index and turn_side == "player")
		tok.has_overwatch = i in overwatch_indices
		tok.has_defend    = i in defend_indices
		tok.set_targeted(false)
		tok.visible = int(u.get("hp", 0)) > 0
	for j in range(enemy_units.size()):
		var key := "e%d" % j
		if not _unit_tokens.has(key): continue
		var tok = _unit_tokens[key]
		if not is_instance_valid(tok): _unit_tokens.erase(key); continue
		var u   := enemy_units[j] as Dictionary
		tok.update_data(u)
		tok.set_active(false)
		tok.set_targeted(j == selected_target_index \
						  and selected_action in ["FIRE", "MELEE", "PSI"] \
						  and turn_side == "player")
		tok.visible = int(u.get("hp", 0)) > 0

	_hud.show_log = show_combat_log
	_hud.update_state(player_units, enemy_units, initiative_entries,
					  active_player_index, selected_action,
					  turn_side, turn_number, combat_log,
					  portrait_textures, status_line)
	queue_redraw()

func _resize_tokens() -> void:
	# Called after NOTIFICATION_RESIZED: update every live token's card dimensions
	# and world position to match the new iso_tw.
	var cs := Vector2(_battlefield.iso_tw * 2.0, _battlefield.iso_tw * 2.0)
	for key in _unit_tokens.keys():
		var tok = _unit_tokens[key]
		if not is_instance_valid(tok):
			_unit_tokens.erase(key)
			continue
		tok.cell_size = cs
		tok._recalc_dims()
		tok.queue_redraw()
	for i in range(player_units.size()):
		var k := "p%d" % i
		if _unit_tokens.has(k) and is_instance_valid(_unit_tokens[k]):
			_unit_tokens[k].position = _battlefield.cell_to_world(_cell_position(player_units[i]))
	for j in range(enemy_units.size()):
		var k := "e%d" % j
		if _unit_tokens.has(k) and is_instance_valid(_unit_tokens[k]):
			_unit_tokens[k].position = _battlefield.cell_to_world(_cell_position(enemy_units[j]))
	for vi in range(vehicle_units.size()):
		var k := "v%d" % vi
		if _unit_tokens.has(k) and is_instance_valid(_unit_tokens[k]):
			_unit_tokens[k].position = _battlefield.cell_to_world(_cell_position(vehicle_units[vi]))

func _spawn_all_tokens() -> void:
	# Destroy old tokens first
	for key in _unit_tokens.keys():
		var tok = _unit_tokens[key]
		if is_instance_valid(tok):
			tok.queue_free()
	_unit_tokens.clear()

	# Use isometric tile dimensions so token radius scales to the diamond tile,
	# not the rectangular cell bounding box.
	var cell_size := Vector2(
		_battlefield.iso_tw * 2.0,   # full iso tile width
		_battlefield.iso_tw * 2.0    # treat as square; token uses x for radius
	)

	for i in range(player_units.size()):
		var u    := player_units[i] as Dictionary
		var tkey := _unit_texture_key(u, false)
		var tex  := unit_textures.get(tkey, null) as Texture2D
		var tok  = _TOKScript.new()
		tok.name = "Player%d" % i
		_units_layer.add_child(tok)
		tok.setup(u, i, false, tex, cell_size)
		var wp0 : Vector2 = _battlefield.cell_to_world(_cell_position(u))
		tok.position = wp0
		_unit_tokens["p%d" % i] = tok

	for j in range(enemy_units.size()):
		var u    := enemy_units[j] as Dictionary
		var tkey := _unit_texture_key(u, true)
		var tex  := unit_textures.get(tkey, null) as Texture2D
		var tok  = _TOKScript.new()
		tok.name = "Enemy%d" % j
		_units_layer.add_child(tok)
		tok.setup(u, j, true, tex, cell_size)
		var wp1 : Vector2 = _battlefield.cell_to_world(_cell_position(u))
		tok.position = wp1
		_unit_tokens["e%d" % j] = tok

	# Decorative vehicle tokens — use id ≥ 1000 so click handler ignores them.
	for vi in range(vehicle_units.size()):
		var v    := vehicle_units[vi] as Dictionary
		var vkey := str(v.get("vehicle_key", "vehicle_agent_vtol"))
		var tex  := unit_textures.get(vkey, null) as Texture2D
		var is_ev := str(v.get("kind", "player")) == "enemy"
		var tok  = _TOKScript.new()
		tok.name = "Vehicle%d" % vi
		_units_layer.add_child(tok)
		# id ≥ 1000 signals "vehicle" to _on_unit_clicked so it is silently ignored.
		tok.setup(v, 1000 + vi, is_ev, tex, cell_size)
		tok.position = _battlefield.cell_to_world(_cell_position(v))
		_unit_tokens["v%d" % vi] = tok

# ─── Handoff & assets ─────────────────────────────────────────────────────────

func _read_args() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	for index in range(args.size()):
		if args[index] == "--handoff" and index + 1 < args.size():
			handoff_path = args[index + 1]

func _load_handoff() -> void:
	if not FileAccess.file_exists(handoff_path):
		status_line = "No handoff JSON at %s" % handoff_path
		return
	var text := FileAccess.get_file_as_string(handoff_path)
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		status_line = "Handoff JSON unreadable."
		return
	handoff = parsed
	var base_from_json := str(handoff.get("asset_base_dir", "")).strip_edges()
	if base_from_json != "":
		project_root = base_from_json
	else:
		project_root = handoff_path.get_base_dir().get_base_dir().get_base_dir()
	status_line = ""

func _load_unit_textures() -> void:
	unit_textures = {}
	# ── Agent tokens: 25 diverse sprites, one per roster slot via name hash ──
	var _agent_names: Array[String] = [
		"neon_blade", "longcoat_gunner", "magenta_pistol", "trench_sniper",
		"psi_doctor", "street_medic", "hooded_infiltrator", "holo_hacker",
		"blue_mohawk_scout", "ronin_duelist", "rail_sniper", "violet_fixer",
		"silver_pistol", "armored_vanguard", "chrome_medic", "heavy_breacher",
		"yellow_strike", "red_enforcer", "drone_handler", "cyber_doc",
		"twin_blade_adept", "veteran_inquisitor", "dreadlock_rifle",
		"hooded_psion", "redline_runner",
	]
	for i in range(_agent_names.size()):
		var n  := i + 1
		var key  := "agent_diverse_%02d" % n
		var hi   := "assets/units/agent_diverse_%02d_%s_512.png" % [n, _agent_names[i]]
		var lo   := "assets/units/agent_diverse_%02d_%s.png"     % [n, _agent_names[i]]
		_try_load_tex(key, hi)
		if not unit_textures.has(key):
			_try_load_tex(key, lo)
	# Role-based legacy fallbacks.
	_try_load_tex("agent_samurai", "assets/units/agent_samurai_512.png")
	if not unit_textures.has("agent_samurai"):
		_try_load_tex("agent_samurai", "assets/units/agent_samurai.png")
	_try_load_tex("agent_psi", "assets/units/agent_psi_512.png")
	if not unit_textures.has("agent_psi"):
		_try_load_tex("agent_psi", "assets/units/agent_psi.png")

	# ── Enemy generic fallbacks ───────────────────────────────────────────────
	var base: Dictionary = {
		"enemy_grunt":     "assets/units/enemy_grunt_512.png",
		"enemy_heavy":     "assets/units/enemy_heavy_512.png",
		"enemy_elite":     "assets/units/enemy_elite_512.png",
		"enemy_commander": "assets/units/enemy_commander_512.png",
		"enemy_sniper":    "assets/units/enemy_elite_512.png",
		"enemy_psi":       "assets/units/enemy_elite_512.png",
	}
	for key: String in base:
		_try_load_tex(key, str(base[key]))
		if not unit_textures.has(key):
			_try_load_tex(key, str(base[key]).replace("_512.png", ".png"))

	var theme := str(_mission_data().get("enemy_theme", "")).to_lower().replace(" ", "_")
	if theme == "" or theme == "generic":
		return

	# Standard subtypes — themed sprites exist for all factions.
	for sub: String in ["grunt", "heavy", "elite", "commander"]:
		_try_load_tex("enemy_%s_%s" % [theme, sub],
					  "assets/units/enemy_%s_%s_512.png" % [theme, sub])
		if not unit_textures.has("enemy_%s_%s" % [theme, sub]):
			_try_load_tex("enemy_%s_%s" % [theme, sub],
						  "assets/units/enemy_%s_%s.png" % [theme, sub])

	# Sniper variant — named sprites where available, else reuse elite.
	var sniper_sprite: Dictionary = {
		"raider":       "assets/units/enemy_raider_04_scrap_sniper.png",
		"mutant":       "assets/units/enemy_mutant_02_spine_stalker.png",
		"starver":      "assets/units/enemy_starver_elite_512.png",
		"corp_37":      "assets/units/enemy_corp_37_elite_512.png",
		"corp_samurai": "assets/units/enemy_corp_samurai_elite_512.png",
	}
	if sniper_sprite.has(theme):
		_try_load_tex("enemy_%s_sniper" % theme, str(sniper_sprite[theme]))
	if not unit_textures.has("enemy_%s_sniper" % theme):
		var elite_key := "enemy_%s_elite" % theme
		if unit_textures.has(elite_key):
			unit_textures["enemy_%s_sniper" % theme] = unit_textures[elite_key]

	# Psi variant — named sprites where available, else reuse elite.
	var psi_sprite: Dictionary = {
		"mutant":       "assets/units/enemy_mutant_03_acid_psychic.png",
		"raider":       "assets/units/enemy_raider_10_dust_preacher.png",
		"starver":      "assets/units/enemy_starver_07_gasmask.png",
		"corp_37":      "assets/units/enemy_corp_37_robot_support.png",
		"corp_samurai": "assets/units/enemy_corp_samurai_robot_support.png",
	}
	if psi_sprite.has(theme):
		_try_load_tex("enemy_%s_psi" % theme, str(psi_sprite[theme]))
	if not unit_textures.has("enemy_%s_psi" % theme):
		var elite_key := "enemy_%s_elite" % theme
		if unit_textures.has(elite_key):
			unit_textures["enemy_%s_psi" % theme] = unit_textures[elite_key]

	# Vehicle textures — agent VTOL + faction-specific enemy ground vehicles.
	# Mechs and drones are NOT vehicles and are not loaded here.
	var vehicle_map: Dictionary = {
		"vehicle_agent_vtol":       "assets/units/vehicle_aerial_military_01_vtol_gunship_512.png",
		"vehicle_enemy_corp_37":    "assets/units/vehicle_terrestrial_military_03_apc_512.png",
		"vehicle_enemy_corp_samurai": "assets/units/vehicle_terrestrial_military_01_battle_tank_512.png",
		"vehicle_enemy_raider":     "assets/units/vehicle_terrestrial_civil_07_cargo_hauler_512.png",
	}
	for vk: String in vehicle_map:
		_try_load_tex(vk, str(vehicle_map[vk]))

func _asset_path(rel: String) -> String:
	if rel.begins_with("/") or (rel.length() > 1 and rel[1] == ":"):
		return rel
	if project_root == "":
		return rel
	return project_root.path_join(rel)

func _load_tex(path: String) -> Texture2D:
	var full := _asset_path(path)
	if not FileAccess.file_exists(full):
		return null
	var img := Image.load_from_file(full)
	if img == null:
		return null
	return ImageTexture.create_from_image(img)

func _try_load_tex(key: String, path: String) -> void:
	var tex := _load_tex(path)
	if tex != null:
		unit_textures[key] = tex

func _unit_texture_key(unit: Dictionary, is_enemy: bool) -> String:
	if not is_enemy:
		# Deterministic token: same agent name always maps to the same sprite.
		var agent_name := str(unit.get("name", "")).strip_edges()
		if agent_name != "":
			var idx := (agent_name.hash() & 0x7FFFFFFF) % 25 + 1
			var key := "agent_diverse_%02d" % idx
			if unit_textures.has(key):
				return key
		# Fallback: role-based sprite.
		var role := str(unit.get("role", "samurai")).to_lower()
		for candidate: String in ["agent_%s" % role, "agent_psi", "agent_samurai"]:
			if unit_textures.has(candidate):
				return candidate
		return "agent_samurai"
	var theme := str(unit.get("enemy_theme", "")).to_lower().replace(" ", "_")
	var sub   := str(unit.get("enemy_subtype", "grunt")).to_lower()
	# Themed key first (covers all subtypes including sniper/psi loaded above).
	if theme != "" and theme != "generic":
		var themed := "enemy_%s_%s" % [theme, sub]
		if unit_textures.has(themed):
			return themed
	# Generic fallback (enemy_grunt / enemy_heavy / enemy_elite /
	# enemy_commander / enemy_sniper / enemy_psi).
	var generic := "enemy_%s" % sub
	if unit_textures.has(generic):
		return generic
	return "enemy_grunt"

func _load_map_and_portraits() -> void:
	var map_path := str(_map_data().get("path", ""))
	if map_path != "":
		map_texture = _load_tex(map_path)
	portrait_textures = {}
	var squad_raw: Variant = handoff.get("squad", [])
	if typeof(squad_raw) == TYPE_ARRAY:
		for entry: Variant in squad_raw as Array:
			if typeof(entry) != TYPE_DICTIONARY: continue
			var agent := entry as Dictionary
			var portrait_path := str(agent.get("portrait_path", ""))
			var agent_name    := str(agent.get("name", ""))
			if portrait_path != "" and agent_name != "":
				var tex := _load_tex(portrait_path)
				if tex != null:
					portrait_textures[agent_name] = tex

# ─── Layout helper (kept for handoff scene) ──────────────────────────────────

func _layout_combat_hud() -> void:
	battlefield_rect = Rect2(
		LEFT_MARGIN, TOP_BAR_H + 8.0,
		maxf(300.0, size.x - RIGHT_PANEL_W - LEFT_MARGIN - 10.0),
		maxf(200.0, size.y - TOP_BAR_H - STRIP_H - 20.0))

# ─── Draw entry ───────────────────────────────────────────────────────────────

func _draw() -> void:
	if battle_started:
		return   # components handle all remaining drawing
	_draw_panel(Rect2(42, 36, size.x - 84, size.y - 72))
	_draw_handoff_scene()
	_draw_text(status_line, Vector2(74, size.y - 74), 15, NEON)

func _draw_panel(rect: Rect2) -> void:
	draw_rect(rect, PANEL, true)
	draw_rect(rect, NEON, false, 2.0)

# ─── Handoff scene ────────────────────────────────────────────────────────────

func _draw_handoff_scene() -> void:
	var mission  := _mission_data()
	var campaign := _campaign_data()
	var map_data := _map_data()
	_draw_text("CYBERCITY 2085 // GODOT COMBAT UI", Vector2(72, 82), 26, NEON)
	_draw_text(str(mission.get("title", "TACTICAL INSERTION")).to_upper(), Vector2(72, 126), 34, TEXT)
	_draw_text("%s • Risk %s • %s" % [
			mission.get("target_faction", "Unknown"), mission.get("risk_level", "?"),
			map_data.get("label", "unmapped site")], Vector2(74, 166), 18, WARN)
	_draw_text(str(mission.get("objective_text", "Complete the objective.")),
			   Vector2(74, 208), 20, TEXT)
	_draw_text("Campaign: %s / %s" % [
			campaign.get("corp_name", "AEGIS"), campaign.get("city_name", "Neo-Chrome City")],
			   Vector2(74, 246), 16, TEXT)
	_draw_squad(Vector2(74, 308))
	_draw_actions_preview(Vector2(size.x - 410, 308))
	_draw_deploy_prompt()

func _draw_deploy_prompt() -> void:
	var rect := Rect2(72, size.y - 166, 260, 44)
	deploy_rect = rect
	draw_rect(rect, Color(0.04, 0.22, 0.17, 0.95), true)
	draw_rect(rect, NEON, false, 1.5)
	_draw_text("DEPLOY  [Enter]", rect.position + Vector2(16, 28), 16, TEXT)
	_draw_text("Click to begin combat.", Vector2(74, size.y - 116), 14, WARN)

func _draw_squad(origin: Vector2) -> void:
	_draw_text("DEPLOYED AGENTS", origin, 20, NEON)
	var squad: Array = handoff.get("squad", [])
	if squad.is_empty():
		_draw_text("No agents in handoff.", origin + Vector2(0, 38), 16, WARN)
		return
	for index in range(mini(squad.size(), 6)):
		var agent: Dictionary = squad[index]
		var y: float = origin.y + 42 + index * 48
		_draw_text("%s  [%s]  HP %s/%s  Stress %s" % [
				agent.get("name", "Agent"), agent.get("role", "unit"),
				agent.get("hp", 0), agent.get("max_hp", 0), agent.get("stress", 0)],
				Vector2(origin.x, y), 17, TEXT)

func _draw_actions_preview(origin: Vector2) -> void:
	_draw_text("TACTICAL DECK", origin, 20, NEON)
	for index in range(ACTIONS.size()):
		var rect := Rect2(origin.x, origin.y + 36 + index * 38, 260, 28)
		draw_rect(rect, Color(0.03, 0.08, 0.08, 0.6), true)
		draw_rect(rect, Color(0.25, 0.7, 0.62, 0.5), false, 1.0)
		_draw_text(ACTIONS[index], rect.position + Vector2(10, 19), 13, TEXT)

# ─── Input ────────────────────────────────────────────────────────────────────

func _gui_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var ke := event as InputEventKey
		match ke.keycode:
			KEY_ESCAPE:
				get_tree().quit()
				accept_event()
			KEY_TAB:
				if battle_started and turn_side == "player":
					_cycle_active_unit()
				accept_event()
			KEY_L:
				show_combat_log = not show_combat_log
				if _hud != null: _hud.show_log = show_combat_log
				queue_redraw()
				accept_event()
			KEY_T:
				if battle_started and turn_side == "player":
					_execute_action("END TURN")
				accept_event()
			KEY_ENTER, KEY_KP_ENTER:
				if not battle_started:
					_start_combat("ENTER")
				elif pending_end_turn_confirmation:
					_end_player_turn()
				elif _action_type(selected_action) in ["FIRE", "MELEE", "FIRE_AOE", "PSI_HEAL", "HEAL"]:
					_resolve_selected_attack()
				accept_event()

	if event is InputEventMouseButton and event.pressed \
			and event.button_index == MOUSE_BUTTON_LEFT:
		var me    := event as InputEventMouseButton
		var point := me.position
		if not battle_started:
			if deploy_rect.has_point(point):
				_start_combat("DEPLOY")
				accept_event()

# ─── Camera zoom / pan ───────────────────────────────────────────────────────
# _input() runs before _unhandled_input() on all nodes, so consuming a
# LEFT-UP here prevents battlefield / token _unhandled_input() from treating
# a drag-release as a cell/unit click.

func _input(event: InputEvent) -> void:
	if not battle_started or battle_ended or _camera == null: return
	if event is InputEventMouseButton:
		var mbe := event as InputEventMouseButton
		match mbe.button_index:
			MOUSE_BUTTON_WHEEL_UP:
				if mbe.pressed:
					_zoom_at(mbe.position, 1.12)
					get_viewport().set_input_as_handled()
			MOUSE_BUTTON_WHEEL_DOWN:
				if mbe.pressed:
					_zoom_at(mbe.position, 1.0 / 1.12)
					get_viewport().set_input_as_handled()
			MOUSE_BUTTON_LEFT:
				if mbe.pressed:
					_pan_active   = true
					_drag_started = false
					_pan_start_screen = mbe.position
					_pan_start_cam    = _camera.position
					# Don't consume — could still be a plain click.
				else:
					if _drag_started:
						# Was a drag; consume release so children don't fire a click.
						_battlefield.pan_lock = false
						get_viewport().set_input_as_handled()
					_pan_active   = false
					_drag_started = false
	elif event is InputEventMouseMotion and _pan_active:
		var mme  := event as InputEventMouseMotion
		var dist := (mme.position - _pan_start_screen).length()
		if _drag_started or dist > _DRAG_THRESHOLD:
			if not _drag_started:
				_drag_started = true
				_battlefield.pan_lock = true
			var delta := (mme.position - _pan_start_screen) / _camera.zoom.x
			_camera.position = _pan_start_cam - delta
			get_viewport().set_input_as_handled()

func _zoom_at(cursor_screen: Vector2, factor: float) -> void:
	var old_zoom := _camera.zoom.x
	var new_zoom := clampf(old_zoom * factor, _ZOOM_MIN, _ZOOM_MAX)
	if absf(new_zoom - old_zoom) < 0.001: return
	var vp_center   := size * 0.5
	# World point that must stay under the cursor before and after the zoom.
	var world_under := _camera.position + (cursor_screen - vp_center) / old_zoom
	_camera.zoom     = Vector2(new_zoom, new_zoom)
	_camera.position = world_under - (cursor_screen - vp_center) / new_zoom

# ─── Signal handlers from CombatSignals ──────────────────────────────────────

func _on_action_pressed(action: String) -> void:
	_execute_action(action)

func _on_cell_clicked(cell: Vector2i) -> void:
	if not battle_started or turn_side != "player":
		return

	# Objective interaction: clicking the objective cell when the active player
	# is within interact_range and has AP triggers the mission-specific action.
	if not objective.is_empty() and objective.get("needs_marker", false) \
			and not objective_completed:
		var obj_cell := objective["cell"] as Vector2i
		if cell == obj_cell:
			var active := _current_active_player()
			if not active.is_empty() and int(active.get("ap", 0)) > 0:
				var apos := _cell_position(active)
				var dist := absi(cell.x - apos.x) + absi(cell.y - apos.y)
				if dist <= int(objective.get("interact_range", 2)):
					_interact_with_objective()
					return

	var atype := _action_type(selected_action)
	if atype == "MOVE":
		_move_active_unit_to(cell)
	elif atype in ["FIRE", "MELEE"]:
		var ti := _enemy_at_cell(cell)
		if ti >= 0:
			selected_target_index = ti
			_attack_enemy(ti, selected_action)
		else:
			_resolve_selected_attack()
	elif atype == "FIRE_AOE":
		_apply_missile_salvo(cell)
	elif atype == "PSI_HEAL":
		_apply_psi_focus()
	elif atype == "HEAL":
		_apply_trauma_patch()
	elif atype in ["DEFEND", "OVERWATCH"]:
		_execute_action(selected_action)

func _on_unit_clicked(unit_id: int, is_enemy: bool) -> void:
	if not battle_started or turn_side != "player":
		return
	if unit_id >= 1000:
		return   # vehicle token — decorative, not a combat target
	if is_enemy:
		var atype := _action_type(selected_action)
		if atype in ["FIRE", "MELEE"]:
			selected_target_index = unit_id
			_attack_enemy(unit_id, selected_action)
		elif atype == "FIRE_AOE":
			if unit_id >= 0 and unit_id < enemy_units.size():
				_apply_missile_salvo(_cell_position(enemy_units[unit_id]))
	else:
		if unit_id >= 0 and unit_id < player_units.size() \
				and int(player_units[unit_id].get("hp", 0)) > 0:
			active_player_index = unit_id
			status_line = "Active: %s" % str(player_units[unit_id].get("name", "Agent"))
			_refresh_initiative()
			_sync_display()

func _interact_with_objective() -> void:
	var active := _current_active_player()
	if active.is_empty(): return
	var ap := int(active.get("ap", 0))
	if ap <= 0: return

	var label      := str(objective.get("label",           "Interact"))
	var needed     := int(objective.get("progress_needed", 1))
	var action_key := str(objective.get("action_key",      ""))

	# Spend 1 AP per interaction tick.
	active["ap"] = ap - 1
	player_units[active_player_index] = active
	objective_progress += 1

	if objective_progress >= needed:
		objective_completed = true
		var line := "%s: %s — OBJECTIVE COMPLETE!" % [
				str(active.get("name", "Agent")), label]
		status_line = line
		_log_event(line)
		CombatSignals.audio_event.emit("ui_click")
		_sync_display()
		_complete_mission()
	else:
		var line := "%s: %s (%d/%d)" % [
				str(active.get("name", "Agent")), label,
				objective_progress, needed]
		status_line = line
		_log_event(line)
		CombatSignals.audio_event.emit("ui_click")
		_sync_display()

func _cycle_active_unit() -> void:
	var count := player_units.size()
	if count == 0: return
	var start := active_player_index
	for offset in range(1, count + 1):
		var idx := (start + offset) % count
		if int(player_units[idx].get("hp", 0)) > 0:
			active_player_index = idx
			status_line = "Active: %s" % str(player_units[idx].get("name", "Agent"))
			_refresh_initiative()
			_sync_display()
			return

func _auto_advance_unit() -> void:
	# Find the next living unit that still has AP; called after AP-spending actions.
	var count := player_units.size()
	for offset in range(1, count + 1):
		var next := (active_player_index + offset) % count
		if int(player_units[next].get("hp", 0)) > 0 \
				and int(player_units[next].get("ap", 0)) > 0:
			active_player_index = next
			selected_action     = "MOVE"
			status_line = "%s — ready." % str(player_units[next].get("name", "Agent")).split(" ")[0]
			_refresh_initiative()
			_sync_display()
			CombatSignals.audio_event.emit("ui_click")
			return
	# All living units have spent their AP — end the player turn automatically.
	_end_player_turn()

# ─── Combat flow ──────────────────────────────────────────────────────────────

func _seed_combat_state() -> void:
	player_units        = _build_player_units()
	cover_nodes         = _build_cover_nodes()
	var enc             := _ENCScript.new()
	var enc_result      := enc.generate(handoff, GRID_COLS, GRID_ROWS)
	enemy_units         = enc_result["enemy_units"] as Array[Dictionary]
	objective           = enc_result["objective"]   as Dictionary
	# Extract decorative vehicle tokens (giant vehicles are already in enemy_units).
	vehicle_units = []
	var vehicles := enc_result.get("vehicles", {}) as Dictionary
	for vk: String in ["agent_vehicle", "enemy_vehicle"]:
		var vd := vehicles.get(vk, {}) as Dictionary
		if not vd.is_empty():
			vehicle_units.append(vd)
	objective_progress  = 0
	objective_completed = false
	combat_log          = []
	selected_action     = "MOVE"
	pending_end_turn_confirmation = false
	show_combat_log     = false
	turn_side           = "player"
	turn_number         = 1
	active_player_index   = 0
	selected_target_index = 0
	enemy_turn_timer    = 0.0
	elapsed_time        = 0.0
	battle_started      = false
	overwatch_indices   = []
	defend_indices      = []
	deploy_rect         = Rect2()
	_refresh_initiative()
	if enemy_units.size() > 0:
		combat_log.append("Enemy contacts detected: %d." % enemy_units.size())
	combat_log.append("Press Enter or click DEPLOY to begin.")

func _overview_zoom() -> float:
	# Fixed overview zoom: grid fills ~87-98% of the available play area,
	# tiles appear 86 px wide at 1280×720 and 137 px at 1920×1080.
	# Player can zoom out to _ZOOM_MIN (0.25) for a broader overview or in
	# to _ZOOM_MAX for detail.
	return 0.40

func _start_combat(source: String) -> void:
	if battle_started: return
	battle_started = true

	# Configure child components
	_layout_combat_hud()
	# Pass 2× the viewport size so the battlefield grid is twice as large.
	# Camera2D starts at zoom=0.5 (fit-to-screen) and can zoom in/out.
	var obj_cell := objective.get("cell", Vector2i(GRID_COLS / 2, GRID_ROWS / 2)) as Vector2i
	_battlefield.configure(size * 4.0, map_texture, cover_nodes, obj_cell)

	_hud_layer.visible = true
	# Force HUD to fill the viewport — Controls inside a CanvasLayer don't
	# have their anchors resolved before _ready() returns, so size may be wrong.
	_hud.size     = size
	_hud.position = Vector2.ZERO
	_hud._reposition_buttons()
	_hud.update_state(player_units, enemy_units, initiative_entries,
					  active_player_index, selected_action,
					  turn_side, turn_number, combat_log,
					  portrait_textures, status_line)

	_spawn_all_tokens()
	_sync_display()

	# Centre the camera on the agent squad and set the overview zoom.
	if _camera != null:
		var center_cell := Vector2i(GRID_COLS / 2, GRID_ROWS / 2)
		if not player_units.is_empty():
			var sum := Vector2i.ZERO
			for pu in player_units:
				sum += pu.get("position", center_cell) as Vector2i
			center_cell = sum / player_units.size()
		_camera.position = _battlefield.cell_to_world(center_cell)
		_camera.zoom = Vector2.ONE * _overview_zoom()

	_banner.show_banner("player", turn_number)
	CombatSignals.turn_changed.emit("player", turn_number)
	CombatSignals.audio_event.emit("turn_player")

	status_line = "TACTICAL COMBAT UI READY"
	_log_event("%s: tactical insertion live." % source)
	print("TACTICAL COMBAT UI READY")
	print("grid / timeline / action bar / unit panel / log")
	queue_redraw()

func _execute_action(action_name: String) -> void:
	if not battle_started or turn_side != "player": return
	if action_name == "END TURN":
		if pending_end_turn_confirmation:
			_end_player_turn()
			return
		pending_end_turn_confirmation = true
		status_line = "Confirm end turn — press T again or click END TURN."
		_log_event("End turn: confirm required.")
		_sync_display()
		return
	if action_name == "NEXT":
		# Manual cycle — select the next alive unit regardless of remaining AP.
		_cycle_active_unit()
		return
	var atype := _action_type(action_name)
	if atype == "OVERWATCH":
		if active_player_index in overwatch_indices:
			overwatch_indices.erase(active_player_index)
			_log_event("%s leaves overwatch." % _active_unit_name())
		else:
			overwatch_indices.append(active_player_index)
			_log_event("%s enters overwatch." % _active_unit_name())
		status_line = "Overwatch toggled."
		_sync_display()
		return
	if atype == "DEFEND":
		if active_player_index in defend_indices:
			defend_indices.erase(active_player_index)
			var u := player_units[active_player_index] as Dictionary
			u["defense"] = maxi(0, int(u.get("defense", 4)) - 3)
			player_units[active_player_index] = u
			_log_event("%s drops guard." % _active_unit_name())
		else:
			defend_indices.append(active_player_index)
			var u := player_units[active_player_index] as Dictionary
			u["defense"] = int(u.get("defense", 4)) + 3
			player_units[active_player_index] = u
			_log_event("%s braces: DEF +3." % _active_unit_name())
		status_line = "Defend toggled."
		_sync_display()
		return
	if atype == "PSI_HEAL":
		_apply_psi_focus()
		return
	if atype == "HEAL":
		_apply_trauma_patch()
		return
	selected_action = action_name
	pending_end_turn_confirmation = false
	status_line = "%s selected." % action_name
	_sync_display()

func _apply_psi_pulse() -> void:
	for i in range(player_units.size()):
		var u := player_units[i] as Dictionary
		u["stress"] = maxi(0, int(u.get("stress", 0)) - 14)
		player_units[i] = u
	_log_event("Psi pulse: squad stress reduced.")
	status_line = "Psi pulse deployed."
	CombatSignals.audio_event.emit("psi")
	_sync_display()

func _apply_psi_focus() -> void:
	var active := _current_active_player()
	if active.is_empty(): return
	var ap := int(active.get("ap", 0))
	if ap <= 0:
		status_line = "No AP remaining."
		_sync_display()
		return
	var relief: int = int((_ACTION_DEFS.get("Psi Focus", {}) as Dictionary).get("stress_relief", 25))
	active["ap"] = maxi(0, ap - 1)
	player_units[active_player_index] = active
	for i in range(player_units.size()):
		var u := player_units[i] as Dictionary
		u["stress"] = maxi(0, int(u.get("stress", 0)) - relief)
		player_units[i] = u
	var line := "%s: Psi Focus — squad stress −%d." % [_active_unit_name(), relief]
	_log_event(line)
	status_line = line
	CombatSignals.audio_event.emit("psi")
	_sync_display()
	if int(active.get("ap", 0)) == 0:
		_auto_advance_unit()

func _apply_trauma_patch() -> void:
	var active := _current_active_player()
	if active.is_empty(): return
	var ap := int(active.get("ap", 0))
	if ap <= 0:
		status_line = "No AP remaining."
		_sync_display()
		return
	var heal_amt: int = int((_ACTION_DEFS.get("Trauma Patch", {}) as Dictionary).get("heal", 12))
	var old_hp  := int(active.get("hp", 0))
	var max_hp  := maxi(1, int(active.get("max_hp", 1)))
	if old_hp >= max_hp:
		status_line = "%s is already at full HP." % _active_unit_name()
		_sync_display()
		return
	active["ap"] = maxi(0, ap - 1)
	active["hp"] = mini(max_hp, old_hp + heal_amt)
	player_units[active_player_index] = active
	var healed := int(active.get("hp", 0)) - old_hp
	var line := "%s: Trauma Patch +%d HP." % [_active_unit_name(), healed]
	_log_event(line)
	status_line = line
	var pkey := "p%d" % active_player_index
	if _unit_tokens.has(pkey) and is_instance_valid(_unit_tokens[pkey]):
		_unit_tokens[pkey].update_data(active)
	CombatSignals.audio_event.emit("ui_click")
	_sync_display()
	if int(active.get("ap", 0)) == 0:
		_auto_advance_unit()

func _apply_missile_salvo(center_cell: Vector2i) -> void:
	var active := _current_active_player()
	if active.is_empty(): return
	var ap := int(active.get("ap", 0))
	var ap_cost: int = _action_ap_cost("Missile Salvo")
	if ap < ap_cost:
		status_line = "Not enough AP (Missile Salvo costs %d AP)." % ap_cost
		_sync_display()
		return
	active["ap"] = maxi(0, ap - ap_cost)
	player_units[active_player_index] = active
	var base_dmg   := _action_damage("Missile Salvo")
	var aoe_radius := int((_ACTION_DEFS.get("Missile Salvo", {}) as Dictionary).get("aoe_radius", 2))
	var hits := 0
	for j in range(enemy_units.size()):
		var eu := enemy_units[j] as Dictionary
		if int(eu.get("hp", 0)) <= 0: continue
		var epos := _cell_position(eu)
		var dist := absi(epos.x - center_cell.x) + absi(epos.y - center_cell.y)
		if dist > aoe_radius: continue
		var dmg := maxi(1, base_dmg - dist)
		eu["hp"] = maxi(0, int(eu.get("hp", 0)) - dmg)
		enemy_units[j] = eu
		var ekey := "e%d" % j
		if _unit_tokens.has(ekey) and is_instance_valid(_unit_tokens[ekey]):
			_unit_tokens[ekey].play_hit(dmg, true)
			if int(eu.get("hp", 0)) <= 0:
				_unit_tokens[ekey].play_death()
				CombatSignals.unit_died.emit(j, true)
		hits += 1
	var line := "%s: Missile Salvo — %d enemies hit." % [_active_unit_name(), hits]
	_log_event(line)
	status_line = line
	CombatSignals.audio_event.emit("fire")
	_selected_target_validity()
	_refresh_initiative()
	if _enemy_alive_count() == 0:
		_complete_mission()
		return
	_sync_display()
	if int(active.get("ap", 0)) == 0:
		_auto_advance_unit()

func _resolve_selected_attack() -> void:
	var atype := _action_type(selected_action)
	if atype == "PSI_HEAL":
		_apply_psi_focus()
		return
	if atype == "HEAL":
		_apply_trauma_patch()
		return
	if _current_target().is_empty():
		status_line = "No live target."
		_sync_display()
		return
	_attack_enemy(selected_target_index, selected_action)

func _move_active_unit_to(cell: Vector2i) -> void:
	var active := _current_active_player()
	if active.is_empty(): return
	var u      := player_units[active_player_index] as Dictionary
	var origin := _cell_position(u)
	var ap: int   = int(u.get("ap", 0))
	var dist: int = absi(cell.x - origin.x) + absi(cell.y - origin.y)
	if dist == 0: return
	if cell not in _battlefield.move_range_cells:
		status_line = "Out of move range."
		_sync_display()
		return

	overwatch_indices.erase(active_player_index)
	if active_player_index in defend_indices:
		defend_indices.erase(active_player_index)
		u["defense"] = maxi(0, int(u.get("defense", 4)) - 3)

	# Animate token BEFORE updating data (token is still at old world pos)
	var new_world : Vector2 = _battlefield.cell_to_world(cell)
	var pkey := "p%d" % active_player_index
	if _unit_tokens.has(pkey):
		_unit_tokens[pkey].move_to(new_world, u)

	u["position"] = cell
	u["ap"]       = maxi(0, ap - dist)
	player_units[active_player_index] = u

	status_line = "%s → %d,%d  (AP: %d)" % [
			str(u.get("name", "Agent")), cell.x, cell.y, int(u.get("ap", 0))]
	_log_event("%s moved to %d,%d" % [str(u.get("name", "Agent")), cell.x, cell.y])
	_refresh_initiative()
	_hud.update_state(player_units, enemy_units, initiative_entries,
					  active_player_index, selected_action,
					  turn_side, turn_number, combat_log,
					  portrait_textures, status_line)
	if int(u.get("ap", 0)) == 0:
		_auto_advance_unit()

func _attack_enemy(target_index: int, action_name: String) -> void:
	if target_index < 0 or target_index >= enemy_units.size(): return
	var target := enemy_units[target_index] as Dictionary
	if int(target.get("hp", 0)) <= 0: return
	var attacker := player_units[active_player_index] as Dictionary
	# Silently ignore clicks outside weapon range.
	var rng := _action_range(action_name)
	if rng == 0:
		rng = _role_attack_range(str(attacker.get("role", "")), action_name)
	var apos := _cell_position(attacker)
	var tpos := _cell_position(target)
	if absi(apos.x - tpos.x) + absi(apos.y - tpos.y) > rng:
		return
	var ap: int      = int(attacker.get("ap", 0))
	var ap_cost: int = _action_ap_cost(action_name)
	if ap < ap_cost:
		status_line = "Not enough AP (%s costs %d AP)." % [action_name, ap_cost]
		_sync_display()
		return
	attacker["ap"] = maxi(0, ap - ap_cost)
	player_units[active_player_index] = attacker

	var defense: int  = int(target.get("defense", 6))
	var chance: float = clampf(float(70 - defense * 2 + ap * 4), 20.0, 95.0)
	var hit := randf() * 100.0 < chance

	var ekey := "e%d" % target_index
	var akey := "p%d" % active_player_index
	if _unit_tokens.has(akey) and _unit_tokens.has(ekey):
		_unit_tokens[akey].attack_lunge(_unit_tokens[ekey].position)

	if not hit:
		_log_event("%s misses %s. (%d%%)" % [
				_active_unit_name(), str(target.get("name", "?")), int(chance)])
		status_line = "Miss!"
		if _unit_tokens.has(ekey):
			_unit_tokens[ekey].play_hit(0, false)
		CombatSignals.audio_event.emit("miss")
		CombatSignals.unit_attacked.emit(
			active_player_index, false, target_index, true, 0, false)
		_sync_display()
		if int(player_units[active_player_index].get("ap", 0)) == 0:
			_auto_advance_unit()
		return

	var damage: int = _action_damage(action_name)
	target["hp"] = maxi(0, int(target.get("hp", 0)) - damage)
	enemy_units[target_index] = target

	if _unit_tokens.has(ekey):
		_unit_tokens[ekey].play_hit(damage, true)
		if int(target.get("hp", 0)) <= 0:
			_unit_tokens[ekey].play_death()

	var atype := _action_type(action_name)
	CombatSignals.audio_event.emit("fire" if atype == "FIRE" else "hit")
	CombatSignals.unit_attacked.emit(
		active_player_index, false, target_index, true, damage, true)
	if int(target.get("hp", 0)) <= 0:
		CombatSignals.unit_died.emit(target_index, true)

	var line := "%s: %s → %d dmg." % [_active_unit_name(), action_name, damage]
	_log_event(line)
	status_line = line
	if int(target.get("hp", 0)) <= 0:
		_log_event("%s neutralized." % str(target.get("name", "?")))
	_selected_target_validity()
	_refresh_initiative()

	if _enemy_alive_count() == 0:
		_complete_mission()
		return
	_sync_display()
	if int(player_units[active_player_index].get("ap", 0)) == 0:
		_auto_advance_unit()

func _end_player_turn() -> void:
	pending_end_turn_confirmation = false
	selected_action = "MOVE"
	defend_indices.clear()
	for i in range(player_units.size()):
		var u := player_units[i] as Dictionary
		u["ap"] = 4
		player_units[i] = u
	turn_side = "enemy"
	enemy_turn_timer = enemy_turn_duration
	_log_event("── Player ends turn %02d ──" % turn_number)
	status_line = "Enemy turn..."
	_banner.show_banner("enemy", turn_number)
	CombatSignals.turn_changed.emit("enemy", turn_number)
	CombatSignals.audio_event.emit("turn_enemy")
	_sync_display()

func _resolve_enemy_turn() -> void:
	if turn_side != "enemy": return
	for i in range(enemy_units.size()):
		if int(enemy_units[i].get("hp", 0)) > 0:
			enemy_units[i]["ap"] = 2
	for i in range(enemy_units.size()):
		if int(enemy_units[i].get("hp", 0)) > 0:
			_enemy_act(i)
	turn_side    = "player"
	turn_number += 1
	overwatch_indices.clear()
	status_line = "Your turn — Turn %d" % turn_number
	_refresh_initiative()
	if _player_alive_count() == 0:
		_end_combat("defeat")
		return
	_banner.show_banner("player", turn_number)
	CombatSignals.turn_changed.emit("player", turn_number)
	CombatSignals.audio_event.emit("turn_player")
	_sync_display()

func _subtype_attack_range(subtype: String) -> int:
	match subtype:
		"grunt":     return 3    # pistol — short
		"heavy":     return 2    # shotgun — very short
		"sniper":    return 10   # sniper rifle — long
		"elite":     return 6    # assault rifle — medium
		"commander": return 6    # rifle — medium
		"psi":       return 4    # psi range
		_:           return 3

func _role_attack_range(role: String, action: String) -> int:
	if action == "MELEE": return 1
	if action == "PSI":   return 5
	match role.to_lower():
		"sniper":  return 10
		"samurai": return 3
		_:         return 6

# ─── Named-action helpers ─────────────────────────────────────────────────────

func _action_type(action: String) -> String:
	# Handle legacy uppercase names used internally.
	match action:
		"MOVE":      return "MOVE"
		"FIRE":      return "FIRE"
		"MELEE":     return "MELEE"
		"PSI":       return "PSI_HEAL"
		"DEFEND":    return "DEFEND"
		"OVERWATCH": return "OVERWATCH"
	var def := _ACTION_DEFS.get(action, {}) as Dictionary
	return str(def.get("type", "SYSTEM"))

func _action_range(action: String) -> int:
	var def := _ACTION_DEFS.get(action, {}) as Dictionary
	if def.is_empty(): return 0
	return int(def.get("range", 0))

func _action_damage(action: String) -> int:
	var def := _ACTION_DEFS.get(action, {}) as Dictionary
	if def.is_empty():
		match action:
			"FIRE":  return 5
			"MELEE": return 4
			"PSI":   return 3
		return 4
	return int(def.get("damage", 4))

func _action_ap_cost(action: String) -> int:
	var def := _ACTION_DEFS.get(action, {}) as Dictionary
	return int(def.get("ap", 1))

func _enemy_act(enemy_index: int) -> void:
	var enemy   := enemy_units[enemy_index] as Dictionary
	var subtype := str(enemy.get("enemy_subtype", "grunt")).to_lower()
	var ti: int  = _nearest_player_to(enemy)
	if ti < 0: return
	var ap: int = int(enemy.get("ap", 2))
	var rng: int = _subtype_attack_range(subtype)

	# ── Move phase — BFS to best reachable cell ───────────────────────────────
	var ep   := _cell_position(enemy)
	var tp   := _cell_position(player_units[ti] as Dictionary)
	var dist := absi(ep.x - tp.x) + absi(ep.y - tp.y)

	# How many AP to spend moving: save 1 for attack if possible.
	# Snipers stay put when target is already within extended range.
	var move_ap := 0
	if dist > rng:
		move_ap = maxi(0, ap - 1)
	if subtype == "sniper" and dist <= rng + 4:
		move_ap = 0

	if move_ap > 0:
		var reachable: Array[Vector2i] = _battlefield.reachable_cells(ep, move_ap)
		var best_cell := ep
		var best_dist := dist
		for cell: Vector2i in reachable:
			if _is_cell_occupied(cell, -1, enemy_index): continue
			var d := absi(cell.x - tp.x) + absi(cell.y - tp.y)
			if d < best_dist:
				best_dist = d
				best_cell = cell
		if best_cell != ep:
			var steps := absi(best_cell.x - ep.x) + absi(best_cell.y - ep.y)
			ap   -= mini(steps, move_ap)
			dist  = best_dist
			enemy["position"] = best_cell
			ep    = best_cell
			var ekey := "e%d" % enemy_index
			if _unit_tokens.has(ekey):
				_unit_tokens[ekey].move_to(_battlefield.cell_to_world(best_cell), enemy)

	# ── Attack phase ──────────────────────────────────────────────────────────
	if dist <= rng and ap > 0:
		_enemy_attack(enemy_index, ti, subtype)
		ap -= 1

	enemy["ap"] = ap
	enemy_units[enemy_index] = enemy

func _enemy_attack(enemy_index: int, target_index: int, subtype: String) -> void:
	var enemy  := enemy_units[enemy_index] as Dictionary
	var target := player_units[target_index] as Dictionary
	var is_psi := subtype == "psi"

	var damage: int
	var base_hit: float
	match subtype:
		"grunt":     damage = 2; base_hit = 60.0   # pistol
		"heavy":     damage = 5; base_hit = 70.0   # shotgun — reliable up close
		"sniper":    damage = 6; base_hit = 82.0   # sniper rifle — high damage, accurate
		"elite":     damage = 4; base_hit = 70.0   # assault rifle
		"commander": damage = 3; base_hit = 68.0   # rifle
		"psi":       damage = 2; base_hit = 65.0
		_:           damage = 2; base_hit = 60.0

	var defense: int = int(target.get("defense", 4))
	var chance: float = clampf(base_hit - float(defense) * 3.0, 10.0, 90.0)
	if target_index in defend_indices:
		damage  = maxi(0, damage - 1)
		chance -= 12.0

	# Lunge animation toward target
	var ekey := "e%d" % enemy_index
	var pkey := "p%d" % target_index
	if _unit_tokens.has(ekey) and _unit_tokens.has(pkey):
		_unit_tokens[ekey].attack_lunge(_unit_tokens[pkey].position)

	if randf() * 100.0 >= chance:
		_log_event("%s misses %s." % [str(enemy.get("name","?")), str(target.get("name","?"))])
		if _unit_tokens.has(pkey):
			_unit_tokens[pkey].play_hit(0, false)
		CombatSignals.audio_event.emit("miss")
		return

	target["hp"] = maxi(0, int(target.get("hp", 0)) - damage)
	if is_psi:
		var stress_gain := 22
		target["stress"] = mini(100, int(target.get("stress", 0)) + stress_gain)
		_log_event("%s PSI-blasts %s: -%d HP +%d stress." % [
				str(enemy.get("name","?")), str(target.get("name","?")), damage, stress_gain])
	else:
		target["stress"] = mini(100, int(target.get("stress", 0)) + 5)
		_log_event("%s hits %s for %d." % [
				str(enemy.get("name","?")), str(target.get("name","?")), damage])
	player_units[target_index] = target

	if _unit_tokens.has(pkey):
		_unit_tokens[pkey].play_hit(damage, true)
		if int(target.get("hp", 0)) <= 0:
			_unit_tokens[pkey].play_death()
	CombatSignals.unit_attacked.emit(enemy_index, true, target_index, false, damage, true)
	CombatSignals.audio_event.emit("hit")
	if int(target.get("hp", 0)) <= 0:
		CombatSignals.unit_died.emit(target_index, false)

func _nearest_player_to(enemy: Dictionary) -> int:
	var ep := _cell_position(enemy)
	var best: int = -1
	var best_d: int = 99999
	for i in range(player_units.size()):
		if int(player_units[i].get("hp", 0)) <= 0: continue
		var tp := _cell_position(player_units[i])
		var d: int = absi(ep.x - tp.x) + absi(ep.y - tp.y)
		if d < best_d:
			best_d = d
			best   = i
	return best

func _is_cell_occupied(cell: Vector2i, exclude_player: int, exclude_enemy: int) -> bool:
	for i in range(player_units.size()):
		if i == exclude_player: continue
		if int(player_units[i].get("hp", 0)) > 0 \
				and _cell_position(player_units[i]) == cell:
			return true
	for i in range(enemy_units.size()):
		if i == exclude_enemy: continue
		if int(enemy_units[i].get("hp", 0)) > 0 \
				and _cell_position(enemy_units[i]) == cell:
			return true
	return false

func _complete_mission() -> void:
	turn_side   = "ended"
	status_line = "Extraction clear. Mission complete."
	_log_event("── MISSION COMPLETE ──")
	_refresh_initiative()
	_sync_display()
	_end_combat("victory")

func _end_combat(outcome: String) -> void:
	if outcome == "defeat":
		turn_side   = "ended"
		status_line = "Squad eliminated. Mission failed."
		_log_event("── MISSION FAILED ──")
		_refresh_initiative()
		_sync_display()

	var casualties: Array = []
	for u: Dictionary in player_units:
		if int(u.get("hp", 0)) <= 0:
			casualties.append(str(u.get("name", "Agent")))
	var enemies_killed := enemy_units.size() - _enemy_alive_count()
	var result := {
		"turn_number":    turn_number,
		"casualties":     casualties,
		"enemies_killed": enemies_killed,
		"fund_reward":    enemies_killed * 150 + (500 if outcome == "victory" else 0),
	}
	_banner.show_banner("ended", turn_number)
	CombatSignals.combat_ended.emit(outcome, result)
	_results.show_results(outcome, result, project_root)
	_results.visible = true
	battle_ended = true   # block all further sync / input processing

# ─── Data builders ────────────────────────────────────────────────────────────

func _build_player_units() -> Array[Dictionary]:
	var squad: Array = handoff.get("squad", [])
	var units: Array[Dictionary] = []
	if squad.is_empty():
		units.append({"name": "ECHO",   "role": "samurai", "hp": 30, "max_hp": 30,
					  "stress": 20, "ap": 4, "defense": 5, "initiative": 18,
					  "position": Vector2i(2, 6), "kind": "player", "status_effects": []})
		units.append({"name": "VESPER", "role": "sniper",  "hp": 24, "max_hp": 24,
					  "stress": 10, "ap": 4, "defense": 3, "initiative": 20,
					  "position": Vector2i(2, 14), "kind": "player", "status_effects": []})
		return units
	for i in range(squad.size()):
		var raw: Variant = squad[i]
		if typeof(raw) != TYPE_DICTIONARY: continue
		var agent: Dictionary = raw as Dictionary
		var role   := str(agent.get("role", "agent")).to_lower()
		var row: int = mini(GRID_ROWS - 1, 1 + (i % maxi(1, GRID_ROWS / 2)) * 2)
		var def: int = 4 + (2 if role == "samurai" else (-1 if role == "psi" else 0))
		var raw_n  : Variant = agent.get("name", null)
		var clean  : String  = str(raw_n).strip_edges() if raw_n != null else ""
		if clean == "" or clean.to_lower() == "null":
			clean = role.to_upper().substr(0, 6) + "-%d" % (i + 1)
		# Carry the handoff action list so the HUD can show agent-specific buttons.
		var raw_actions: Variant = agent.get("available_actions", null)
		var agent_actions: Array[String] = []
		if typeof(raw_actions) == TYPE_ARRAY:
			for a: Variant in raw_actions as Array:
				agent_actions.append(str(a))
		if agent_actions.is_empty():
			# Sensible fallback by role if handoff omits the list.
			match role:
				"sniper": agent_actions = ["Move", "Defend", "Rifle Burst", "Pistol Shot", "Overwatch"]
				"psi":    agent_actions = ["Move", "Defend", "Rifle Burst", "Pistol Shot", "Psi Focus"]
				_:        agent_actions = ["Move", "Defend", "Rifle Burst", "Pistol Shot", "Overwatch"]
		units.append({
			"name":              clean,
			"role":              role,
			"hp":                int(agent.get("hp", 30)),
			"max_hp":            maxi(1, int(agent.get("max_hp", agent.get("hp", 30)))),
			"stress":            int(agent.get("stress", 0)),
			"ap":                2 if int(agent.get("stress", 0)) >= 80 else 4,
			"defense":           def,
			"initiative":        20 + int(agent.get("level", 1)) * 2 - i,
			"position":          Vector2i(1, row),
			"kind":              "player",
			"status_effects":    [],
			"available_actions": agent_actions,
		})
	return units

func _build_enemy_units() -> Array[Dictionary]:
	var mission    := _mission_data()
	var count: int  = maxi(1, mini(6, int(mission.get("starting_enemy_count", 3))))
	var theme      := str(mission.get("enemy_theme", "generic")).to_lower()
	var subtypes: Array[String] = ["grunt", "psi", "sniper", "elite", "commander", "grunt"]
	var units: Array[Dictionary] = []
	for i in range(count):
		var sub: String = subtypes[mini(i, subtypes.size() - 1)]
		var hp: int   = 10 + i * 2
		var defen: int = 6
		var init: int  = 16 - i * 2
		match sub:
			"elite":     hp += 4;  defen += 2; init += 2
			"commander": hp += 8;  defen += 4; init += 4
			"heavy":     hp += 5;  defen += 3
			"sniper":    init += 3; defen -= 1
			"psi":       hp -= 2;  defen -= 2; init += 2
		units.append({
			"name":          "%s %02d" % [theme.replace("_", " ").to_upper(), i + 1],
			"role":          "enemy",
			"hp":            hp, "max_hp": hp,
			"stress":        0,  "ap": 2,
			"initiative":    init,
			"position":      Vector2i(GRID_COLS - 2 - (i % 2), 1 + (i % 4) * 2),
			"kind":          "enemy",
			"enemy_subtype": sub,
			"enemy_theme":   theme,
			"status_effects": [],
			"defense":       defen,
		})
	return units

func _build_cover_nodes() -> Array[Dictionary]:
	return [
		# Left flank
		{"cell": Vector2i(6,  12), "high": true},
		{"cell": Vector2i(10,  6), "high": false},
		{"cell": Vector2i(10, 18), "high": true},
		{"cell": Vector2i(14,  4), "high": false},
		{"cell": Vector2i(14, 22), "high": true},
		# Centre corridor
		{"cell": Vector2i(16, 10), "high": false},
		{"cell": Vector2i(16, 20), "high": true},
		{"cell": Vector2i(20,  8), "high": true},
		{"cell": Vector2i(20, 18), "high": false},
		{"cell": Vector2i(22, 14), "high": true},
		# Right flank
		{"cell": Vector2i(24,  6), "high": true},
		{"cell": Vector2i(24, 22), "high": false},
		{"cell": Vector2i(28, 10), "high": false},
		{"cell": Vector2i(28, 24), "high": true},
		{"cell": Vector2i(30,  4), "high": false},
		{"cell": Vector2i(30, 14), "high": true},
		# Far side
		{"cell": Vector2i(34, 10), "high": false},
		{"cell": Vector2i(34, 20), "high": true},
		{"cell": Vector2i(36,  6), "high": true},
		{"cell": Vector2i(36, 16), "high": false},
		{"cell": Vector2i(38, 22), "high": true},
		{"cell": Vector2i(38,  8), "high": false},
	]

# Updated to match HudController's expected fields: name, is_enemy, active, hp, max_hp
func _refresh_initiative() -> void:
	initiative_entries = []
	var all_units: Array[Dictionary] = []
	for u: Dictionary in player_units:
		if int(u.get("hp", 0)) > 0: all_units.append(u)
	for e: Dictionary in enemy_units:
		if int(e.get("hp", 0)) > 0: all_units.append(e)
	all_units.sort_custom(Callable(self, "_compare_unit_initiative"))
	for i in range(mini(8, all_units.size())):
		var unit: Dictionary = all_units[i]
		var is_enemy := str(unit.get("kind", "player")) == "enemy"
		var pidx := player_units.find(unit)
		var is_act := (not is_enemy and pidx == active_player_index and turn_side == "player") \
					or (is_enemy and i == 0 and turn_side == "enemy")
		initiative_entries.append({
			"name":     _unit_short_label(unit),
			"is_enemy": is_enemy,
			"active":   is_act,
			"hp":       int(unit.get("hp", 0)),
			"max_hp":   maxi(1, int(unit.get("max_hp", 1))),
		})

func _compare_unit_initiative(a: Dictionary, b: Dictionary) -> bool:
	return int(a.get("initiative", 0)) > int(b.get("initiative", 0))

func _unit_short_label(unit: Dictionary) -> String:
	if str(unit.get("kind", "player")) == "enemy":
		return str(unit.get("enemy_subtype", "grunt")).to_upper().substr(0, 8)
	return str(unit.get("name", "AGENT")).to_upper().split(" ")[0].substr(0, 8)

# ─── Query helpers ────────────────────────────────────────────────────────────

func _current_active_player() -> Dictionary:
	if active_player_index < 0 or active_player_index >= player_units.size():
		return {}
	return player_units[active_player_index] as Dictionary

func _current_target() -> Dictionary:
	if enemy_units.is_empty(): return {}
	if selected_target_index < 0 or selected_target_index >= enemy_units.size():
		selected_target_index = 0
	if int(enemy_units[selected_target_index].get("hp", 0)) <= 0:
		for i in range(enemy_units.size()):
			if int(enemy_units[i].get("hp", 0)) > 0:
				selected_target_index = i
				break
	if int(enemy_units[selected_target_index].get("hp", 0)) <= 0:
		return {}
	return enemy_units[selected_target_index] as Dictionary

func _selected_target_validity() -> void:
	if enemy_units.is_empty(): selected_target_index = 0; return
	if selected_target_index < 0 or selected_target_index >= enemy_units.size() \
			or int(enemy_units[selected_target_index].get("hp", 0)) <= 0:
		for i in range(enemy_units.size()):
			if int(enemy_units[i].get("hp", 0)) > 0:
				selected_target_index = i
				return

func _enemy_at_cell(cell: Vector2i) -> int:
	for i in range(enemy_units.size()):
		if int(enemy_units[i].get("hp", 0)) > 0 \
				and _cell_position(enemy_units[i]) == cell:
			return i
	return -1

func _enemy_alive_count() -> int:
	var c: int = 0
	for e: Dictionary in enemy_units:
		if int(e.get("hp", 0)) > 0: c += 1
	return c

func _player_alive_count() -> int:
	var c: int = 0
	for u: Dictionary in player_units:
		if int(u.get("hp", 0)) > 0: c += 1
	return c

func _active_unit_name() -> String:
	return str(_current_active_player().get("name", "Agent"))

func _cell_position(unit: Dictionary) -> Vector2i:
	var raw: Variant = unit.get("position", Vector2i.ZERO)
	if typeof(raw) == TYPE_VECTOR2I: return raw as Vector2i
	if typeof(raw) == TYPE_ARRAY:
		var arr := raw as Array
		if arr.size() >= 2: return Vector2i(int(arr[0]), int(arr[1]))
	return Vector2i.ZERO

func _log_event(line: String) -> void:
	combat_log.append(line)
	if combat_log.size() > 24:
		combat_log.remove_at(0)

# ─── Handoff accessors ────────────────────────────────────────────────────────

func _mission_data() -> Dictionary:
	var raw: Variant = handoff.get("mission", {})
	return raw as Dictionary if typeof(raw) == TYPE_DICTIONARY else {}

func _campaign_data() -> Dictionary:
	var raw: Variant = handoff.get("campaign", {})
	return raw as Dictionary if typeof(raw) == TYPE_DICTIONARY else {}

func _map_data() -> Dictionary:
	var raw: Variant = handoff.get("map", {})
	return raw as Dictionary if typeof(raw) == TYPE_DICTIONARY else {}

# ─── Text helpers ─────────────────────────────────────────────────────────────

func _draw_text(text: String, pos: Vector2, font_size: int, color: Color) -> void:
	draw_string(ThemeDB.fallback_font, pos, text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, color)
