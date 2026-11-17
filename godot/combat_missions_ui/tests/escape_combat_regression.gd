extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var fixture:=ProjectSettings.globalize_path("user://escape-test-handoff.json")
	var file:=FileAccess.open(fixture,FileAccess.WRITE)
	file.store_string(JSON.stringify({"asset_base_dir":ProjectSettings.globalize_path("res://../.."),"audio":{"enabled":false},"map":{"path":"assets/maps/cybercity_inner_02_safehouse.png"},"mission":{"title":"Escape regression","objective_type":"hack","risk_level":1},"squad":[{"name":"Test","role":"samurai","hp":24,"max_hp":24}]}));file.close()
	var scene=load("res://scenes/combat_mission_ui.tscn").instantiate()
	scene.handoff_path=fixture
	root.add_child(scene)
	await process_frame
	await process_frame
	assert(scene.battle_started and not scene.battle_ended)
	var state:=JSON.stringify([scene.player_units,scene.enemy_units,scene.turn_number,scene.turn_side,scene.objective])
	# Exercise actual keyboard routing, including repeated Escape with no overlay.
	for premium in [true,false]:
		if not premium:scene._toggle_visual_interface()
		scene.show_combat_log=true;scene._hud.show_log=true
		if "settings_open" in scene._hud:scene._hud.settings_open=true
		for press in range(2):
			var event:=InputEventKey.new()
			event.keycode=KEY_ESCAPE;event.pressed=true
			Input.parse_input_event(event)
			await process_frame
			event.pressed=false;Input.parse_input_event(event)
			await process_frame
			assert(is_instance_valid(scene) and scene.battle_started and not scene.battle_ended,"Escape must never exit or end the battle")
			assert(JSON.stringify([scene.player_units,scene.enemy_units,scene.turn_number,scene.turn_side,scene.objective])==state,"Escape must preserve tactical state")
			assert(not scene.show_combat_log and not scene._hud.show_log)
			if "settings_open" in scene._hud:assert(not scene._hud.settings_open)
	scene.queue_free();await process_frame
	DirAccess.remove_absolute(fixture)
	print("ESCAPE_COMBAT_CHECKS_PASSED")
	quit()
