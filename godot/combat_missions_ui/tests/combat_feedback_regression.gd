extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var scene = load("res://scenes/combat_mission_ui.tscn").instantiate()
	scene.handoff_path = "user://combat-feedback-fixture.json"
	var fixture := FileAccess.open(scene.handoff_path,FileAccess.WRITE)
	fixture.store_string(JSON.stringify({"mission":{"risk_level":3}, "squad":[{"name":"Tester","role":"samurai","hp":20,"max_hp":20}]}))
	fixture.close()
	root.add_child(scene)
	await process_frame
	await process_frame
	var board = scene._battlefield
	scene.active_player_index = 0
	scene.player_units[0]["position"] = Vector2i(5,5)
	scene.player_units[0]["ap"] = 4
	scene.enemy_units[0]["position"] = Vector2i(20,5)
	board._opaque_cells.clear()
	board._opaque_cells.append(Vector2i(6,5))
	scene.selected_action = "Pistol Shot"
	scene.selected_target_index = 0
	var before := JSON.stringify([scene.player_units,scene.enemy_units])
	scene._attack_enemy(0,"Pistol Shot")
	assert(scene.status_line.begins_with("Cible hors de portée"), "range takes priority over blocked LOS")
	assert("distance 15" in scene.status_line, "actual distance explained")
	assert(scene._hud.target_info.chance_label=="OUT OF RANGE", "target card matches click feedback")
	assert(JSON.stringify([scene.player_units,scene.enemy_units])==before, "rejected shot spends no AP or HP")
	scene.enemy_units[0]["position"] = Vector2i(7,5)
	before = JSON.stringify([scene.player_units,scene.enemy_units])
	scene._attack_enemy(0,"Pistol Shot")
	assert(scene.status_line.begins_with("Tir bloqué par un obstacle"), "in-range obstruction uses generic accurate wording")
	assert(JSON.stringify([scene.player_units,scene.enemy_units])==before)
	assert(scene._hud.target_info.chance_label=="OBSTACLE: SIGHT BLOCKED")
	var vehicles := {"agent_vehicle":{"name":"arrival VTOL"},"enemy_vehicle":{"name":"enemy vehicle"}}
	for path in ["city_interior_blacksite_lab.png", "cybercity_inner_02_safehouse.png", "wasteland_inner_01_bunker.png", "city_maintenance_tunnel.png"]:
		scene.handoff = {"map":{"path":"assets/maps/"+path}}
		assert(scene._decorative_vehicles(vehicles).is_empty(), "interiors omit every decorative vehicle")
	scene.handoff = {"map":{"path":"assets/maps/city_exterior_neon_market_alley.png"}}
	assert(scene._decorative_vehicles(vehicles)==[vehicles.agent_vehicle,vehicles.enemy_vehicle], "exterior vehicles retained")
	assert(vehicles.size()==2, "source encounter unchanged")
	var generator = load("res://scripts/encounter_generator.gd").new()
	for filename: String in DirAccess.get_files_at(scene.project_root.path_join("assets/maps")):
		if not filename.ends_with(".png"): continue
		var map := {"path":"assets/maps/"+filename}
		if not generator.is_interior_map(map): continue
		var encounter: Dictionary = generator.generate({"map":map,"mission":{"risk_level":10,"faction":"Samurai Consortium"}},40,28)
		assert(encounter.vehicles.is_empty(), "no interior arrival or decorative enemy vehicle")
		for enemy: Dictionary in encounter.enemy_units:
			assert(not enemy.get("is_vehicle",false), "no interior vehicle combat unit")
	scene.handoff = {"map":{"path":"assets/maps/city_interior_blacksite_lab.png"},"support_assets":[{"name":"Mantis", "asset_type":"power_armor", "hp":40, "actions":["Move","Rifle Burst"]}]}
	var allies: Array[Dictionary] = scene._build_player_units()
	assert(allies.size()==1 and allies[0].role=="power_armor", "power armor remains deployable indoors")
	DirAccess.remove_absolute(scene.handoff_path)
	scene.queue_free()
	await process_frame
	print("COMBAT_FEEDBACK_CHECKS_PASSED")
	quit()
