extends SceneTree
## Runtime assertions against the actual mission scene and its existing mechanics.
var failures: Array[String] = []
var checks := 0
var scene

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, description: String) -> void:
	checks += 1
	if not condition:
		failures.append(description)
		push_error("VISUAL_CHECK_FAILED: "+description)

func run() -> void:
	root.size = Vector2i(1280,720)
	scene = load("res://scenes/combat_mission_ui.tscn").instantiate()
	root.add_child(scene)
	await process_frame
	await process_frame
	check(scene.battle_started, "real mission auto deploy")
	check(scene._hud.has_signal("quality_changed"), "premium HUD integrated")
	check(scene._unit_tokens.size() >= scene.player_units.size()+scene.enemy_units.size(), "all encounter units instantiated")
	check(scene._units_layer.y_sort_enabled, "units and props share depth sorting")
	var initial_players: Array[Dictionary] = scene.player_units.duplicate(true)
	var initial_enemies: Array[Dictionary] = scene.enemy_units.duplicate(true)
	var board = scene._battlefield
	var map_count := 0
	var wall_layout = load("res://scripts/map_wall_layout.gd")
	var paths := DirAccess.get_files_at(scene.project_root.path_join("assets/maps"))
	for filename: String in paths:
		if not filename.ends_with(".walls.json"): continue
		var path: String = scene.project_root.path_join("assets/maps").path_join(filename)
		var geometry: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
		var covers: Array[Dictionary] = wall_layout.cover_nodes(geometry)
		board.configure(Vector2(5120,2880), null, covers, Vector2i(20,14))
		check(not covers.is_empty(),filename+": walls load")
		var first: Vector2i = covers[0]["cell"]
		check(board.is_wall(first),filename+": collision retained")
		var open: Vector2i = board.nearest_open_cell(first)
		check(not board.is_wall(open),filename+": walkable spawn")
		check(board.find_path(open,first).is_empty(),filename+": blocked path stays blocked")
		map_count += 1
	board.configure(Vector2(5120,2880),scene.map_texture,scene.cover_nodes,scene.objective["cell"])
	scene._build_visual_obstacles()
	for prop in scene._visual_obstacles:
		check(prop.top.size() >= 3,"visual obstacle has surveyed polygon")
	var state_before: String = JSON.stringify([scene.player_units,scene.enemy_units,scene.turn_number])
	for level in range(3): scene._set_visual_quality(level)
	await key(KEY_F9)
	check(not scene._hud.has_signal("quality_changed"),"legacy HUD accessible")
	await key(KEY_F9)
	check(scene._hud.has_signal("quality_changed"),"premium HUD restored")
	check(JSON.stringify([scene.player_units,scene.enemy_units,scene.turn_number]) == state_before,"quality/interface preserve tactical state")
	# Controlled open lane to verify actual actions, independent of random map spawns.
	var empty: Array[Dictionary] = []
	board.configure(Vector2(5120,2880),scene.map_texture,empty,Vector2i(20,14))
	scene.cover_nodes = empty
	scene.player_units[0]["position"] = Vector2i(5,5)
	scene.player_units[0]["ap"] = 20
	scene.player_units[0]["aim"] = 100
	scene.enemy_units[0]["position"] = Vector2i(7,5)
	scene.enemy_units[0]["hp"] = 100
	scene.enemy_units[0]["max_hp"] = 100
	scene.active_player_index = 0
	scene._resize_tokens()
	scene.selected_action = "MOVE"
	scene._sync_display()
	var ap: int = scene.player_units[0]["ap"]
	var click_position: Vector2 = root.get_canvas_transform() * board.cell_to_world(Vector2i(6,5))
	await click(click_position)
	check(scene.player_units[0]["position"] == Vector2i(6,5),"accepted move updates real cell")
	check(scene.player_units[0]["ap"] == ap-1,"movement AP unchanged")
	await create_timer(0.25).timeout
	var tok = scene._unit_tokens["p0"]
	check(tok.position.distance_to(board.cell_to_world(Vector2i(6,5))) < 0.1,"rendered movement reaches tactical position")
	check(not tok.play_action("nonexistent"),"missing animation reported honestly")
	seed(1)
	ap = scene.player_units[0]["ap"]
	scene._attack_enemy(0,"Rifle Burst")
	check(scene.player_units[0]["ap"] == ap-1,"fire uses original AP cost")
	check(not scene._visual_fx.effects.is_empty(),"accepted shot creates effects")
	ap = scene.player_units[0]["ap"]
	scene._attack_enemy(0,"Katana Slash")
	check(scene.player_units[0]["ap"] == ap-1,"melee uses original action")
	scene.player_units[0]["stress"] = 50
	scene._apply_psi_focus()
	check(scene.player_units[0]["stress"] == 25,"PSI retains original stress relief")
	scene.player_units[0]["max_hp"] = 40
	scene.player_units[0]["hp"] = 1
	if "Trauma Patch" not in scene.player_units[0]["available_actions"]:
		scene.player_units[0]["available_actions"].append("Trauma Patch")
	scene._apply_medical_utility("Trauma Patch")
	check(scene.player_units[0]["hp"] == 13,"healing retains original amount")
	scene.player_units[0]["ap"] = 20
	ap = scene.player_units[0]["ap"]
	scene._apply_missile_salvo(Vector2i(7,5))
	check(scene.player_units[0]["ap"] == ap-2,"missiles retain original AP cost")
	scene._execute_action("Defend")
	check(0 in scene.defend_indices,"cover/defend toggles")
	scene._execute_action("Overwatch")
	check(0 in scene.overwatch_indices,"overwatch toggles")
	scene.player_units[0]["hp"] = 40
	var turn: int = scene.turn_number
	scene._end_player_turn()
	check(scene.turn_side == "enemy","enemy phase starts")
	scene._resolve_enemy_turn()
	check(scene.turn_side == "player" and scene.turn_number == turn+1,"enemy AI returns control")
	# Repeatable preview uses actual mechanics and never moves the selected agent.
	scene.selected_action = "Rifle Burst"
	scene.selected_target_index = 0
	scene._sync_display()
	check(not scene._hud.target_info.is_empty(),"contextual target reflects actual combat")
	for _i in range(100): scene._visual_fx.burst("explosion",Vector2.ZERO,Vector2.ONE)
	check(scene._visual_fx.effects.size() <= 64,"effects bounded")
	# Smoke lives longer than its explosion; use the actual remaining lifetimes.
	var remaining := 0.0
	for effect: Dictionary in scene._visual_fx.effects:
		remaining = maxf(remaining,float(effect["life"])-float(effect["age"]))
	await create_timer(remaining+0.15).timeout
	await process_frame
	check(scene._visual_fx.effects.is_empty(),"effects reclaimed")
	# Result UI and Python JSON writer are the actual existing implementation.
	var result_root := OS.get_cmdline_user_args()
	for i in range(result_root.size()-1):
		if result_root[i] == "--result-root": scene.project_root = result_root[i+1]
	scene._end_combat("victory")
	check(scene.battle_ended and scene._results.visible,"mission completion/results functional")
	check(scene._results._extract_btn.visible,"extraction control visible after mission")
	print("VISUAL_REGRESSION: ",checks," checks; ",map_count," maps; failures=",failures.size())
	scene.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)

func click(pos: Vector2) -> void:
	var motion := InputEventMouseMotion.new()
	motion.position = pos
	Input.parse_input_event(motion)
	await process_frame
	for pressed: bool in [true,false]:
		var event := InputEventMouseButton.new()
		event.position = pos
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		Input.parse_input_event(event)
		await process_frame

func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	Input.parse_input_event(event)
	await process_frame
