extends SceneTree
## Real-renderer catalogue QA. Fixtures use genuine source maps and wall surveys.
var scene
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var args := OS.get_cmdline_user_args()
	var output := ProjectSettings.globalize_path("res://../../work/combat-21")
	var baseline := "--baseline" in args
	var polish := "--polish" in args
	var selected_map := ""
	var selected_size := Vector2i.ZERO
	var capture_quality := 2
	for i in range(args.size()-1):
		if args[i]=="--output": output=args[i+1]
		elif args[i]=="--map": selected_map=args[i+1]
		elif args[i]=="--size":
			var pair := args[i+1].split("x")
			selected_size=Vector2i(int(pair[0]),int(pair[1]))
		elif args[i]=="--quality": capture_quality=int(args[i+1])
	DirAccess.make_dir_recursive_absolute(output)
	var base := ProjectSettings.globalize_path("res://../..")
	var maps := ["city_exterior_neon_market_alley","city_industrial_factory_floor","city_interior_blacksite_lab","wasteland_outdoor_01_dust_road_ambush"]
	if "--depth-catalogue" in args:
		maps=["cybercity_inner_02_safehouse","city_industrial_factory_floor","city_exterior_neon_market_alley","city_interior_blacksite_lab","wasteland_outdoor_01_dust_road_ambush"]
	for name: String in maps:
		if not selected_map.is_empty() and name!=selected_map: continue
		var payload := {"asset_base_dir":base,"audio":{"enabled":false},"campaign":{"corp_name":"CYBERCITY 2085"},"mission":{"title":name.replace("_"," "),"objective_text":"Atteindre et sécuriser le terminal","objective_type":"hack","starting_enemy_count":3,"risk_level":3},"map":{"path":"assets/maps/%s.png"%name,"environment":"wasteland" if "wasteland" in name else "city"},"squad":[{"name":"Rook","role":"samurai","hp":24,"max_hp":24,"portrait_path":"assets/ui/portraits/agent_male_01.png"},{"name":"Longshot","role":"sniper","hp":18,"max_hp":24,"portrait_path":"assets/ui/portraits/agent_male_02.png"},{"name":"Oracle","role":"psi","hp":16,"max_hp":20,"portrait_path":"assets/ui/portraits/agent_male_03.png"}]}
		var file := FileAccess.open(output.path_join("handoff.json"),FileAccess.WRITE)
		file.store_string(JSON.stringify(payload));file.close()
		seed(2085)
		scene=load("res://scenes/combat_mission_ui.tscn").instantiate()
		scene.handoff_path=output.path_join("handoff.json")
		root.add_child(scene)
		scene._set_visual_quality(capture_quality)
		await create_timer(2.15).timeout
		if polish: stage_polish_scene()
		for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1920,1080),Vector2i(2560,1440)]:
			if selected_size!=Vector2i.ZERO and dimensions!=selected_size: continue
			root.size=dimensions
			await process_frame
			await process_frame
			if scene.has_method("_frame_squad"):scene._frame_squad()
			scene.selected_action="MOVE";scene._sync_display()
			if polish: preview_polish_route()
			await process_frame
			await RenderingServer.frame_post_draw
			var path := output.path_join("%s-%dx%d%s.png"%[name,dimensions.x,dimensions.y,"-before" if baseline else ""])
			assert(root.get_texture().get_image().save_png(path)==OK)
			if "--wall-overlay" in args:
				scene._battlefield.debug_walls_visible=true
				scene._battlefield.queue_redraw()
				await process_frame
				await RenderingServer.frame_post_draw
				assert(root.get_texture().get_image().save_png(output.path_join("%s-%dx%d-walls.png"%[name,dimensions.x,dimensions.y]))==OK)
				scene._battlefield.debug_walls_visible=false
				scene._battlefield.queue_redraw()
			if polish:
				await capture_polish_target(output,"%s-%dx%d"%[name,dimensions.x,dimensions.y])
			if not baseline and not polish and scene._battlefield.has_method("uv_to_world"):
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

func stage_polish_scene() -> void:
	# Only QA fixture positions change; source maps and real collisions remain intact.
	var layout = load("res://scripts/map_wall_layout.gd")
	var arena: Array[Vector2i] = layout.largest_floor_region(scene._battlefield,Vector2i(18,14))
	var occupied: Array[Vector2i] = []
	for group: Array in [scene.player_units,scene.enemy_units]:
		for index in range(group.size()):
			var desired_players := [Vector2i(16,14),Vector2i(12,16),Vector2i(16,18)]
			var desired_enemies := [Vector2i(20,13),Vector2i(22,15),Vector2i(22,18)]
			var desired: Vector2i = desired_players[index%3] if group==scene.player_units else desired_enemies[index%3]
			var best := Vector2i(-1,-1)
			var distance := 99999
			for cell: Vector2i in arena:
				var d := absi(cell.x-desired.x)+absi(cell.y-desired.y)
				if d<distance and cell not in occupied:
					best=cell;distance=d
			group[index]["position"]=best
			occupied.append(best)
	# Put the selected contact on a genuine open firing lane for target-card QA.
	var origin: Vector2i = scene._cell_position(scene.player_units[0])
	var preferred: Vector2 = scene._battlefield.cell_to_world(origin)+Vector2(scene._battlefield.iso_tw*3,0)
	var target_cell: Vector2i = scene._cell_position(scene.enemy_units[0])
	var best_score := INF
	for cell: Vector2i in arena:
		var distance := absi(cell.x-origin.x)+absi(cell.y-origin.y)
		if cell in occupied or distance<3 or distance>6: continue
		if not scene._battlefield.has_los(origin,cell): continue
		var score: float = scene._battlefield.cell_to_world(cell).distance_to(preferred)
		if score<best_score:
			target_cell=cell;best_score=score
	scene.enemy_units[0]["position"]=target_cell
	scene._resize_tokens()

func preview_polish_route() -> void:
	var board = scene._battlefield
	var origin: Vector2i = scene._cell_position(scene.player_units[0])
	var best := origin
	var distance := 0.0
	for cell: Vector2i in board.reachable_cells(origin,4):
		if scene._is_cell_occupied(cell,0,-1): continue
		var route: Array[Vector2i] = board.find_path(origin,cell)
		var score: float = board.cell_to_world(cell).x-board.cell_to_world(origin).x
		if route.size()==5 and score>distance:
			best=cell;distance=score
	board.hovered_cell=best
	scene._visual_cell_hovered(best)
	if best!=origin: assert(board._route_preview_geometry().cost==4)

func capture_polish_target(output: String, label: String) -> void:
	await verify_interactions()
	scene._frame_squad()
	scene.selected_action="Rifle Burst"
	scene.selected_target_index=0
	scene._sync_display()
	var actor: Node2D=scene._unit_tokens["p0"]
	var enemy: Node2D=scene._unit_tokens["e0"]
	# Simulate a player pan for the detail capture; zoom and projection stay exact.
	scene._camera.position=(actor.position+enemy.position)*.5+Vector2(0,scene.size.y*.07/scene._camera.zoom.y)
	var effect=scene._visual_fx
	effect.burst("plasma",actor.position-Vector2(0,actor._sh*.55),enemy.position-Vector2(0,enemy._sh*.5))
	effect.burst("heal",actor.position,actor.position)
	effect._process(.24)
	effect.set_process(false)
	await process_frame
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(output.path_join(label+"-target-fx.png"))==OK)
	effect.effects.clear()
	effect.queue_redraw()
	if label=="city_industrial_factory_floor-1920x1080" and "--effects-showcase" in OS.get_cmdline_user_args():
		for kind in ["fire","impact","explosion","heal","psi","melee"]:
			effect.effects.clear()
			effect.burst(kind,actor.position-Vector2(0,actor._sh*.55),enemy.position-Vector2(0,enemy._sh*.5))
			effect._process(.26)
			effect.set_process(false)
			await process_frame
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png(output.path_join(label+"-"+kind+".png"))
		effect.effects.clear()
		effect.queue_redraw()
