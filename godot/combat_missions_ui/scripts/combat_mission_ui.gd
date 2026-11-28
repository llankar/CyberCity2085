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

# Named actions implemented by the tactical client. The handoff can also
# contain equipment names whose bonuses are already included in agent stats.
const _ACTION_DEFS: Dictionary = {
	"Precision Shot": {"type":"FIRE","range":36,"damage":11,"heal":0,"ap":2},
	"Shotgun Blast": {"type":"FIRE","range":8,"damage":9,"heal":0,"ap":1},
	"SMG Spray": {"type":"FIRE","range":10,"damage":5,"heal":0,"ap":1},
	"Plasma Shot": {"type":"FIRE","range":12,"damage":6,"heal":0,"ap":1},
	"Magnum Shot": {"type":"FIRE","range":12,"damage":6,"heal":0,"ap":1},
	"Gravity Shot": {"type":"FIRE","range":30,"damage":12,"heal":0,"ap":2},
	"Arc Discharge": {"type":"FIRE","range":24,"damage":7,"heal":0,"ap":2},
	"Fire Spray": {"type":"FIRE","range":10,"damage":7,"heal":0,"ap":2},
	"Shock Burst": {"type":"FIRE","range":18,"damage":7,"heal":0,"ap":1},
	"Minigun Spray": {"type":"FIRE","range":24,"damage":9,"heal":0,"ap":2},
	"Rail Shot": {"type":"FIRE","range":36,"damage":12,"heal":0,"ap":2},
	"Rocket Volley": {"type":"FIRE_AOE","range":24,"damage":10,"heal":0,"ap":2,"aoe_radius":2},
	"Grenade": {"type":"FIRE_AOE","range":12,"damage":8,"heal":0,"ap":2,"aoe_radius":2},
	"EMP Pulse": {"type":"FIRE","range":18,"damage":5,"heal":0,"ap":1},
	"Sensor Lock": {"type":"FIRE","range":9,"damage":3,"heal":0,"ap":1},
	"Stun Strike": {"type":"MELEE","range":1,"damage":4,"heal":0,"ap":1},
	"Silent Kill": {"type":"MELEE","range":1,"damage":6,"heal":0,"ap":1},
	"Shield Bash": {"type":"MELEE","range":1,"damage":6,"heal":0,"ap":1},
	"Move":          {"type": "MOVE",     "range": 0, "damage": 0, "heal": 0, "ap": 0},
	"Defend":        {"type": "DEFEND",   "range": 0, "damage": 0, "heal": 0, "ap": 1},
	"Overwatch":     {"type": "OVERWATCH","range": 0, "damage": 0, "heal": 0, "ap": 1},
	"Pistol Shot":   {"type": "FIRE",     "range": 10, "damage": 4, "heal": 0, "ap": 1},
	"Rifle Burst":   {"type": "FIRE",     "range": 24, "damage": 7, "heal": 0, "ap": 1},
	"Plasma Burst":  {"type": "FIRE",     "range": 18, "damage": 9, "heal": 0, "ap": 2},
	"Katana Slash":  {"type": "MELEE",    "range": 1, "damage": 7, "heal": 0, "ap": 1},
	"Blade Strike":  {"type": "MELEE",    "range": 1, "damage": 5, "heal": 0, "ap": 1},
	"Servo Punch":   {"type": "MELEE",    "range": 1, "damage": 9, "heal": 0, "ap": 1},
	"Mind Spike":    {"type": "PSI",      "range": 12,"damage": 7, "heal": 0, "ap": 1},
	"Psi Focus":     {"type": "PSI_HEAL", "range": 0, "damage": 0, "heal": 0, "ap": 1, "stress_relief": 25},
	"Trauma Patch":  {"type": "HEAL",     "range": 0, "damage": 0, "heal": 12,"ap": 1},
	"Med Kit Pro":   {"type": "HEAL",     "range": 0, "damage": 0, "heal": 16,"ap": 1},
	"Nano-Repair Kit": {"type": "HEAL",   "range": 0, "damage": 0, "heal": 18,"ap": 1},
	"Missile Salvo": {"type": "FIRE_AOE", "range": 24, "damage": 10, "heal": 0, "ap": 2, "aoe_radius": 2},
	"VTOL Heavy Strike": {"type": "FIRE_AOE", "range": 999, "damage": 14, "heal": 0, "ap": 0, "aoe_radius": 2},
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
const _FOGScript = preload("res://scripts/fog_of_war.gd")

# ─── Component refs (untyped to avoid class-name scope errors) ────────────────
var _battlefield                 = null   # Battlefield
var _gamepad_cell := Vector2i(-1, -1)
var _units_layer   : Node2D      = null
var _hud                         = null   # HudController
var _hud_layer     : CanvasLayer = null
var _banner                      = null   # PhaseBanner
var _audio                       = null   # AudioManager
var _results                     = null   # MissionResults
var visual_mode := true
var visual_quality := 2
var environment_depth_enabled := true
var _depth_occlusion_clock := 0.0
var _visual_fx = null
var _visual_obstacles: Array[Node2D] = []
var _visual_lighting: Node2D
var _unit_tokens   : Dictionary  = {}    # "p0" / "e1" → UnitToken instance

# ─── Handoff + assets ─────────────────────────────────────────────────────────
var handoff         : Dictionary = {}
var _checkpoint_queued := false
var _checkpoint_signature := ""
var _checkpoint_warning := false
var _recovery_error := ""
var _session_control_clock := 0.0
var _audio_released := false
var _audio_release_clock := 0.0
var handoff_path    := "runtime/godot_combat/mission_handoff.json"
var project_root    : String = ""
var unit_textures   : Dictionary = {}
var _visual_asset_keys: Dictionary = {}
var _visual_enemy_portraits: Dictionary = {}
var portrait_textures: Dictionary = {}
var map_texture     : Texture2D = null

# ─── Game state ───────────────────────────────────────────────────────────────
var status_line   := "Waiting for CyberCity handoff."
var battle_started: bool  = false
var battle_ended  : bool  = false
var initial_enemy_count: int=0
var elapsed_time  : float = 0.0
var selected_action: String = "MOVE"
var heavy_strike_available: bool = false
var heavy_strike_used: bool = false
var pending_end_turn_confirmation: bool = false
var pending_retreat_confirmation: bool = false
var show_combat_log: bool = false
var turn_side     : String = "player"
var turn_number   : int    = 1
var active_player_index: int = 0
var _queued_player_index: int = -1
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
var _player_visible_cells: Dictionary = {}
var _explored_cells: Dictionary = {}

# ─── IPC to Python ────────────────────────────────────────────────────────────
var ipc_pipe_path  : String = ""   # Unix pipe path for IPC signal to Python

# ─── Camera / zoom / pan ──────────────────────────────────────────────────────
const _ZOOM_MIN        := 0.10
const _ZOOM_MAX        := 3.0
const _REFERENCE_TILE_WIDTH := 280.0
const BASE_VISION_RANGE := 15
const _DRAG_THRESHOLD  := 8.0   # pixels moved before a click becomes a pan
var _camera       : Camera2D  = null
var _map_root     : Node2D    = null
var _pressed_map_unit: Node2D = null
var _pan_active   : bool      = false
var _drag_started : bool      = false
var _pan_start_screen: Vector2 = Vector2.ZERO
var _pan_start_cam   : Vector2 = Vector2.ZERO

# ─── Lifecycle ────────────────────────────────────────────────────────────────

func _ready() -> void:
	set_process(true)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Set the scene clear colour here so it is unaffected by Camera2D transforms.
	# draw_rect inside _draw() is subject to the camera's world-space transform,
	# which makes it appear as a scaled rectangle rather than a full-screen fill.
	RenderingServer.set_default_clear_color(Color(0.005, 0.015, 0.025, 1.0))
	var graphics_config := ConfigFile.new()
	if graphics_config.load("user://combat_visual.cfg") == OK:
		visual_quality = clampi(int(graphics_config.get_value("graphics", "quality", 2)), 0, 2)
		environment_depth_enabled = bool(graphics_config.get_value("graphics","environment_depth",true))
	_read_args()
	_load_handoff()
	var saved: Variant = handoff.get("resume_snapshot")
	if saved is Dictionary and saved.get("camera") is Dictionary and saved.camera.get("visual_mode") is bool:
		visual_mode = saved.camera.visual_mode
	_load_unit_textures()
	_load_map_and_portraits()
	_build_children()
	_audio.configure_soundtrack(handoff.get("audio", {}),project_root,not handoff.get("session",{}).has("audio_path"))
	_connect_signals()
	_seed_combat_state()
	call_deferred("_start_combat", "AUTO-DEPLOY")
	call_deferred("_announce_session_ready")
	queue_redraw()

func _announce_session_ready() -> void:
	await get_tree().process_frame
	if _recovery_error.is_empty():
		preload("res://scripts/session_mailbox.gd").status(handoff.get("session", {}), "combat_started")

func _session_superseded() -> bool:
	var session: Dictionary = handoff.get("session", {})
	var path := str(session.get("control_path", ""))
	if path.is_empty() or not FileAccess.file_exists(path): return false
	var command: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return command is Dictionary and command.get("protocol_version") == 2 and command.get("session_id") == session.get("session_id") and command.get("event") == "superseded"

func _queue_tactical_checkpoint() -> void:
	if _checkpoint_queued or not battle_started or battle_ended or not _recovery_error.is_empty(): return
	if not handoff.get("session", {}).has("snapshot_path"): return
	_checkpoint_queued = true
	call_deferred("_write_tactical_checkpoint")

func _write_tactical_checkpoint() -> void:
	_checkpoint_queued = false
	if not battle_started or battle_ended or _session_superseded(): return
	var snapshot := preload("res://scripts/tactical_checkpoint.gd").capture(self)
	var signature := JSON.stringify(snapshot)
	if signature == _checkpoint_signature: return
	if preload("res://scripts/session_mailbox.gd").publish(str(handoff.session.snapshot_path), snapshot):
		_checkpoint_signature = signature
	elif not _checkpoint_warning:
		_checkpoint_warning = true
		_log_event("Tactical checkpoint unavailable; current combat continues, recovery is not guaranteed.")

func _poll_audio_release(delta: float) -> void:
	if _audio_released: return
	_audio_release_clock += delta
	if _audio_release_clock < 0.1: return
	_audio_release_clock = 0.0
	var session: Dictionary = handoff.get("session", {})
	var path := str(session.get("audio_path", ""))
	if path.is_empty() or not FileAccess.file_exists(path): return
	var message: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not message is Dictionary: return
	if message.get("protocol_version") != 2 or message.get("session_id") != session.get("session_id") or message.get("mission_id") != session.get("mission_id"): return
	if message.get("event") != "audio_released" or not message.get("audio") is Dictionary: return
	_audio.configure_soundtrack(message.audio, project_root)
	_audio_released = true

func _process(delta: float) -> void:
	_session_control_clock += delta
	if _session_control_clock >= 0.2:
		_session_control_clock = 0.0
		if _session_superseded():
			var runtime=get_node_or_null("/root/PersistentCombatRuntime")
			if runtime!=null:runtime.finish_mission(self)
			else:get_tree().quit()
			return
	_poll_audio_release(delta)
	if not battle_started:
		elapsed_time += delta
		queue_redraw()
		return
	elapsed_time += delta
	if visual_mode and environment_depth_enabled and visual_quality>0 and not battle_ended:
		_depth_occlusion_clock+=delta
		if _depth_occlusion_clock>=.05:
			_depth_occlusion_clock=0
			_update_prop_occlusion()
	if turn_side == "enemy":
		enemy_turn_timer = maxf(0.0, enemy_turn_timer - delta)
		if enemy_turn_timer <= 0.0:
			_resolve_enemy_turn()

func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED and _battlefield != null and not battle_ended:
		_battlefield.resize(size * 4.0)
		if _hud != null:
			_fit_hud_viewport()
		# Re-centre the camera whenever the window is resized (e.g. Win32 overlay
		# repositions the window to match Arcade's client area).  iso_tw changes
		# with the new viewport size so the camera must be recalculated.
		if _camera != null:
			_frame_squad()
		if battle_started:
			_resize_tokens()
			_build_visual_obstacles()
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
	_battlefield = preload("res://scripts/visual_battlefield.gd").new() if visual_mode else _BFScript.new()
	if visual_mode:
		_battlefield.top_down = "--isometric" not in OS.get_cmdline_user_args()
		var presentation := preload("res://scripts/map_presentation.gd")
		_battlefield.human_height_ratio = presentation.human_height_ratio(_map_data())
		var surface: Dictionary = presentation.entry_for(_map_data()).get("surface", {})
		var map_path := str(_map_data().get("path", ""))
		if not surface.is_empty() and map_texture != null and preload("res://scripts/environment_catalog.gd").matches_source(map_path, _asset_path(map_path), Vector2i(map_texture.get_size())):
			var rect: Array = surface.uv_rect
			var sample: Array = surface.get("sample_uv_rect", [0, 0, 1, 1])
			_battlefield.surface_texture = _load_tex(surface.path) if surface.has("path") else map_texture
			_battlefield.surface_uv = Rect2(rect[0], rect[1], rect[2], rect[3])
			_battlefield.surface_sample_uv = Rect2(sample[0], sample[1], sample[2], sample[3])
			_battlefield.surface_vertical = bool(surface.get("vertical", false))
			_battlefield.surface_feather = float(surface.get("feather", 0.0))
	_battlefield.name = "Battlefield"
	_map_root.add_child(_battlefield)

	# Units layer: parent for all UnitToken nodes
	_units_layer = Node2D.new()
	_units_layer.name = "UnitsLayer"
	_map_root.add_child(_units_layer)
	_units_layer.y_sort_enabled = visual_mode
	_visual_fx = preload("res://scripts/combat_visual_fx.gd").new()
	_visual_fx.z_index = 50
	_map_root.add_child(_visual_fx)

	# HUD on CanvasLayer 1 — hidden until combat starts
	_hud_layer = CanvasLayer.new()
	_hud_layer.layer   = 1
	_hud_layer.visible = false
	add_child(_hud_layer)
	_hud = preload("res://scripts/visual_hud.gd").new() if visual_mode else _HUDScript.new()
	_hud.name = "HudController"
	_hud_layer.add_child(_hud)
	_configure_visual_hud()

	# Phase banner on CanvasLayer 2
	var banner_layer := CanvasLayer.new()
	banner_layer.layer = 2
	add_child(banner_layer)
	_banner = _BNRScript.new()
	var reduced_motion := bool(handoff.get("accessibility", {}).get("reduced_motion", false))
	_banner.reduced_motion = reduced_motion
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
	_results.reduced_motion = reduced_motion
	_results.name    = "MissionResults"
	_results.visible = false
	results_layer.add_child(_results)

	# CRT post-FX on CanvasLayer 10
	var crt_layer := CanvasLayer.new()
	crt_layer.layer = 10
	crt_layer.visible = not visual_mode
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
	CombatSignals.fx_at.connect(func(kind: String, pos: Vector2):
		if visual_mode: _visual_fx.burst(kind,pos,pos,0.2 if kind == "impact" else 0.0))
	CombatSignals.cell_hovered.connect(_visual_cell_hovered)
	CombatSignals.unit_hovered.connect(_visual_unit_hovered)

# ─── Display sync ─────────────────────────────────────────────────────────────

func _sync_display() -> void:
	if battle_ended: return
	_update_player_visibility()
	_queue_tactical_checkpoint()
	_refresh_initiative()

	# Objective proximity hint — overrides status line when actionable.
	if turn_side == "player" and not objective.is_empty() \
			and objective.get("needs_marker", false) and objective.get("interactive", true) \
			and not objective_completed and _objective_interaction_available():
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
			var available_ap := maxi(0, int(active.get("ap", 0)))
			if available_ap == 0:
				_battlefield.clear_highlights()
			elif atype == "MOVE":
				var budget := available_ap
				_battlefield.show_move_range(_battlefield.reachable_cells(origin, budget), origin)
			elif atype in ["FIRE", "MELEE", "PSI", "FIRE_AOE"]:
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
		tok.visible = int(u.get("hp", 0)) > 0 or (visual_mode and tok._death)
	for j in range(enemy_units.size()):
		var key := "e%d" % j
		if not _unit_tokens.has(key): continue
		var tok = _unit_tokens[key]
		if not is_instance_valid(tok): _unit_tokens.erase(key); continue
		var u   := enemy_units[j] as Dictionary
		var currently_visible := _is_enemy_visible_to_player(j)
		tok.update_data(u)
		tok.set_active(false)
		tok.set_targeted(currently_visible and j == selected_target_index \
						  and _action_type(selected_action) in ["FIRE", "MELEE", "PSI", "FIRE_AOE"] \
						  and turn_side == "player")
		tok.visible = currently_visible and (int(u.get("hp", 0)) > 0 or (visual_mode and tok._death))

	_update_visual_context()
	_hud.show_log = show_combat_log
	_hud.update_state(player_units, _visible_enemy_units_for_hud(), initiative_entries,
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
		if visual_mode:
			tok.terrain_scale=_battlefield.token_terrain_scale()
			tok.facing_y_scale=_battlefield.iso_tw/maxf(.001,_battlefield.iso_th) if _battlefield.top_down else 2.0
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
		var tok  = preload("res://scripts/unit_visual.gd").new() if visual_mode else _TOKScript.new()
		tok.name = "Player%d" % i
		_units_layer.add_child(tok)
		if visual_mode:
			tok.terrain_scale=_battlefield.token_terrain_scale()
			tok.facing_y_scale=_battlefield.iso_tw/maxf(.001,_battlefield.iso_th) if _battlefield.top_down else 2.0
		tok.setup(u, i, false, tex, cell_size)
		if visual_mode: tok.configure_animation(str(_visual_asset_keys.get(tkey,tkey)), project_root)
		var wp0 : Vector2 = _battlefield.cell_to_world(_cell_position(u))
		tok.position = wp0
		_unit_tokens["p%d" % i] = tok

	for j in range(enemy_units.size()):
		var u    := enemy_units[j] as Dictionary
		var tkey := _unit_texture_key(u, true)
		var tex  := unit_textures.get(tkey, null) as Texture2D
		var tok  = preload("res://scripts/unit_visual.gd").new() if visual_mode else _TOKScript.new()
		tok.name = "Enemy%d" % j
		_units_layer.add_child(tok)
		if visual_mode:
			tok.terrain_scale=_battlefield.token_terrain_scale()
			tok.facing_y_scale=_battlefield.iso_tw/maxf(.001,_battlefield.iso_th) if _battlefield.top_down else 2.0
		tok.setup(u, j, true, tex, cell_size)
		if visual_mode: tok.configure_animation(str(_visual_asset_keys.get(tkey,tkey)), project_root)
		var wp1 : Vector2 = _battlefield.cell_to_world(_cell_position(u))
		tok.position = wp1
		_unit_tokens["e%d" % j] = tok

	# Decorative vehicle tokens — use id ≥ 1000 so click handler ignores them.
	for vi in range(vehicle_units.size()):
		var v    := vehicle_units[vi] as Dictionary
		var vkey := str(v.get("vehicle_key", "vehicle_agent_vtol"))
		var tex  := unit_textures.get(vkey, null) as Texture2D
		var is_ev := str(v.get("kind", "player")) == "enemy"
		var tok  = preload("res://scripts/unit_visual.gd").new() if visual_mode else _TOKScript.new()
		tok.name = "Vehicle%d" % vi
		_units_layer.add_child(tok)
		# id ≥ 1000 signals "vehicle" to _on_unit_clicked so it is silently ignored.
		if visual_mode:
			tok.terrain_scale=_battlefield.token_terrain_scale()
			tok.facing_y_scale=_battlefield.iso_tw/maxf(.001,_battlefield.iso_th) if _battlefield.top_down else 2.0
		tok.setup(v, 1000 + vi, is_ev, tex, cell_size)
		if visual_mode: tok.configure_animation(str(_visual_asset_keys.get(vkey,vkey)), project_root)
		tok.position = _battlefield.cell_to_world(_cell_position(v))
		_unit_tokens["v%d" % vi] = tok

# ─── Handoff & assets ─────────────────────────────────────────────────────────

func _read_args() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	for index in range(args.size()):
		if args[index] == "--handoff" and index + 1 < args.size():
			handoff_path = args[index + 1]
		elif args[index] == "--flat-environment":
			environment_depth_enabled=false
		elif args[index] == "--environment-depth":
			environment_depth_enabled=true
		elif args[index] == "--legacy-visuals":
			visual_mode = false
		elif args[index] == "--ipc_pipe" and index + 1 < args.size():
			ipc_pipe_path = args[index + 1]

func _load_handoff() -> void:
	var text := FileAccess.get_file_as_string(handoff_path)
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		status_line = "Handoff JSON unreadable."
		return
	handoff = parsed
	ipc_pipe_path = str(handoff.get("ipc_pipe_path", ipc_pipe_path))
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
	_try_load_tex("robot_combat", "assets/units/robot_combat_512.png")
	if not unit_textures.has("robot_combat"):
		_try_load_tex("robot_combat", "assets/units/robot_combat.png")

	# ── Enemy generic fallbacks ───────────────────────────────────────────────
	var base: Dictionary = {
		"enemy_grunt":     "assets/units/enemy_grunt_512.png",
		"enemy_heavy":     "assets/units/enemy_heavy_512.png",
		"enemy_elite":     "assets/units/enemy_elite_512.png",
		"enemy_commander": "assets/units/enemy_commander_512.png",
		"enemy_sniper":    "assets/units/enemy_sniper_512.png",
		"enemy_psi":       "assets/units/enemy_psi_512.png",
	}
	for key: String in base:
		_try_load_tex(key, str(base[key]))
		if not unit_textures.has(key):
			_try_load_tex(key, str(base[key]).replace("_512.png", ".png"))

	# Agent VTOL is always present in every mission regardless of enemy faction.
	_try_load_tex("vehicle_agent_vtol",
				  "assets/units/vehicle_aerial_military_01_vtol_gunship_512.png")

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

	# Faction-specific enemy ground vehicles (agent VTOL already loaded above).
	var vehicle_map: Dictionary = {
		"vehicle_enemy_corp_37":      "assets/units/vehicle_terrestrial_military_03_apc_512.png",
		"vehicle_enemy_corp_samurai": "assets/units/vehicle_terrestrial_military_01_battle_tank_512.png",
		"vehicle_enemy_raider":       "assets/units/vehicle_terrestrial_civil_07_cargo_hauler_512.png",
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
	return preload("res://scripts/runtime_texture_cache.gd").load_texture(full)

func _try_load_tex(key: String, path: String) -> void:
	var highres := path.get_basename() + "_512.png"
	var tex := _load_tex(highres) if visual_mode and FileAccess.file_exists(_asset_path(highres)) else _load_tex(path)
	if tex != null:
		unit_textures[key] = tex
		_visual_asset_keys[key] = path.get_file().get_basename().trim_suffix("_512")

func _unit_texture_key(unit: Dictionary, is_enemy: bool) -> String:
	if visual_mode:
		var vehicle_key := str(unit.get("vehicle_key", ""))
		if not vehicle_key.is_empty() and unit_textures.has(vehicle_key): return vehicle_key
		if not is_enemy and str(unit.get("role", "")) in ["power_armor","heavy_armor"]:
			var is_heavy := str(unit.get("asset_type", unit.get("role", ""))) == "heavy_armor"
			var suit_key := "power_armor_heavy" if is_heavy else "power_armor"
			if not unit_textures.has(suit_key):
				_try_load_tex(suit_key, "assets/units/%s.png" % suit_key)
			if unit_textures.has(suit_key):
				return suit_key
			var armor_key := "visual_power_armor"
			if not unit_textures.has(armor_key): _try_load_tex(armor_key,"assets/units/enemy_corp_37_power_armor_grunt.png")
			if unit_textures.has(armor_key): return armor_key
		var explicit_art := str(unit.get("visual_asset", ""))
		# A handoff may opt into any catalogued family without executable paths.
		if not explicit_art.is_empty() and explicit_art == explicit_art.get_file() and not "." in explicit_art:
			if not unit_textures.has(explicit_art): _try_load_tex(explicit_art,"assets/units/%s.png" % explicit_art)
			if unit_textures.has(explicit_art): return explicit_art
	if not is_enemy:
		var role := str(unit.get("role", "samurai")).to_lower()
		if role == "robot":
			if str(unit.get("asset_type", "")) == "support_robot":
				if not unit_textures.has("robot_support"):
					_try_load_tex("robot_support", "assets/units/robot_support.png")
				if unit_textures.has("robot_support"):
					return "robot_support"
			if unit_textures.has("robot_combat"):
				return "robot_combat"
		# Deterministic token: same agent name always maps to the same sprite.
		var agent_name := str(unit.get("name", "")).strip_edges()
		if agent_name != "":
			var idx := (agent_name.hash() & 0x7FFFFFFF) % 25 + 1
			var key := "agent_diverse_%02d" % idx
			if unit_textures.has(key):
				return key
		# Fallback: role-based sprite.
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
	for group_name: String in ["squad","support_assets"]:
		var entries: Variant = handoff.get(group_name,[])
		if entries is not Array: continue
		for entry: Variant in entries:
			if entry is not Dictionary: continue
			var data: Dictionary = entry
			var agent_name := str(data.get("name",""))
			if agent_name.is_empty(): continue
			var tex := _load_tex(str(data.get("portrait_path","")))
			var role := str(data.get("role",data.get("asset_type","agent"))).to_lower()
			if tex == null:
				var fallback := "assets/ui/portraits/agent_%02d.png" % ((agent_name.hash() & 0x7fffffff)%124+1)
				if "robot" in role: fallback = "assets/ui/portraits/robot_combat.png"
				elif "armor" in role: fallback = "assets/ui/portraits/power_armor_01.png"
				tex = _load_tex(fallback)
			if tex == null: tex = _load_tex("assets/ui/portraits/agent_01.png")
			if tex != null: portrait_textures[agent_name] = tex

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
	_draw_text("CYBERCITY 2085 // TACTICAL DEPLOYMENT", Vector2(72, 82), 26, NEON)
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
		_draw_text("No agents assigned.", origin + Vector2(0, 38), 16, WARN)
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
	if battle_ended:return
	if event is InputEventKey and event.pressed and not event.echo:
		var ke := event as InputEventKey
		match ke.keycode:
			KEY_ESCAPE:
				# Escape dismisses overlays; only mission results may leave combat.
				show_combat_log = false
				if is_instance_valid(_hud):
					if "settings_open" in _hud:_hud.settings_open = false
					_hud.show_log = false
					_hud.queue_redraw()
				accept_event()
			KEY_TAB:
				if battle_started and turn_side == "player":
					_cycle_active_unit()
				accept_event()
			KEY_HOME:
				_frame_squad()
				accept_event()
			KEY_F11:
				if visual_mode:
					_battlefield.top_down = not _battlefield.top_down
					_battlefield.resize(size*4.0)
					_resize_tokens()
					_build_visual_obstacles()
					_sync_display()
					_frame_squad()
				accept_event()
			KEY_F10:
				environment_depth_enabled = not environment_depth_enabled
				_build_visual_obstacles()
				_update_visual_context()
				accept_event()
			KEY_F9:
				_toggle_visual_interface()
				accept_event()
			KEY_L:
				show_combat_log = not show_combat_log
				if _hud != null:
					_hud.show_log = show_combat_log
					_hud.queue_redraw()
				queue_redraw()
				accept_event()
			KEY_T:
				if battle_started and turn_side == "player":
					_execute_action("END TURN")
				accept_event()
			KEY_R:
				if battle_started and turn_side == "player":
					_execute_action("RETREAT")
				accept_event()
			KEY_ENTER, KEY_KP_ENTER:
				_confirm_tactical_action("ENTER")
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
	if event is InputEventMouseMotion or event is InputEventMouseButton:
		_clear_gamepad_cursor()
		if _hud != null and _hud.gamepad_hints:
			_hud.close_gamepad_actions()
			_hud.gamepad_hints = false
			_hud.queue_redraw()
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
					_pressed_map_unit = null
					if _hud.has_method("blocks_map_input") and _hud.blocks_map_input(mbe.position):
						_pan_active = false
						_drag_started = false
						return
					var picked: Node2D = _pick_map_unit(mbe.position)
					if picked != null:
						_pressed_map_unit = picked
						_pan_start_screen = mbe.position
						_pan_active = false
						_drag_started = false
						get_viewport().set_input_as_handled()
						return
					_pan_active   = true
					_drag_started = false
					_pan_start_screen = mbe.position
					_pan_start_cam    = _camera.position
					# Don't consume — could still be a plain click.
				else:
					if is_instance_valid(_pressed_map_unit):
						var picked := _pressed_map_unit
						_pressed_map_unit = null
						if mbe.position.distance_to(_pan_start_screen) <= _DRAG_THRESHOLD*1.5:
							_on_unit_clicked(int(picked.get("unit_id")),bool(picked.get("is_enemy")))
						get_viewport().set_input_as_handled()
						return
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
	var new_zoom := clampf(old_zoom * factor, _ZOOM_MIN, _close_zoom())
	if absf(new_zoom - old_zoom) < 0.001: return
	var vp_center   := size * 0.5
	# World point that must stay under the cursor before and after the zoom.
	var world_under := _camera.position + (cursor_screen - vp_center) / old_zoom
	_camera.zoom     = Vector2(new_zoom, new_zoom)
	_camera.position = world_under - (cursor_screen - vp_center) / new_zoom

# ─── Signal handlers from CombatSignals ──────────────────────────────────────

func _on_action_pressed(action: String) -> void:
	_execute_action(action)

func _on_cell_clicked(cell: Vector2i, require_exact_target: bool = false) -> void:
	if not battle_started or turn_side != "player":
		return

	# Objective interaction: clicking the objective cell when the active player
	# is within interact_range and has AP triggers the mission-specific action.
	if not objective.is_empty() and objective.get("needs_marker", false) \
			and objective.get("interactive", true) and not objective_completed:
		var obj_cell := objective["cell"] as Vector2i
		if cell == obj_cell:
			var active := _current_active_player()
			if not active.is_empty() and int(active.get("ap", 0)) > 0:
				var apos := _cell_position(active)
				var dist := absi(cell.x - apos.x) + absi(cell.y - apos.y)
				if dist <= int(objective.get("interact_range", 2)):
					_interact_with_objective()
					return

	for index in range(player_units.size()):
		if int(player_units[index].get("hp",0)) > 0 and _cell_position(player_units[index]) == cell:
			_on_unit_clicked(index,false)
			return

	var atype := _action_type(selected_action)
	if atype == "MOVE":
		_move_active_unit_to(cell)
	elif atype in ["FIRE", "MELEE", "PSI"]:
		var ti := _enemy_at_cell(cell)
		if ti >= 0:
			selected_target_index = ti
			_attack_enemy(ti, selected_action)
		elif not require_exact_target:
			_resolve_selected_attack()
		else:
			status_line = "No live target on this cell."
			_sync_display()
	elif atype == "FIRE_AOE":
		if _player_visible_cells.has(cell):
			_apply_missile_salvo(cell)
		else:
			status_line = "Target area is hidden by fog of war."
			_sync_display()
	elif atype == "PSI_HEAL":
		_apply_psi_focus()
	elif atype == "HEAL":
		_apply_medical_utility(selected_action)
	elif atype in ["DEFEND", "OVERWATCH"]:
		_execute_action(selected_action)

func _on_unit_clicked(unit_id: int, is_enemy: bool) -> void:
	if battle_started and not battle_ended and turn_side == "enemy" and not is_enemy:
		if unit_id >= 0 and unit_id < player_units.size() and int(player_units[unit_id].get("hp",0)) > 0:
			_queued_player_index = unit_id
			status_line = "%s will act when the player turn resumes." % str(player_units[unit_id].get("name","Agent"))
			_sync_display()
		return
	if not battle_started or battle_ended or turn_side != "player":
		return
	if unit_id >= 1000:
		return   # vehicle token — decorative, not a combat target
	if is_enemy:
		var atype := _action_type(selected_action)
		if atype in ["FIRE", "MELEE", "PSI"]:
			selected_target_index = unit_id
			_attack_enemy(unit_id, selected_action)
		elif atype == "FIRE_AOE":
			if unit_id >= 0 and unit_id < enemy_units.size():
				_apply_missile_salvo(_cell_position(enemy_units[unit_id]))
	else:
		if unit_id >= 0 and unit_id < player_units.size() \
				and int(player_units[unit_id].get("hp", 0)) > 0:
			_activate_player_from_portrait(unit_id)

func _interact_with_objective() -> void:
	var active := _current_active_player()
	if active.is_empty(): return
	var ap := int(active.get("ap", 0))
	if ap <= 0: return
	if not _objective_interaction_available():
		status_line = "Charge armed. Survive the counterpush." if objective.has("hold_until_turn") \
			else "Objective in progress. Continue next squad turn."
		_sync_display()
		return

	var label      := str(objective.get("label",           "Interact"))
	var needed     := int(objective.get("progress_needed", 1))
	var action_key := str(objective.get("action_key",      ""))

	# Spend 1 AP per interaction tick.
	_spend_player_ap(active, 1)
	active["objective_contribution"] = int(active.get("objective_contribution", 0)) + 1
	player_units[active_player_index] = active
	objective_progress += 1
	var branch_note := ""
	if objective_progress == 1 and objective.has("field_proxy_cell") and _terminal_under_guard(active):
		objective["progress_needed"] = needed + 1
		_move_objective_marker(objective["field_proxy_cell"], "Establish Field Proxy")
		branch_note = "Main access blocked. Reach the field proxy."
	elif objective_progress == 2 and label == "Establish Field Proxy":
		objective["label"] = "Complete Download"
		branch_note = "Field proxy established. Complete the download next squad turn."
	if objective.get("once_per_turn", false):
		objective["last_interaction_turn"] = turn_number
	CombatSignals.audio_event.emit("terminal" if action_key in ["HACK", "SABOTAGE", "RETRIEVE", "PLANT", "SEARCH", "REPAIR", "ACTIVATE"] else "door_open")

	if objective_progress >= needed:
		var hold_turns := int(objective.get("hold_turns_after_interaction", 0))
		if hold_turns > 0:
			objective["hold_until_turn"] = turn_number + hold_turns
			status_line = "Charge armed. Survive the counterpush."
			_log_event(status_line)
			_sync_display()
			return
		objective_completed = true
		var line := "%s: %s — OBJECTIVE COMPLETE!" % [
				str(active.get("name", "Agent")), label]
		status_line = line
		_log_event(line)
		_sync_display()
		_complete_mission()
	else:
		var exit_cell: Array = objective.get("extraction_cell", [])
		if exit_cell.size() == 2:
			_move_objective_marker(exit_cell, "Reach Extraction")
		var phase_cells: Array = objective.get("phase_cells", [])
		var phase_labels: Array = objective.get("phase_labels", [])
		if objective_progress <= phase_cells.size() and objective_progress < phase_labels.size():
			var next_label := str(phase_labels[objective_progress])
			_move_objective_marker(phase_cells[objective_progress - 1], next_label)
			branch_note = "Next marker: %s. Continue next squad turn." % next_label
		var line := "%s: %s (%d/%d)" % [
				str(active.get("name", "Agent")), label,
				objective_progress, int(objective.get("progress_needed", needed))]
		status_line = line
		if not branch_note.is_empty():
			status_line += " " + branch_note
		elif objective.get("once_per_turn", false):
			status_line += " Continue next squad turn."
		if exit_cell.size() == 2:
			status_line += " Move to the extraction marker."
		_log_event(line)
		if not branch_note.is_empty():
			_log_event(branch_note)
		_sync_display()

func _terminal_under_guard(actor: Dictionary) -> bool:
	var terminal: Vector2i = objective["cell"]
	for enemy in enemy_units:
		var offset := _cell_position(enemy) - terminal
		if absi(offset.x) + absi(offset.y) <= 1 and _unit_can_see(actor, enemy):
			return true
	return false

func _move_objective_marker(cell: Array, label: String) -> void:
	var destination := Vector2i(int(cell[0]), int(cell[1]))
	objective["cell"] = destination
	objective["label"] = label
	_battlefield.objective_cell = destination

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
	initial_enemy_count=enemy_units.size()
	objective           = enc_result["objective"]   as Dictionary
	# Extract decorative vehicle tokens (giant vehicles are already in enemy_units).
	vehicle_units = _decorative_vehicles(enc_result.get("vehicles", {}) as Dictionary)
	objective_progress  = 0
	objective_completed = false
	combat_log          = []
	selected_action     = "MOVE"
	pending_end_turn_confirmation = false
	pending_retreat_confirmation = false
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
	_player_visible_cells = {}
	_explored_cells = {}
	deploy_rect         = Rect2()
	_refresh_initiative()
	if enemy_units.size() > 0:
		combat_log.append("Hostile presence suspected. Advance to establish contact.")
	combat_log.append("Press Enter or click DEPLOY to begin.")

func _overview_zoom() -> float:
	if visual_mode and _battlefield.top_down:
		return clampf(minf(size.x*.94/_battlefield.source_rect.size.x,size.y*.72/_battlefield.source_rect.size.y),_ZOOM_MIN,_ZOOM_MAX)
	var tile_width := maxf(1.0,_battlefield.iso_tw*2.0) if _battlefield != null else 280.0
	var target := 200.0*clampf(size.y/941.0,.75,1.7) if visual_mode else _REFERENCE_TILE_WIDTH
	return clampf(target/tile_width,_ZOOM_MIN,_ZOOM_MAX)

func _close_zoom() -> float:
	return minf(_ZOOM_MAX,_overview_zoom()*(3.0 if _battlefield.top_down else 1.65)) if visual_mode else _overview_zoom()

func _frame_squad() -> void:
	if _camera==null or player_units.is_empty():return
	var bounds:=Rect2(_battlefield.cell_to_world(_cell_position(player_units[0])),Vector2.ZERO)
	for unit: Dictionary in player_units:
		if int(unit.get("hp",0))>0:bounds=bounds.expand(_battlefield.cell_to_world(_cell_position(unit)))
	var reading:=_overview_zoom()
	if visual_mode and _battlefield.top_down:
		var body: float=_battlefield.source_rect.size.x*_battlefield.human_height_ratio
		var cinematic: float=96.0*clampf(size.y/1080.0,.75,1.6)/maxf(1,body)
		var margin: float=body*2.0
		var fit: float=minf(size.x*.72/maxf(1,bounds.size.x+margin),size.y*.58/maxf(1,bounds.size.y+margin))
		_camera.zoom=Vector2.ONE*clampf(minf(maxf(reading,cinematic),fit),reading,_close_zoom())
		_camera.position=bounds.get_center()+Vector2(0,size.y*.09/_camera.zoom.y)
		return
	var available:=Vector2(size.x*.70,size.y*.55)
	var margin: float=_battlefield.iso_tw*3.0
	var fit:=minf(available.x/maxf(1,bounds.size.x+margin),available.y/maxf(1,bounds.size.y+margin))
	_camera.zoom=Vector2.ONE*clampf(minf(reading,fit),_ZOOM_MIN,_close_zoom())
	# Offset toward the usable viewport above the portrait/action HUD.
	_camera.position=bounds.get_center()+Vector2(0,size.y*.07/_camera.zoom.y)

func _start_combat(source: String) -> void:
	if battle_started or not _recovery_error.is_empty(): return
	var resume: Dictionary = {}
	if handoff.has("resume_snapshot"):
		if handoff.resume_snapshot is Dictionary:
			resume = handoff.resume_snapshot
			_recovery_error = preload("res://scripts/tactical_checkpoint.gd").validate(resume, self)
		else: _recovery_error = "Invalid tactical snapshot"
		if not _recovery_error.is_empty():
			status_line = _recovery_error
			preload("res://scripts/session_mailbox.gd").status(handoff.get("session", {}), "error", false, _recovery_error)
			queue_redraw()
			return
		preload("res://scripts/tactical_checkpoint.gd").restore(resume, self)
	battle_started = true

	# Configure child components
	_layout_combat_hud()
	# Pass 2× the viewport size so the battlefield grid is twice as large.
	# Camera2D starts at zoom=0.5 (fit-to-screen) and can zoom in/out.
	var obj_cell := objective.get("cell", Vector2i(GRID_COLS / 2, GRID_ROWS / 2)) as Vector2i
	_battlefield.configure(size * 4.0, map_texture, cover_nodes, obj_cell, objective)
	if resume.is_empty():
		preload("res://scripts/map_wall_layout.gd").place_encounter(player_units, enemy_units, objective, _battlefield)

	_hud_layer.visible = true
	# Force HUD to fill the viewport — Controls inside a CanvasLayer don't
	# have their anchors resolved before _ready() returns, so size may be wrong.
	_fit_hud_viewport()
	_hud.update_state(player_units, _visible_enemy_units_for_hud(), initiative_entries,
					  active_player_index, selected_action,
					  turn_side, turn_number, combat_log,
					  portrait_textures, status_line)

	_spawn_all_tokens()
	_build_visual_obstacles()
	_sync_display()

	_frame_squad()
	if not resume.is_empty():
		preload("res://scripts/tactical_checkpoint.gd").restore_camera(resume, self)
		status_line = "Combat resumed — turn %d" % turn_number
		_sync_display()
		_banner.show_banner(turn_side, turn_number)
		print("TACTICAL COMBAT UI RESUMED")
		return

	_banner.show_banner("player", turn_number)
	CombatSignals.turn_changed.emit("player", turn_number)
	CombatSignals.audio_event.emit("turn_player")

	status_line = "TACTICAL COMBAT UI READY"
	var solid_count := 0
	for node: Dictionary in cover_nodes:
		if bool(node.get("solid", false)):
			solid_count += 1
	if visual_mode: status_line = "Squad deployed — choose an action."
	_log_event("Tactical insertion live.")
	_sync_display()
	print("TACTICAL COMBAT UI READY")
	print("grid / timeline / action bar / unit panel / log")
	queue_redraw()

func _execute_action(action_name: String) -> void:
	if not battle_started or turn_side != "player": return
	if action_name == "RETREAT":
		if pending_retreat_confirmation:
			pending_retreat_confirmation = false
			_log_event("Command orders a tactical retreat.")
			_end_combat("retreat")
			return
		pending_retreat_confirmation = true
		pending_end_turn_confirmation = false
		status_line = "Confirm retreat — press R again or click RETREAT."
		_log_event("Retreat: confirmation required.")
		_sync_display()
		return
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
	if atype == "SYSTEM":
		return
	if atype == "OVERWATCH":
		if active_player_index in overwatch_indices:
			overwatch_indices.erase(active_player_index)
			_log_event("%s leaves overwatch." % _active_unit_name())
		else:
			var watcher := _current_active_player()
			var cost := _action_ap_cost("Overwatch")
			if int(watcher.get("hp", 0)) <= 0 or _overwatch_weapon(watcher).is_empty() \
					or int(watcher.get("ap", 0)) < cost:
				status_line = "Overwatch requires a ranged weapon and 1 AP."
				_sync_display()
				return
			_spend_player_ap(watcher, cost)
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
			_visual_self_effect("cover")
			CombatSignals.audio_event.emit("shield")
		status_line = "Defend toggled."
		_sync_display()
		return
	if atype == "PSI_HEAL":
		_apply_psi_focus()
		return
	if atype == "HEAL":
		_apply_medical_utility(action_name)
		return
	selected_action = action_name
	pending_end_turn_confirmation = false
	pending_retreat_confirmation = false
	status_line = "%s: select a target in range." % action_name if atype in ["FIRE","MELEE","PSI","FIRE_AOE"] else "%s selected." % action_name
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
	var affected := 0
	var relieved := 0
	for unit in player_units:
		if int(unit.get("hp", 0)) <= 0:
			continue
		var reduction := mini(relief, maxi(0, int(unit.get("stress", 0))))
		if reduction > 0:
			unit["stress"] = int(unit["stress"]) - reduction
			affected += 1
			relieved += reduction
	if affected == 0:
		status_line = "No active allies need stress relief."
		_sync_display()
		return
	_spend_player_ap(active, 1)
	player_units[active_player_index] = active
	_visual_self_effect("psi")
	var line := "%s: Psi Focus relieved %d stress across %d active allies." % [_active_unit_name(), relieved, affected]
	_log_event(line)
	status_line = line
	CombatSignals.audio_event.emit("psi")
	_sync_display()
	if int(active.get("ap", 0)) == 0:
		_auto_advance_unit()

func _apply_medical_utility(action_name: String) -> void:
	var active := _current_active_player()
	if int(active.get("hp", 0)) <= 0 or action_name not in active.get("available_actions", []):
		return
	var cost := _action_ap_cost(action_name)
	var ap := int(active.get("ap", 0))
	if ap < cost:
		status_line = "No AP remaining."
		_sync_display()
		return
	var heal_amt := int(_ACTION_DEFS[action_name]["heal"])
	var old_hp  := int(active.get("hp", 0))
	var max_hp  := maxi(1, int(active.get("max_hp", 1)))
	if old_hp >= max_hp:
		status_line = "%s is already at full HP." % _active_unit_name()
		_sync_display()
		return
	_spend_player_ap(active, cost)
	active["hp"] = mini(max_hp, old_hp + heal_amt)
	player_units[active_player_index] = active
	_visual_self_effect("heal")
	CombatSignals.audio_event.emit("heal")
	var healed := int(active.get("hp", 0)) - old_hp
	var line := "%s: %s +%d HP." % [_active_unit_name(), action_name, healed]
	_log_event(line)
	status_line = line
	var pkey := "p%d" % active_player_index
	if _unit_tokens.has(pkey) and is_instance_valid(_unit_tokens[pkey]):
		_unit_tokens[pkey].update_data(active)
	_sync_display()
	if int(active.get("ap", 0)) == 0:
		_auto_advance_unit()

func _apply_missile_salvo(center_cell: Vector2i) -> void:
	var active := _current_active_player()
	if active.is_empty(): return
	var ap := int(active.get("ap", 0))
	var action := selected_action if _action_type(selected_action)=="FIRE_AOE" else "Missile Salvo"
	if action == "VTOL Heavy Strike" and (not heavy_strike_available or heavy_strike_used):
		status_line = "Nighthawk heavy strike already expended."
		_sync_display()
		return
	var origin := _cell_position(active)
	var distance := absi(origin.x-center_cell.x)+absi(origin.y-center_cell.y)
	var reach := _action_range(action)
	if distance>reach:
		status_line="Target out of range (distance %d / range %d tiles)."%[distance,reach]
		_sync_display()
		return
	var ap_cost: int = _action_ap_cost(action)
	if ap < ap_cost:
		status_line = "Not enough AP (%s costs %d AP)." % [action,ap_cost]
		_sync_display()
		return
	_spend_player_ap(active, ap_cost)
	player_units[active_player_index] = active
	if action == "VTOL Heavy Strike":
		heavy_strike_used = true
		for unit: Dictionary in player_units:
			var actions: Array = unit.get("available_actions", [])
			actions.erase("VTOL Heavy Strike")
			unit["available_actions"] = actions
	if visual_mode:
		_visual_fx.burst("explosion", Vector2.ZERO, _battlefield.cell_to_world(center_cell))
	var base_dmg   := _action_damage(action)
	var aoe_radius := int((_ACTION_DEFS.get(action, {}) as Dictionary).get("aoe_radius", 2))
	var confirmed_hits := 0
	for j in range(enemy_units.size()):
		var eu := enemy_units[j] as Dictionary
		if int(eu.get("hp", 0)) <= 0: continue
		var epos := _cell_position(eu)
		var dist := absi(epos.x - center_cell.x) + absi(epos.y - center_cell.y)
		if dist > aoe_radius: continue
		var visible := _is_enemy_visible_to_player(j)
		var dmg := maxi(1, base_dmg - dist)
		_apply_hp_damage(eu, dmg, active)
		enemy_units[j] = eu
		var ekey := "e%d" % j
		if visible and _unit_tokens.has(ekey) and is_instance_valid(_unit_tokens[ekey]):
			_unit_tokens[ekey].play_hit(dmg, true)
			if int(eu.get("hp", 0)) <= 0:
				_unit_tokens[ekey].play_death()
				CombatSignals.unit_died.emit(j, true)
		if visible and int(eu.get("hp", 0)) <= 0:
			_log_last_stand(active)
		if visible:
			confirmed_hits += 1
	var line := "%s: %s — Confirmed hits: %d." % [_active_unit_name(), action, confirmed_hits]
	_log_event(line)
	status_line = line
	CombatSignals.audio_event.emit("explosion_small")
	_selected_target_validity()
	_refresh_initiative()
	if _elimination_objective_met():
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
		_apply_medical_utility(selected_action)
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
	var route: Array[Vector2i] = _battlefield.find_path(origin, cell)
	if route.is_empty(): return
	dist = route.size() - 1
	if dist > ap: return
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
		_visual_move_token(pkey, _cell_position(u), cell, u)

	u["position"] = cell
	_spend_player_ap(u, dist)
	player_units[active_player_index] = u

	status_line = "%s → %d,%d  (AP: %d)" % [
			str(u.get("name", "Agent")), cell.x, cell.y, int(u.get("ap", 0))]
	_log_event("%s moved to %d,%d" % [str(u.get("name", "Agent")), cell.x, cell.y])
	_sync_display()
	if int(u.get("ap", 0)) == 0:
		_auto_advance_unit()

func _log_last_stand(attacker: Dictionary) -> void:
	var line := str(attacker.get("last_stand_dialogue", ""))
	var hp := int(attacker.get("hp", 0))
	if line.is_empty() or attacker.get("last_stand_spoken", false):
		return
	if hp <= 0 or hp > maxi(1, int(attacker.get("max_hp", 1)) / 4):
		return
	attacker["last_stand_spoken"] = true
	attacker["last_stand_hp"] = hp
	_log_event('%s: "%s"' % [str(attacker.get("name", "Agent")), line])

func _attack_audio_event(attacker: Dictionary, action_name: String, attack_type: String) -> String:
	if attack_type == "PSI":
		return "psi"
	if attack_type == "MELEE":
		return "melee"
	if attack_type != "FIRE":
		return "hit"
	var normalized_action := action_name.to_lower()
	if str(attacker.get("role", "")).to_lower() == "sniper" or "precision" in normalized_action or "sniper" in normalized_action:
		return "fire_sniper"
	if "pistol" in normalized_action:
		return "fire_pistol"
	if "laser" in normalized_action or "plasma" in normalized_action:
		return "fire_laser"
	return "fire"

func _attack_enemy(target_index: int, action_name: String, watcher_index: int = -1) -> void:
	if target_index < 0 or target_index >= enemy_units.size(): return
	var reaction := watcher_index >= 0
	var attacker_index := watcher_index if reaction else active_player_index
	if not reaction and not _is_enemy_visible_to_player(target_index):
		status_line = "No visible hostile at that position."
		_sync_display()
		return
	var target := enemy_units[target_index] as Dictionary
	if int(target.get("hp", 0)) <= 0: return
	var attacker := player_units[attacker_index] as Dictionary
	var attacker_name := str(attacker.get("name", "Agent"))
	# Report range before line of sight, consistently with the target card.
	var rng := _action_range(action_name)
	if rng == 0:
		rng = _role_attack_range(str(attacker.get("role", "")), action_name)
	var apos := _cell_position(attacker)
	var tpos := _cell_position(target)
	var distance := absi(apos.x - tpos.x) + absi(apos.y - tpos.y)
	if distance > rng:
		status_line = "Target out of range (distance %d / range %d tiles)." % [distance, rng]
		_sync_display()
		return
	if not _battlefield.has_los(apos, tpos, []):
		status_line = "Shot blocked: line of sight obstructed."
		_sync_display()
		return
	var ap: int      = int(attacker.get("ap", 0))
	var ap_cost: int = 0 if reaction else _action_ap_cost(action_name)
	if ap < ap_cost:
		status_line = "Not enough AP (%s costs %d AP)." % [action_name, ap_cost]
		_sync_display()
		return
	_spend_player_ap(attacker, ap_cost)
	player_units[attacker_index] = attacker

	var atype := _action_type(action_name)
	var aim: int      = int(attacker.get("psi", 5)) if atype == "PSI" else int(attacker.get("aim", 5))
	var defense: int  = int(target.get("defense", 6))
	# aim raises hit chance; enemy defense lowers it.  Base 50 keeps it balanced.
	var chance: float = clampf(50.0 + aim * 2.0 - defense * 2.0, 20.0, 95.0)
	var hit := randf() * 100.0 < chance

	var ekey := "e%d" % target_index
	var akey := "p%d" % attacker_index
	if _unit_tokens.has(akey) and _unit_tokens.has(ekey):
		_visual_attack(akey, ekey, _action_type(action_name), action_name)
	# The weapon report happens when the shot leaves the barrel, independently
	# of the later hit roll. This keeps missed sniper shots audible too.
	if atype == "FIRE":
		CombatSignals.audio_event.emit(_attack_audio_event(attacker, action_name, atype))

	if not hit:
		_log_event("%s misses %s. (%d%%)" % [
				attacker_name, str(target.get("name", "?")), int(chance)])
		status_line = "Miss!"
		if _unit_tokens.has(ekey):
			_unit_tokens[ekey].play_hit(0, false)
		CombatSignals.audio_event.emit("miss")
		CombatSignals.unit_attacked.emit(
			attacker_index, false, target_index, true, 0, false)
		_sync_display()
		if not reaction and int(attacker.get("ap", 0)) == 0:
			_auto_advance_unit()
		return

	var damage: int = _action_damage(action_name)
	# Melee attacks gain a bonus from the attacker's melee_power (str + close_combat).
	if _action_type(action_name) == "MELEE":
		damage += int(attacker.get("melee_power", 0)) / 3
	_apply_hp_damage(target, damage, attacker)
	enemy_units[target_index] = target

	if _unit_tokens.has(ekey):
		_unit_tokens[ekey].play_hit(damage, true)
		if int(target.get("hp", 0)) <= 0:
			_unit_tokens[ekey].play_death()

	if atype != "FIRE":
		CombatSignals.audio_event.emit(_attack_audio_event(attacker, action_name, atype))
	CombatSignals.unit_attacked.emit(
		attacker_index, false, target_index, true, damage, true)
	if int(target.get("hp", 0)) <= 0:
		CombatSignals.unit_died.emit(target_index, true)
		_log_last_stand(attacker)

	var line := "%s: %s → %d dmg." % [attacker_name, action_name, damage]
	_log_event(line)
	status_line = line
	if int(target.get("hp", 0)) <= 0:
		_log_event("%s neutralized." % str(target.get("name", "?")))
	_selected_target_validity()
	_refresh_initiative()

	if _elimination_objective_met():
		_complete_mission()
		return
	_sync_display()
	if not reaction and int(attacker.get("ap", 0)) == 0:
		_auto_advance_unit()

func _overwatch_weapon(unit: Dictionary) -> String:
	for action: String in unit.get("available_actions", []):
		if _action_type(action) == "FIRE":
			return action
	return ""

func _trigger_overwatch(enemy_index: int) -> void:
	var target := enemy_units[enemy_index]
	for index in overwatch_indices.duplicate():
		if int(target.get("hp", 0)) <= 0 or battle_ended:
			break
		var watcher := player_units[index]
		var weapon := _overwatch_weapon(watcher)
		if weapon.is_empty() or not _unit_can_see(watcher, target):
			continue
		var offset := _cell_position(target) - _cell_position(watcher)
		if absi(offset.x) + absi(offset.y) > _action_range(weapon):
			continue
		overwatch_indices.erase(index)
		_log_event("%s fires on overwatch." % str(watcher.get("name", "Agent")))
		_attack_enemy(enemy_index, weapon, index)

func _end_player_turn() -> void:
	pending_end_turn_confirmation = false
	selected_action = "MOVE"
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
	var containment: bool = objective.get("type", "") == "containment"
	var defending: bool = objective.get("type", "") == "defend"
	if defending and _defense_zone_breached():
		_end_combat("defeat", "Defense failed: a hostile entered the marked zone.")
		return
	var breacher := _containment_breacher_index() if containment or defending else -1
	for i in range(enemy_units.size()):
		if int(enemy_units[i].get("hp", 0)) <= 0: continue
		if containment:
			if i == breacher:
				var origin := _cell_position(enemy_units[i])
				_enemy_containment_act(i)
				if origin != _cell_position(enemy_units[i]):
					_trigger_overwatch(i)
		elif defending and i == breacher and _advance_defense_breacher(i):
			_trigger_overwatch(i)
		else:
			_enemy_act(i)
		if battle_ended:
			return
		if containment and _containment_breached():
			_end_combat("defeat", "Containment failed: a hostile crossed the marked breach zone.")
			return
		if defending and _defense_zone_breached():
			_end_combat("defeat", "Defense failed: a hostile entered the marked zone.")
			return
	for index in defend_indices:
		var defender := player_units[index]
		defender["defense"] = maxi(0, int(defender.get("defense", 4)) - 3)
	defend_indices.clear()
	for unit in player_units:
		unit["ap"] = _player_turn_ap(unit)
	turn_side    = "player"
	turn_number += 1
	overwatch_indices.clear()
	status_line = "Your turn — Turn %d" % turn_number
	_refresh_initiative()
	if _player_alive_count() == 0:
		_end_combat("defeat")
		return
	if defending:
		var hold_turns := int(objective.get("defend_turns_required", 4))
		objective_progress = mini(turn_number - 1, hold_turns)
		if turn_number > hold_turns:
			objective_completed = true
			_complete_mission()
			return
		status_line = "Hold position: turn %d/%d." % [turn_number, hold_turns]
	if objective.has("hold_until_turn"):
		if turn_number >= int(objective["hold_until_turn"]):
			objective_completed = true
			_complete_mission()
			return
		status_line = "Charge armed. Survive the counterpush."
	_banner.show_banner("player", turn_number)
	CombatSignals.turn_changed.emit("player", turn_number)
	CombatSignals.audio_event.emit("turn_player")
	if _queued_player_index >= 0:
		var chosen := _queued_player_index
		_queued_player_index = -1
		if chosen < player_units.size() and int(player_units[chosen].get("hp",0)) > 0:
			_activate_player_from_portrait(chosen)
			return
	_sync_display()

func _player_turn_ap(unit: Dictionary) -> int:
	if int(unit.get("hp", 0)) <= 0:
		return 0
	var budget := int(unit.get("base_ap", 4))
	return mini(2, budget) if int(unit.get("stress", 0)) >= 80 else budget

func _subtype_attack_range(subtype: String) -> int:
	match subtype:
		"grunt":     return 10    # pistol — short
		"heavy":     return 8    # shotgun — very short
		"sniper":    return 36   # sniper rifle — long
		"elite":     return 24    # assault rifle — medium
		"commander": return 24    # rifle — medium
		"psi":       return 4    # psi range
		_:           return 3

func _role_attack_range(role: String, action: String) -> int:
	if action == "MELEE": return 1
	if action == "PSI":   return 5
	match role.to_lower():
		"sniper":  return 36
		"samurai": return 10
		_:         return 24

# ─── Named-action helpers ─────────────────────────────────────────────────────

func _action_type(action: String) -> String:
	# Handle legacy uppercase names used internally.
	match action:
		"MOVE":      return "MOVE"
		"FIRE":      return "FIRE"
		"MELEE":     return "MELEE"
		"PSI":       return "PSI"
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
			"FIRE":  return 7
			"MELEE": return 4
			"PSI":   return 3
		return 4
	return int(def.get("damage", 4))

func _action_ap_cost(action: String) -> int:
	var def := _ACTION_DEFS.get(action, {}) as Dictionary
	return int(def.get("ap", 1))

func _enemy_act(enemy_index: int) -> void:
	var enemy   := enemy_units[enemy_index] as Dictionary
	var initial_cell := _cell_position(enemy)
	var subtype := str(enemy.get("enemy_subtype", "grunt")).to_lower()
	var ap: int = int(enemy.get("ap", 2))
	var rng: int = _subtype_attack_range(subtype)
	var ti: int = _enemy_engagement_target(enemy_index, subtype, rng)
	var occupied := _enemy_known_occupied_cells(enemy_index)
	# Search without using hidden player coordinates. Enemies reserve one AP so
	# discovery during movement can still lead to an attack this turn.
	if ti < 0:
		var start := _cell_position(enemy)
		var search_goal := Vector2i(GRID_COLS / 2, GRID_ROWS / 2)
		var route: Array[Vector2i] = []
		# After the initial sweep to the center, keep searching fixed sectors.
		var patrol_phase := floori(float(maxi(1, turn_number) - 1) / 8.0)
		if patrol_phase > 0:
			var offsets := [Vector2i(0, -7), Vector2i(-10, 0), Vector2i(0, 7), Vector2i(10, 0)]
			for alternate in offsets.size():
				var sector := posmod(patrol_phase - 1 + enemy_index + alternate, offsets.size())
				var waypoint: Vector2i = search_goal + offsets[sector]
				route = _battlefield.find_path(start, waypoint, occupied)
				if not route.is_empty():
					break
		if route.is_empty():
			route = _battlefield.find_path(start, search_goal, occupied, true)
		var search_steps := mini(maxi(0, ap - 1), maxi(0, route.size() - 1))
		for step in range(1, search_steps + 1):
			if _is_cell_occupied(route[step], -1, enemy_index):
				search_steps = step - 1
				break
		if search_steps > 0:
			var destination := route[search_steps]
			enemy["position"] = destination
			ap -= search_steps
			var search_key := "e%d" % enemy_index
			if _unit_tokens.has(search_key):
				_visual_move_token(search_key, start, destination, enemy)
		ti = _enemy_engagement_target(enemy_index, subtype, rng)
		if ti < 0:
			if _cell_position(enemy) != initial_cell:
				_trigger_overwatch(enemy_index)
			enemy["ap"] = 0
			enemy_units[enemy_index] = enemy
			return

	# ── Move phase — BFS to best reachable cell ───────────────────────────────
	var ep   := _cell_position(enemy)
	var tp   := _cell_position(player_units[ti] as Dictionary)
	var dist := absi(ep.x - tp.x) + absi(ep.y - tp.y)

	# Reserve one AP to shoot. Trained enemies may reposition to low cover.
	var profile := _mission_data().get("tactical_profile", {}) as Dictionary
	var prefers_cover := subtype in ["elite", "commander"] and float(profile.get("cover_bias", 1.0)) >= 1.0
	var has_shot := dist <= rng
	var covered: bool = prefers_cover and _battlefield.has_low_cover_toward(ep, tp)
	var move_ap := maxi(0, ap - 1) if not has_shot or (prefers_cover and not covered) else 0

	if move_ap > 0:
		occupied = _enemy_known_occupied_cells(enemy_index)
		var reachable: Array[Vector2i] = _battlefield.reachable_cells(ep, move_ap, occupied)
		var best_cell := ep
		var best_has_shot := has_shot
		var best_covered := covered
		var pursuit_occupied := occupied.duplicate()
		pursuit_occupied.erase(tp)
		var best_route_length: int = _battlefield.find_path(ep, tp, pursuit_occupied).size()
		for cell: Vector2i in reachable:
			var offset := tp - cell
			var can_shoot: bool = absi(offset.x) + absi(offset.y) <= mini(rng, _vision_range(enemy)) \
				and _battlefield.has_los(cell, tp, [])
			var has_cover: bool = can_shoot and prefers_cover and _battlefield.has_low_cover_toward(cell, tp)
			var route_length: int = _battlefield.find_path(cell, tp, pursuit_occupied).size()
			var advances := not can_shoot and route_length > 0 \
				and (best_route_length == 0 or route_length < best_route_length)
			if (can_shoot and not best_has_shot) or (has_cover and not best_covered) \
					or (not best_has_shot and advances):
				best_has_shot = can_shoot
				best_covered = has_cover
				best_route_length = route_length
				best_cell = cell
		if best_cell != ep:
			var route: Array[Vector2i] = _battlefield.find_path(ep, best_cell, occupied)
			for step in range(1, route.size()):
				if _is_cell_occupied(route[step], -1, enemy_index):
					break
				enemy["position"] = route[step]
				ap -= 1
			var destination := _cell_position(enemy)
			dist = absi(destination.x - tp.x) + absi(destination.y - tp.y)
			var ekey := "e%d" % enemy_index
			if destination != ep and _unit_tokens.has(ekey):
				_visual_move_token(ekey, ep, destination, enemy)

	# ── Attack phase ──────────────────────────────────────────────────────────
	if _cell_position(enemy) != initial_cell:
		_trigger_overwatch(enemy_index)
		if int(enemy.get("hp", 0)) <= 0 or battle_ended:
			return
	if dist <= rng and ap > 0 and _unit_can_see(enemy, player_units[ti] as Dictionary):
		_enemy_attack(enemy_index, ti, subtype)
		ap -= 1

	enemy["ap"] = ap
	enemy_units[enemy_index] = enemy

func _enemy_known_occupied_cells(enemy_index: int) -> Array[Vector2i]:
	var occupied: Array[Vector2i] = []
	for i in enemy_units.size():
		if i != enemy_index and int(enemy_units[i].get("hp", 0)) > 0:
			occupied.append(_cell_position(enemy_units[i]))
	for player in player_units:
		if _unit_can_see(enemy_units[enemy_index], player):
			occupied.append(_cell_position(player))
	return occupied

func _containment_breacher_index() -> int:
	return preload("res://scripts/containment_objective.gd").breacher_index(enemy_units, objective)

func _enemy_containment_act(enemy_index: int) -> void:
	var enemy := enemy_units[enemy_index] as Dictionary
	var start := _cell_position(enemy)
	var marker := objective.get("cell", Vector2i.ZERO) as Vector2i
	var half_width := int(objective.get("breach_half_width_cells", 3))
	var goal := preload("res://scripts/containment_objective.gd").target_cell(start, objective)
	var occupied := _enemy_known_occupied_cells(enemy_index)
	var route: Array[Vector2i] = _battlefield.find_path(start, goal, occupied)
	if route.size() < 2:
		for row in range(marker.y - half_width, marker.y + half_width + 1):
			if row < 0 or row >= GRID_ROWS: continue
			var alternate: Array[Vector2i] = _battlefield.find_path(start, Vector2i(marker.x, row), occupied)
			if alternate.size() >= 2 and (route.is_empty() or alternate.size() < route.size()):
				route = alternate
	if route.size() >= 2:
		var destination := route[1]
		if not _is_cell_occupied(destination, -1, enemy_index):
			enemy["position"] = destination
			var ekey := "e%d" % enemy_index
			if _unit_tokens.has(ekey):
				_visual_move_token(ekey, start, destination, enemy)
	enemy["ap"] = 0
	enemy_units[enemy_index] = enemy

func _containment_breached() -> bool:
	return preload("res://scripts/containment_objective.gd").breached(enemy_units, objective)

func _defense_zone_breached() -> bool:
	var zone := _BFScript.defense_zone_cells(objective["cell"])
	for enemy in enemy_units:
		if int(enemy.get("hp", 0)) > 0 and _cell_position(enemy) in zone:
			return true
	return false

func _advance_defense_breacher(enemy_index: int) -> bool:
	var enemy := enemy_units[enemy_index]
	var start := _cell_position(enemy)
	var occupied := _enemy_known_occupied_cells(enemy_index)
	var best_route: Array[Vector2i] = []
	for cell in _BFScript.defense_zone_cells(objective["cell"]):
		if _battlefield.is_wall(cell) or cell in occupied:
			continue
		var route: Array[Vector2i] = _battlefield.find_path(start, cell, occupied)
		if route.size() >= 2 and (best_route.is_empty() or route.size() < best_route.size()):
			best_route = route
	if best_route.is_empty() or _is_cell_occupied(best_route[1], -1, enemy_index):
		return false
	var destination := best_route[1]
	enemy["position"] = destination
	enemy["ap"] = 0
	var key := "e%d" % enemy_index
	if _unit_tokens.has(key):
		_visual_move_token(key, start, destination, enemy)
	return true

func _enemy_attack(enemy_index: int, target_index: int, subtype: String) -> void:
	var enemy  := enemy_units[enemy_index] as Dictionary
	var target := player_units[target_index] as Dictionary
	var is_psi := subtype == "psi"

	var damage: int
	var base_hit: float
	match subtype:
		"grunt":     damage = 4; base_hit = 60.0   # pistol
		"heavy":     damage = 9; base_hit = 70.0   # shotgun — reliable up close
		"sniper":    damage = 11; base_hit = 82.0   # sniper rifle — high damage, accurate
		"elite":     damage = 7; base_hit = 70.0   # assault rifle
		"commander": damage = 7; base_hit = 68.0   # rifle
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
		_visual_attack(ekey, pkey, "PSI" if is_psi else "FIRE")
	var enemy_audio := "psi" if is_psi else ("fire_sniper" if subtype == "sniper" else ("fire_pistol" if subtype == "grunt" else "fire"))
	CombatSignals.audio_event.emit(enemy_audio)

	if randf() * 100.0 >= chance:
		_log_event("%s misses %s." % [str(enemy.get("name","?")), str(target.get("name","?"))])
		if _unit_tokens.has(pkey):
			_unit_tokens[pkey].play_hit(0, false)
		CombatSignals.audio_event.emit("miss")
		return

	_apply_hp_damage(target, damage)
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
	status_line = "Relay destroyed. Mission complete." if objective.has("hold_until_turn") else "Mission complete."
	_log_event("── MISSION COMPLETE ──")
	_refresh_initiative()
	_sync_display()
	_end_combat("victory")

func _end_combat(outcome: String, failure_message: String = "") -> void:
	if outcome == "defeat":
		turn_side   = "ended"
		status_line = failure_message if not failure_message.is_empty() else "Squad eliminated. Mission failed."
		_log_event("── MISSION FAILED ──")
		_refresh_initiative()
		_sync_display()

	var casualties: Array = []
	for u: Dictionary in player_units:
		if int(u.get("hp", 0)) <= 0:
			casualties.append(str(u.get("name", "Agent")))
	var enemies_killed := enemy_units.size() - _enemy_alive_count()
	var agents: Array=[]
	var support: Array=[]
	for unit: Dictionary in player_units:
		var snapshot: Dictionary={"name":unit.name,"hp":int(unit.hp),"max_hp":int(unit.max_hp),"stress":int(unit.get("stress",0))}
		for metric in ["damage_dealt", "damage_taken", "kills", "actions_used", "objective_contribution"]:
			if unit.has(metric):
				snapshot[metric] = int(unit[metric])
		if not str(unit.get("asset_id","")).is_empty():
			snapshot["id"]=unit.asset_id
			support.append(snapshot)
		else:
			snapshot["name"] = unit.get("campaign_name", unit.name)
			if unit.has("last_stand_hp"):
				snapshot["last_stand_hp"] = int(unit.last_stand_hp)
			agents.append(snapshot)
	var result := {
		"session":handoff.get("session",{}),
		"agents":agents,"support":support,
		"initial_enemy_count":initial_enemy_count,
		"enemies_spawned_total":enemy_units.size(),
		"objective_completed":objective_completed,
		"objective_progress":objective_progress,
		"turn_number":    turn_number,
		"casualties":     casualties,
		"enemies_killed": enemies_killed,
		"heavy_strike_used": heavy_strike_used,
		"fund_reward":    enemies_killed * 150 + (500 if outcome == "victory" else 0),
	}
	_banner.show_banner("ended", turn_number)
	CombatSignals.combat_ended.emit(outcome, result)
	_results.show_results(outcome, result, project_root, ipc_pipe_path, _audio)
	_results.visible = true
	battle_ended = true   # block all further sync / input processing

# ─── Data builders ────────────────────────────────────────────────────────────

func _spend_player_ap(unit: Dictionary, cost: int) -> void:
	var before := int(unit.get("ap", 0))
	unit["ap"] = maxi(0, before - cost)
	if unit.has("actions_used"):
		unit["actions_used"] += before - int(unit.ap)

func _apply_hp_damage(target: Dictionary, damage: int, attacker: Dictionary = {}) -> void:
	var before := int(target.get("hp", 0))
	target["hp"] = maxi(0, before - damage)
	var lost := before - int(target.hp)
	if target.has("damage_taken"):
		target["damage_taken"] += lost
	if attacker.has("damage_dealt"):
		attacker["damage_dealt"] += lost
	if attacker.has("kills") and lost > 0 and int(target.hp) == 0:
		attacker["kills"] += 1

func _build_player_units() -> Array[Dictionary]:
	var squad_raw: Variant = handoff.get("squad", [])
	var squad: Array = squad_raw as Array if typeof(squad_raw) == TYPE_ARRAY else []
	var assets_raw: Variant = handoff.get("support_assets", [])
	var support_assets: Array = assets_raw as Array if typeof(assets_raw) == TYPE_ARRAY else []
	var units: Array[Dictionary] = []
	var deployment_upgrades: Array = handoff.get("combat_ui", {}).get("deployment_upgrades", [])
	heavy_strike_available = "heavy_strike" in deployment_upgrades
	if squad.is_empty() and support_assets.is_empty():
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
		# Fallback defense/initiative by role when not supplied by handoff.
		var role_def_base: int = 4 + (2 if role == "samurai" else (-1 if role == "psi" else 0))
		var raw_n  : Variant = agent.get("name", null)
		var clean  : String  = str(raw_n).strip_edges() if raw_n != null else ""
		if clean == "":
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
				"psi":    agent_actions = ["Move", "Defend", "Mind Spike", "Psi Focus", "Pistol Shot"]
				_:        agent_actions = ["Move", "Defend", "Rifle Burst", "Pistol Shot", "Overwatch"]
		if heavy_strike_available and not heavy_strike_used:
			agent_actions.append("VTOL Heavy Strike")
		units.append({
			"name":              clean,
			"campaign_name":     str(raw_n) if raw_n != null else clean,
			"role":              role,
			"hp":                int(agent.get("hp", 30)),
			"max_hp":            maxi(1, int(agent.get("max_hp", agent.get("hp", 30)))),
			"stress":            int(agent.get("stress", 0)),
			"base_ap":           maxi(4, int(agent.get("action_points", 4))),
			"defense":           int(agent.get("defense", role_def_base)),
			"initiative":        int(agent.get("initiative", 20 + int(agent.get("level", 1)) * 2 - i)),
			"aim":               int(agent.get("aim", 5)),
			"psi":               int(agent.get("psi", 5)),
			"melee_power":       int(agent.get("melee_power", 0)),
			"vision_range":      maxi(BASE_VISION_RANGE, int(agent.get("vision_range", BASE_VISION_RANGE))),
			"position":          Vector2i(1, row),
			"kind":              "player",
			"status_effects":    [],
			"available_actions": agent_actions,
			"last_stand_dialogue": str(agent.get("last_stand_dialogue", "")),
			"size_scale":        clampf(float(agent.get("size_scale", 1.0)), 0.5, 5.0),
		})
	for j in range(support_assets.size()):
		var raw_asset: Variant = support_assets[j]
		if typeof(raw_asset) != TYPE_DICTIONARY: continue
		var asset: Dictionary = raw_asset as Dictionary
		var asset_type := str(asset.get("asset_type", "")).to_lower()
		var role := "robot" if asset_type in ["combat_robot", "support_robot"] or asset_type.ends_with("_robot") else "power_armor"
		var row_index := units.size()
		var row: int = mini(GRID_ROWS - 1, 1 + (row_index % maxi(1, GRID_ROWS / 2)) * 2)
		var raw_name: Variant = asset.get("name", null)
		var clean_name: String = str(raw_name).strip_edges() if raw_name != null else ""
		if clean_name == "" or clean_name.to_lower() == "null":
			clean_name = "SUPPORT-%d" % (j + 1)
		var raw_asset_actions: Variant = asset.get("actions", [])
		var asset_actions: Array[String] = []
		if typeof(raw_asset_actions) == TYPE_ARRAY:
			for action: Variant in raw_asset_actions as Array:
				asset_actions.append(str(action))
		if asset_actions.is_empty():
			asset_actions.assign(["Move", "Defend", "Missile Salvo"] if role == "robot" else ["Move", "Defend", "Rifle Burst", "Servo Punch"])
		var hp := maxi(1, int(asset.get("hp", 24)))
		units.append({
			"name":              clean_name,
			"role":              role,
			"asset_type":        asset_type,
			"asset_id":          str(asset.get("id", "")),
			"hp":                hp,
			"max_hp":            maxi(hp, int(asset.get("max_hp", hp))),
			"stress":            0,
			"base_ap":           maxi(1, int(asset.get("action_points", 2))),
			"defense":           int(asset.get("defense", 6 if role == "robot" else 8)),
			"initiative":        int(asset.get("initiative", 16 - row_index)),
			"aim":               int(asset.get("aim", 5)),
			"melee_power":       int(asset.get("melee_power", 0)),
			"vision_range":      BASE_VISION_RANGE,
			"position":          Vector2i(1, row),
			"kind":              "player",
			"status_effects":    [],
			"available_actions": asset_actions,
			"size_scale":        (clampf(float(asset.get("size_scale",3.5)),0.5,5.0) if role == "robot" else 1.15),
		})
	for unit: Dictionary in units:
		unit["ap"] = _player_turn_ap(unit)
		var actions: Array = unit.get("available_actions", [])
		actions.erase("Overwatch")
		if not _overwatch_weapon(unit).is_empty():
			actions.append("Overwatch")
		unit["damage_dealt"] = 0
		unit["damage_taken"] = 0
		unit["kills"] = 0
		unit["actions_used"] = 0
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
	var layout = preload("res://scripts/map_wall_layout.gd")
	var map_data := handoff.get("map", {}) as Dictionary
	return layout.cover_nodes(layout.geometry_for_map(map_data, project_root))

# Updated to match HudController's expected fields: name, is_enemy, active, hp, max_hp
func _refresh_initiative() -> void:
	initiative_entries = []
	var all_units: Array[Dictionary] = []
	for u: Dictionary in player_units:
		if int(u.get("hp", 0)) > 0: all_units.append(u)
	for enemy_index in range(enemy_units.size()):
		var e := enemy_units[enemy_index] as Dictionary
		if int(e.get("hp", 0)) > 0 and _is_enemy_visible_to_player(enemy_index): all_units.append(e)
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

func _vision_range(unit: Dictionary) -> int:
	return _FOGScript.vision_range(unit)

func _unit_can_see(observer: Dictionary, target: Dictionary) -> bool:
	return _FOGScript.can_see(observer, target, func(origin: Vector2i, destination: Vector2i):
		return _battlefield.has_los(origin, destination, []))

func _update_player_visibility() -> void:
	_player_visible_cells = _FOGScript.visible_cells(player_units, GRID_COLS, GRID_ROWS,
		func(origin: Vector2i, destination: Vector2i):
			return _battlefield.has_los(origin, destination, []))
	for cell: Vector2i in _player_visible_cells:
		_explored_cells[cell] = true
	_battlefield.set_fog(_player_visible_cells, _explored_cells)
	for prop: Node2D in _visual_obstacles:
		var prop_cell: Vector2i = prop.tactical_cell
		prop.visible = visual_quality > 0 and _explored_cells.has(prop_cell)
		prop.modulate = Color(1, 1, 1, 1.0 if _player_visible_cells.has(prop_cell) else 0.42)

func _is_enemy_visible_to_player(enemy_index: int) -> bool:
	if enemy_index < 0 or enemy_index >= enemy_units.size():
		return false
	var enemy := enemy_units[enemy_index] as Dictionary
	return _player_visible_cells.has(_cell_position(enemy))

func _visible_enemy_units_for_hud() -> Array[Dictionary]:
	var visible: Array[Dictionary] = []
	for index in range(enemy_units.size()):
		if _is_enemy_visible_to_player(index):
			visible.append(enemy_units[index])
	return visible

func _enemy_engagement_target(enemy_index: int, subtype: String, attack_range: int) -> int:
	var enemy := enemy_units[enemy_index]
	var commander_index := _linked_enemy_commander(enemy_index)
	if commander_index >= 0:
		var commander := enemy_units[commander_index]
		var focus := _select_visible_player_target(commander, "commander", _subtype_attack_range("commander"))
		if focus >= 0 and _unit_can_see(enemy, player_units[focus]):
			var offset := _cell_position(player_units[focus]) - _cell_position(enemy)
			if absi(offset.x) + absi(offset.y) <= attack_range:
				return focus
	return _select_visible_player_target(enemy, subtype, attack_range)

func _linked_enemy_commander(enemy_index: int) -> int:
	var enemy := enemy_units[enemy_index]
	var profile := _mission_data().get("tactical_profile", {}) as Dictionary
	var radius := float(profile.get("command_radius_cells", 0))
	if radius <= 0.0 or enemy.get("enemy_subtype", "") == "commander":
		return -1
	var origin := _cell_position(enemy)
	var best := -1
	var best_distance := INF
	for index in range(enemy_units.size()):
		var candidate := enemy_units[index]
		if index == enemy_index or candidate.get("enemy_subtype", "") != "commander" \
				or int(candidate.get("hp", 0)) <= 0 or candidate.get("enemy_theme") != enemy.get("enemy_theme"):
			continue
		var statuses: Array = candidate.get("status_effects", [])
		if "suppressed" in statuses or "stunned" in statuses or "panicked" in statuses:
			continue
		var position := _cell_position(candidate)
		var distance := origin.distance_to(position)
		if distance <= radius and distance < best_distance and _battlefield.has_los(origin, position, []):
			best = index
			best_distance = distance
	return best

func _select_visible_player_target(enemy: Dictionary, subtype: String, attack_range: int) -> int:
	var ep := _cell_position(enemy)
	var profile := _mission_data().get("tactical_profile", {}) as Dictionary
	var best := -1
	var best_score := -INF
	var best_in_range := false
	for index in range(player_units.size()):
		var player := player_units[index] as Dictionary
		if not _unit_can_see(enemy, player):
			continue
		var position := _cell_position(player)
		var distance := absi(ep.x - position.x) + absi(ep.y - position.y)
		var in_range := distance <= attack_range
		var score := -float(distance) * float(profile.get("distance_weight", 1.0))
		if in_range and not profile.is_empty():
			var max_hp := int(player.get("max_hp", player.get("hp", 1)))
			if int(player.get("hp", 0)) < max_hp * 0.4:
				score += int(profile.get("wounded_weight", 0))
			var role := str(player.get("role", "")).to_lower()
			if role in ["psi", "sniper", "commander"]:
				score += int(profile.get("specialist_weight", 0))
			elif role in ["samurai", "assault", "heavy"]:
				score += int(profile.get("specialist_weight", 0)) * 0.5
		if in_range and subtype in ["sniper", "elite", "commander"]:
			# Prefer an available shot at an exposed target over a slightly closer guard.
			score -= 1.5 * int(player.get("defense", 4))
			if index in defend_indices:
				score -= 6.0
		if (in_range and not best_in_range) or (in_range == best_in_range and score > best_score):
			best_score = score
			best = index
			best_in_range = in_range
	return best

func _current_active_player() -> Dictionary:
	if active_player_index < 0 or active_player_index >= player_units.size():
		return {}
	return player_units[active_player_index] as Dictionary

func _current_target() -> Dictionary:
	if enemy_units.is_empty(): return {}
	if selected_target_index < 0 or selected_target_index >= enemy_units.size():
		selected_target_index = 0
	if int(enemy_units[selected_target_index].get("hp", 0)) <= 0 or not _is_enemy_visible_to_player(selected_target_index):
		for i in range(enemy_units.size()):
			if int(enemy_units[i].get("hp", 0)) > 0 and _is_enemy_visible_to_player(i):
				selected_target_index = i
				break
	if int(enemy_units[selected_target_index].get("hp", 0)) <= 0 or not _is_enemy_visible_to_player(selected_target_index):
		return {}
	return enemy_units[selected_target_index] as Dictionary

func _selected_target_validity() -> void:
	if enemy_units.is_empty(): selected_target_index = 0; return
	if selected_target_index < 0 or selected_target_index >= enemy_units.size() \
			or int(enemy_units[selected_target_index].get("hp", 0)) <= 0 \
			or not _is_enemy_visible_to_player(selected_target_index):
		for i in range(enemy_units.size()):
			if int(enemy_units[i].get("hp", 0)) > 0 and _is_enemy_visible_to_player(i):
				selected_target_index = i
				return

func _enemy_at_cell(cell: Vector2i) -> int:
	for i in range(enemy_units.size()):
		if int(enemy_units[i].get("hp", 0)) > 0 \
				and _is_enemy_visible_to_player(i) \
				and _cell_position(enemy_units[i]) == cell:
			return i
	return -1

func _assassination_target_index() -> int:
	if objective.get("type") != "assassination":
		return -1
	var priority := {"commander": 4, "elite": 3, "heavy": 2, "grunt": 1}
	var target := -1
	var best_priority := -1
	for index in range(mini(initial_enemy_count, enemy_units.size())):
		var rank := int(priority.get(enemy_units[index].get("enemy_subtype", ""), 0))
		if rank > best_priority:
			target = index
			best_priority = rank
	return target

func _objective_interaction_available() -> bool:
	return not objective.has("hold_until_turn") and (not objective.get("once_per_turn", false) \
		or int(objective.get("last_interaction_turn", -1)) != turn_number)

func _elimination_objective_met() -> bool:
	var target := _assassination_target_index()
	if target >= 0 and int(enemy_units[target].get("hp", 0)) <= 0:
		objective_completed = true
		objective_progress = int(objective.get("progress_needed", 1))
		return true
	if objective.get("type", "") == "defend" or (objective.get("needs_marker", false) \
			and not str(objective.get("action_key", "")).is_empty()):
		return false
	var eliminated := _enemy_alive_count() == 0
	if eliminated and objective.get("type", "") == "containment":
		objective_completed = true
		objective_progress = int(objective.get("progress_needed", 1))
	return eliminated

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

func _is_interior_map() -> bool:
	return _ENCScript.is_interior_map(_map_data())

func _decorative_vehicles(vehicles: Dictionary) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	if _is_interior_map(): return result
	for key: String in ["agent_vehicle", "enemy_vehicle"]:
		var vehicle := vehicles.get(key, {}) as Dictionary
		if not vehicle.is_empty(): result.append(vehicle)
	return result

func _map_data() -> Dictionary:
	var raw: Variant = handoff.get("map", {})
	return raw as Dictionary if typeof(raw) == TYPE_DICTIONARY else {}

# ─── Text helpers ─────────────────────────────────────────────────────────────

func _draw_text(text: String, pos: Vector2, font_size: int, color: Color) -> void:
	draw_string(ThemeDB.fallback_font, pos, text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, color)

# Presentation adapters: no damage, AP, AI or mission result mutations here.
func _configure_visual_hud() -> void:
	_hud.supported_actions = _ACTION_DEFS.keys()
	_hud.action_tooltips = {
		"Overwatch": "%d AP · Fire once if a moving hostile ends its move in sight and weapon range." % _action_ap_cost("Overwatch"),
		"Psi Focus": "%d AP · Relieve up to %d stress per living, standing squad member." % [
			_action_ap_cost("Psi Focus"), _ACTION_DEFS["Psi Focus"]["stress_relief"]],
	}
	for action: String in _ACTION_DEFS:
		var definition: Dictionary = _ACTION_DEFS[action]
		if definition["type"] == "HEAL":
			_hud.action_tooltips[action] = "%d AP · Restore up to %d HP to this agent." % [
				_action_ap_cost(action), definition["heal"]]
	if not _hud.has_signal("quality_changed"): return
	_hud.mission_title = str(_mission_data().get("title", "TACTICAL INSERTION"))
	_hud.objective_text = str(_mission_data().get("objective_text", "Complete the objective"))
	_hud.quality = visual_quality
	_hud._quality_button.text = "QUALITY: " + ["LOW", "MEDIUM", "HIGH"][visual_quality]
	_hud.quality_changed.connect(_set_visual_quality)

func _set_visual_quality(level: int) -> void:
	var rebuild_depth := (visual_quality==0)!=(clampi(level,0,2)==0)
	visual_quality = clampi(level, 0, 2)
	if rebuild_depth and visual_mode and battle_started:
		_build_visual_obstacles()
		_update_visual_context()
		return
	if "quality" in _battlefield: _battlefield.quality = visual_quality
	_visual_fx.quality = visual_quality
	if is_instance_valid(_visual_lighting):
		_visual_lighting.quality = visual_quality
		_visual_lighting.visible = visual_quality>0
	for token: Node in _unit_tokens.values():
		if "visual_quality" in token: token.visual_quality = visual_quality
	for prop: Node2D in _visual_obstacles: prop.visible = visual_quality > 0
	if is_instance_valid(_hud) and "environment_depth_enabled" in _hud:
		_hud.environment_depth_enabled=environment_depth_enabled
		_hud.queue_redraw()
	var config := ConfigFile.new()
	config.load("user://combat_visual.cfg")
	config.set_value("graphics", "environment_depth",environment_depth_enabled)
	config.set_value("graphics", "quality", visual_quality)
	config.save("user://combat_visual.cfg")

func _build_visual_obstacles() -> void:
	for prop: Node2D in _visual_obstacles: prop.queue_free()
	_visual_obstacles.clear()
	if not visual_mode: return
	var path := str(_map_data().get("path", "")).to_lower()
	var depth = preload("res://scripts/environment_depth.gd").new() if environment_depth_enabled and visual_quality>0 else null
	if "--legacy-environment" in OS.get_cmdline_user_args() and environment_depth_enabled and visual_quality>0:
		depth=preload("res://scripts/environment_depth_legacy.gd").new()
		depth.prepare(map_texture,_battlefield,path)
	elif depth!=null: depth.prepare(map_texture,_battlefield,path,_asset_path(path))
	var seen: Dictionary = {}
	var render_walls: Array[Dictionary]=[]
	if _battlefield.top_down and depth!=null:
		var replacements: Array[Dictionary]=preload("res://scripts/environment_catalog.gd").art_walls(path)
		var replaced: Dictionary={}
		for entry: Dictionary in replacements:replaced[entry.source_object_id]=true
		for wall: Dictionary in cover_nodes:
			if not replaced.has(str(wall.get("wall_id",""))):render_walls.append(wall)
		render_walls.append_array(replacements)
	elif not _battlefield.top_down:render_walls.assign(cover_nodes)
	for wall: Dictionary in render_walls:
		var id := str(wall.get("wall_id", ""))
		if id.is_empty() or seen.has(id): continue
		seen[id] = true
		var prop := preload("res://scripts/visual_obstacle.gd").new()
		_units_layer.add_child(prop)
		prop.configure(wall, _battlefield, map_texture,depth)
		_visual_obstacles.append(prop)
	_battlefield.set_depth_props(_visual_obstacles)
	_battlefield.weather = "interior" if _is_interior_map() else ("dust" if "wasteland" in path else "rain")
	if is_instance_valid(_visual_lighting):_visual_lighting.free()
	_visual_lighting=preload("res://scripts/visual_lighting.gd").new()
	_map_root.add_child(_visual_lighting)
	_map_root.move_child(_visual_lighting,_units_layer.get_index())
	_visual_lighting.configure(map_texture,_battlefield,_battlefield.weather,path)
	_set_visual_quality(visual_quality)

func _update_prop_occlusion() -> void:
	if _visual_obstacles.is_empty(): return
	var bodies: Array[Rect2]=[]
	for key: String in _unit_tokens:
		var token: Node2D=_unit_tokens[key]
		if not token.has_method("_visible_body_rect") or int(token.unit_data.get("hp",0))<=0:continue
		var body: Rect2=token._visible_body_rect()
		bodies.append(Rect2(token.position+body.position,body.size))
	# Route ribbons remain visible through foreground props while previewing.
	for cell: Vector2i in _battlefield.path_cells:
		var point: Vector2=_battlefield.cell_to_world(cell)
		bodies.append(Rect2(point-Vector2(8,5),Vector2(16,10)))
	for prop: Node2D in _visual_obstacles: prop.update_occlusion_for_units(bodies)

func _update_visual_context() -> void:
	var active := _current_active_player()
	_update_prop_occlusion()
	if not _hud.has_signal("quality_changed"): return
	if objective.get("type", "") == "containment":
		_hud.objective_text = "HOLD // %s" % str(_mission_data().get("objective_text","Hold the breach zone"))
	elif objective.get("type", "") == "defend":
		_hud.objective_text = "HOLD %d/%d // Keep hostiles outside the marked zone." % [
			objective_progress, int(objective.get("defend_turns_required", 4))]
	elif not objective.get("phase_labels", []).is_empty():
		_hud.objective_text = "%d/%d // %s" % [
			objective_progress, int(objective.get("progress_needed", 1)), str(objective.get("label", ""))]
	else:
		_hud.objective_text = "%d/%d // %s" % [objective_progress, int(objective.get("progress_needed",1)), str(_mission_data().get("objective_text","Complete the objective"))]
	_hud.target_info = {}
	_hud.target_anchor_node = null
	if _gamepad_cell.x >= 0 and _enemy_at_cell(_gamepad_cell) < 0:
		return
	var target := _current_target()
	var atype := _action_type(selected_action)
	if turn_side != "player" or target.is_empty() or active.is_empty() or atype not in ["FIRE", "MELEE", "FIRE_AOE"]: return
	var from := _cell_position(active)
	var to := _cell_position(target)
	var distance := absi(from.x-to.x)+absi(from.y-to.y)
	var rng := _action_range(selected_action)
	if rng == 0: rng = _role_attack_range(str(active.get("role", "")), selected_action)
	var los: bool = _battlefield.has_los(from,to,[])
	var chance := clampf(50.0+float(active.get("aim",5))*2-float(target.get("defense",6))*2,20,95)
	_hud.target_info = target.duplicate()
	_hud.target_anchor_node = _unit_tokens.get("e%d" % selected_target_index,null)
	var portrait_key := str(target.get("name", "enemy"))
	if not _visual_enemy_portraits.has(portrait_key):
		var theme := str(target.get("enemy_theme", "generic"))
		var portrait_path := "assets/ui/portraits/enemy_%s_%02d.png" % [theme,(portrait_key.hash() & 0x7fffffff)%20+1]
		var portrait := _load_tex(portrait_path)
		if portrait == null: portrait = _load_tex("assets/ui/portraits/enemy_%s.png" % str(target.get("enemy_subtype","grunt")))
		_visual_enemy_portraits[portrait_key] = portrait
	_hud.target_info["portrait"] = _visual_enemy_portraits[portrait_key]
	_hud.target_info["detail"] = "DISTANCE %d  //  RANGE %d  //  %d AP" % [distance,rng,_action_ap_cost(selected_action)]
	_hud.target_info["chance_label"] = "OUT OF RANGE" if distance > rng else ("OBSTACLE: SIGHT BLOCKED" if not los else "SHOT: %d %%" % int(chance))

func _visual_cell_hovered(cell: Vector2i) -> void:
	if cell.x < 0 or cell.y < 0 or cell.x >= GRID_COLS or cell.y >= GRID_ROWS:
		var no_path: Array[Vector2i] = []
		_battlefield.show_path(no_path)
		return
	if not battle_started or battle_ended or turn_side != "player": return
	if _action_type(selected_action) != "MOVE": return
	var active := _current_active_player()
	if active.is_empty(): return
	var route: Array[Vector2i] = _battlefield.find_path(_cell_position(active),cell)
	if route.size()-1 > int(active.get("ap",0)) or _is_cell_occupied(cell,active_player_index,-1): route.clear()
	_battlefield.show_path(route)
	_update_prop_occlusion()

func _visual_unit_hovered(id: int, enemy: bool) -> void:
	if enemy and id >= 0 and id < enemy_units.size() and int(enemy_units[id].get("hp",0)) > 0:
		selected_target_index = id
		for key: String in _unit_tokens:
			if key.begins_with("e") and is_instance_valid(_unit_tokens[key]):
				_unit_tokens[key].set_targeted(key == "e%d" % id and _action_type(selected_action) in ["FIRE","MELEE","PSI","FIRE_AOE"])
		_update_visual_context()
		_hud.queue_redraw()

func _visual_move_token(key: String, origin: Vector2i, destination: Vector2i, data: Dictionary) -> void:
	var tok = _unit_tokens[key]
	if not tok.has_method("move_route"):
		tok.move_to(_battlefield.cell_to_world(destination),data)
		return
	var points: Array[Vector2] = []
	var path: Array[Vector2i] = _battlefield.find_path(origin,destination)
	for i in range(1,path.size()): points.append(_battlefield.cell_to_world(path[i]))
	if points.is_empty(): points.append(_battlefield.cell_to_world(destination))
	tok.move_route(points,data)

func _visual_attack(attacker_key: String, target_key: String, action_type: String, action_name: String = "") -> void:
	var attacker = _unit_tokens[attacker_key]
	var target = _unit_tokens[target_key]
	if not attacker.has_method("play_action"):
		attacker.attack_lunge(target.position)
		return
	var kind := "melee" if action_type == "MELEE" else ("psi" if action_type.begins_with("PSI") else "fire")
	if "Plasma" in action_name: kind = "plasma"
	attacker.play_action("fire" if kind == "plasma" else kind,target.position)
	var a: Vector2 = attacker.position-Vector2(0,attacker._sh*0.55)
	var b: Vector2 = target.position-Vector2(0,target._sh*0.5)
	var shots := 3 if "Burst" in action_name else 1
	for shot in range(shots): _visual_fx.burst(kind,a,b,float(shot)*0.12)

func _visual_self_effect(kind: String) -> void:
	if not visual_mode: return
	var key := "p%d" % active_player_index
	if _unit_tokens.has(key):
		var tok = _unit_tokens[key]
		tok.play_action(kind)
		if kind != "cover":
			_visual_fx.burst(kind,tok.position,tok.position)

func _toggle_visual_interface() -> void:
	if not battle_started or battle_ended: return
	var premium: bool = not _hud.has_signal("quality_changed")
	_hud_layer.remove_child(_hud)
	_hud.queue_free()
	_hud = preload("res://scripts/visual_hud.gd").new() if premium else _HUDScript.new()
	_hud_layer.add_child(_hud)
	_hud.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_fit_hud_viewport()
	_configure_visual_hud()
	_sync_display()

func _unhandled_key_input(event: InputEvent) -> void:
	# The map root does not take GUI focus; route global tactical shortcuts here.
	_gui_input(event)

func _unhandled_input(event: InputEvent) -> void:
	if battle_ended or not event is InputEventJoypadButton or not event.pressed:
		return
	if event.button_index == JOY_BUTTON_A and not battle_started:
		_confirm_tactical_action("GAMEPAD")
		get_viewport().set_input_as_handled()
		return
	if not battle_started or turn_side != "player":
		return
	match event.button_index:
		JOY_BUTTON_A:
			if not _hud.gamepad_action.is_empty():
				_hud.close_gamepad_actions(true)
			elif pending_retreat_confirmation:
				_execute_action("RETREAT")
			elif pending_end_turn_confirmation:
				_confirm_tactical_action("GAMEPAD")
			elif _gamepad_cell.x >= 0:
				_on_cell_clicked(_gamepad_cell, true)
		JOY_BUTTON_X:
			if _hud.gamepad_action.is_empty() and not pending_end_turn_confirmation and not pending_retreat_confirmation:
				_clear_gamepad_cursor()
				_hud.step_gamepad_action(0)
			else:
				_hud.close_gamepad_actions()
		JOY_BUTTON_DPAD_UP:
			if _hud.gamepad_action.is_empty():
				_move_gamepad_cursor(Vector2i.UP)
			else:
				_hud.step_gamepad_action(-1)
		JOY_BUTTON_DPAD_DOWN:
			if _hud.gamepad_action.is_empty():
				_move_gamepad_cursor(Vector2i.DOWN)
			else:
				_hud.step_gamepad_action(1)
		JOY_BUTTON_DPAD_LEFT:
			_move_gamepad_cursor(Vector2i.LEFT)
		JOY_BUTTON_DPAD_RIGHT:
			_move_gamepad_cursor(Vector2i.RIGHT)
		JOY_BUTTON_RIGHT_SHOULDER:
			_hud.close_gamepad_actions()
			_clear_gamepad_cursor()
			_cycle_active_unit()
		JOY_BUTTON_LEFT_STICK:
			_frame_squad()
		JOY_BUTTON_Y:
			_hud.close_gamepad_actions()
			_execute_action("END TURN")
		JOY_BUTTON_B:
			if not _hud.gamepad_action.is_empty():
				_hud.close_gamepad_actions()
				get_viewport().set_input_as_handled()
				return
			if not pending_end_turn_confirmation and not pending_retreat_confirmation:
				if _gamepad_cell.x < 0:
					return
				_clear_gamepad_cursor()
				get_viewport().set_input_as_handled()
				return
			pending_end_turn_confirmation = false
			pending_retreat_confirmation = false
			status_line = "Confirmation cancelled."
			_sync_display()
		_:
			return
	_hud.gamepad_hints = true
	_hud.queue_redraw()
	get_viewport().set_input_as_handled()

func _move_gamepad_cursor(step: Vector2i) -> void:
	if not _hud.gamepad_action.is_empty():
		return
	var active := _current_active_player()
	if active.is_empty() or _battlefield == null:
		return
	var origin := _cell_position(active) if _gamepad_cell.x < 0 else _gamepad_cell
	_gamepad_cell = (origin + step).clamp(Vector2i.ZERO, Vector2i(GRID_COLS - 1, GRID_ROWS - 1))
	_camera.force_update_scroll()
	var point: Vector2 = _battlefield.get_global_transform_with_canvas() * _battlefield.cell_to_world(_gamepad_cell)
	var bounds: Rect2 = _hud.board_cursor_bounds()
	var visible_point := point.clamp(bounds.position, bounds.end)
	if visible_point != point:
		_camera.position += (point - visible_point) / _camera.zoom
		_camera.force_update_scroll()
	_battlefield.hovered_cell = _gamepad_cell
	_visual_cell_hovered(_gamepad_cell)
	if _action_type(selected_action) in ["FIRE", "MELEE", "PSI", "FIRE_AOE"]:
		_preview_gamepad_target()
	_battlefield.queue_redraw()

func _preview_gamepad_target() -> void:
	var target := _enemy_at_cell(_gamepad_cell)
	if target >= 0:
		_visual_unit_hovered(target, true)
		return
	selected_target_index = -1
	for key: String in _unit_tokens:
		if key.begins_with("e") and is_instance_valid(_unit_tokens[key]):
			_unit_tokens[key].set_targeted(false)
	_update_visual_context()
	_hud.queue_redraw()

func _clear_gamepad_cursor() -> void:
	if _gamepad_cell.x < 0:
		return
	_gamepad_cell = Vector2i(-1, -1)
	if _battlefield != null:
		_battlefield.hovered_cell = _gamepad_cell
		_visual_cell_hovered(_gamepad_cell)
		_battlefield.queue_redraw()

func _confirm_tactical_action(source: String) -> void:
	if not battle_started:
		_start_combat(source)
	elif pending_end_turn_confirmation:
		_clear_gamepad_cursor()
		_end_player_turn()
	elif _action_type(selected_action) in ["FIRE", "MELEE", "PSI", "FIRE_AOE", "PSI_HEAL", "HEAL"]:
		_resolve_selected_attack()

func _fit_hud_viewport() -> void:
	if is_instance_valid(_banner):_banner.size=size
	if _hud.has_method("fit_viewport"):
		_hud.fit_viewport(size)
	else:
		_hud.scale = Vector2.ONE
		_hud.size = size
		_hud.position = Vector2.ZERO
		_hud._reposition_buttons()

func _activate_player_from_portrait(index: int) -> void:
	active_player_index = index
	pending_end_turn_confirmation = false
	var unit := player_units[index] as Dictionary
	selected_action = "Move" if "Move" in unit.get("available_actions",[]) else "MOVE"
	var ap := int(unit.get("ap",0))
	status_line = "%s — your move (%d AP)." % [unit.get("name","Agent"),ap] if ap > 0 else "%s: no AP remaining this turn." % unit.get("name","Agent")
	if _camera != null: _camera.position = _battlefield.cell_to_world(_cell_position(unit))
	_refresh_initiative()
	_sync_display()

func _pick_map_unit(screen_point: Vector2) -> Node2D:
	var nearest: Node2D = null
	var nearest_distance := INF
	for key: String in _unit_tokens:
		var token = _unit_tokens[key]
		if not is_instance_valid(token) or not token.has_method("hit_test_screen"): continue
		if not token.hit_test_screen(screen_point): continue
		var center: Vector2 = token.get_global_transform_with_canvas()*Vector2(0,-token._sh*0.5)
		var distance := center.distance_squared_to(screen_point)
		if distance < nearest_distance:
			nearest_distance = distance
			nearest = token
	return nearest
