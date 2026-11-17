extends SceneTree
## Real-renderer catalogue QA. Fixtures use genuine source maps and wall surveys.
var scene
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var args := OS.get_cmdline_user_args()
	var output := ProjectSettings.globalize_path("res://../../work/combat-21")
	var baseline := "--baseline" in args
	for i in range(args.size()-1):
		if args[i]=="--output": output=args[i+1]
	DirAccess.make_dir_recursive_absolute(output)
	var base := ProjectSettings.globalize_path("res://../..")
	var maps := ["city_exterior_neon_market_alley","city_industrial_factory_floor","city_interior_blacksite_lab","wasteland_outdoor_01_dust_road_ambush"]
	for name: String in maps:
		var payload := {"asset_base_dir":base,"audio":{"enabled":false},"campaign":{"corp_name":"CYBERCITY 2085"},"mission":{"title":name.replace("_"," "),"objective_text":"Atteindre et sécuriser le terminal","objective_type":"hack","starting_enemy_count":3,"risk_level":3},"map":{"path":"assets/maps/%s.png"%name,"environment":"wasteland" if "wasteland" in name else "city"},"squad":[{"name":"Rook","role":"samurai","hp":24,"max_hp":24,"portrait_path":"assets/ui/portraits/agent_male_01.png"},{"name":"Longshot","role":"sniper","hp":18,"max_hp":24,"portrait_path":"assets/ui/portraits/agent_male_02.png"},{"name":"Oracle","role":"psi","hp":16,"max_hp":20,"portrait_path":"assets/ui/portraits/agent_male_03.png"}]}
		var file := FileAccess.open(output.path_join("handoff.json"),FileAccess.WRITE)
		file.store_string(JSON.stringify(payload));file.close()
		scene=load("res://scenes/combat_mission_ui.tscn").instantiate()
		scene.handoff_path=output.path_join("handoff.json")
		root.add_child(scene)
		await create_timer(2.15).timeout
		for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1920,1080),Vector2i(2560,1440)]:
			root.size=dimensions
			await process_frame
			await process_frame
			if scene.has_method("_frame_squad"):scene._frame_squad()
			scene.selected_action="MOVE";scene._sync_display()
			await process_frame
			await RenderingServer.frame_post_draw
			var path := output.path_join("%s-%dx%d%s.png"%[name,dimensions.x,dimensions.y,"-before" if baseline else ""])
			assert(root.get_texture().get_image().save_png(path)==OK)
			if not baseline and scene._battlefield.has_method("uv_to_world"):
				await verify_interactions()
				# Extra close framing verifies the requested larger visible characters.
				scene._camera.zoom=Vector2.ONE*scene._close_zoom()
				var actor: Node2D=scene._unit_tokens["p0"]
				scene._camera.position=actor.position-Vector2(0,scene.size.y*.05/scene._camera.zoom.y)
				await process_frame
				await RenderingServer.frame_post_draw
				root.get_texture().get_image().save_png(output.path_join("%s-%dx%d-close.png"%[name,dimensions.x,dimensions.y]))
		scene.queue_free();await process_frame
	print("COMBAT_21_CAPTURE_PASSED")
	quit()
func verify_interactions() -> void:
	var board=scene._battlefield
	var before := JSON.stringify([scene.player_units,scene.enemy_units,scene.cover_nodes,scene.objective])
	for unit: Dictionary in scene.player_units:
		var cell: Vector2i = scene._cell_position(unit)
		assert(board.world_to_cell(board.cell_to_world(cell))==cell)
		var uv := (Vector2(cell)+Vector2(.5,.5))/Vector2(40,28)
		assert(board.cell_to_world(cell).distance_to(board.uv_to_world(uv))<.01)
	var cursor := Vector2(root.size)*.5
	var point: Vector2 = scene._camera.position+(cursor-Vector2(root.size)*.5)/scene._camera.zoom.x
	scene._zoom_at(cursor,1.3)
	var after: Vector2 = scene._camera.position+(cursor-Vector2(root.size)*.5)/scene._camera.zoom.x
	assert(point.distance_to(after)<.01)
	assert(JSON.stringify([scene.player_units,scene.enemy_units,scene.cover_nodes,scene.objective])==before)
