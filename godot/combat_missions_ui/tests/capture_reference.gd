extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func nearest_in_arena(arena: Array[Vector2i], desired: Vector2i, occupied: Array[Vector2i]) -> Vector2i:
	var best := Vector2i(-1,-1)
	var distance := 999999
	for cell in arena:
		var d := absi(cell.x-desired.x)+absi(cell.y-desired.y)
		if d < distance and not occupied.has(cell):
			best = cell
			distance = d
	return best

func run() -> void:
	root.size = Vector2i(1600,1000)
	var base := ProjectSettings.globalize_path("res://../..")
	DirAccess.make_dir_recursive_absolute(base.path_join("work"))
	var fixture := base.path_join("work/reference-capture-handoff.json")
	var payload := {"asset_base_dir":base,"audio":{"enabled":false},"campaign":{"corp_name":"CYBERCITY"},"mission":{"title":"Marché souterrain","objective_text":"Atteindre le terminal","objective_type":"extract","starting_enemy_count":3,"risk_level":2},"map":{"path":"assets/maps/wasteland_inner_09_underground_market.png","environment":"wasteland","label":"Marché souterrain"},"squad":[{"name":"Rook","role":"sniper","hp":18,"max_hp":24},{"name":"Vera","role":"sniper","hp":24,"max_hp":24},{"name":"Katana","role":"sniper","hp":12,"max_hp":24}]}
	var file := FileAccess.open(fixture,FileAccess.WRITE)
	file.store_string(JSON.stringify(payload))
	file.close()
	var scene = load("res://scenes/combat_mission_ui.tscn").instantiate()
	scene.handoff_path = fixture
	root.add_child(scene)
	await create_timer(1.0).timeout
	var board = scene._battlefield
	var layout = load("res://scripts/map_wall_layout.gd")
	var arena: Array[Vector2i] = layout.largest_floor_region(board,Vector2i(15,12))
	var occupied: Array[Vector2i] = []
	var origin := nearest_in_arena(arena,Vector2i(15,12),occupied)
	occupied.append(origin)
	scene.player_units[0]["position"] = origin
	scene.player_units[0]["ap"] = 4
	var i := 1
	for desired in [origin+Vector2i(-3,1),origin+Vector2i(0,4)]:
		var cell := nearest_in_arena(arena,desired,occupied)
		scene.player_units[i]["position"] = cell
		occupied.append(cell)
		i += 1
	for j in range(scene.enemy_units.size()):
		var cell := nearest_in_arena(arena,origin+Vector2i(7+j,1-j),occupied)
		scene.enemy_units[j]["position"] = cell
		scene.enemy_units[j]["hp"] = 18
		scene.enemy_units[j]["max_hp"] = 24
		occupied.append(cell)
	scene._resize_tokens()
	scene._camera.zoom = Vector2.ONE*scene._overview_zoom()
	scene._camera.position = board.cell_to_world(origin)+Vector2(150,-60)
	scene.selected_action = "MOVE"
	scene._sync_display()
	var target := origin
	var score := -999999.0
	for cell in board.reachable_cells(origin,4):
		var route: Array[Vector2i] = board.find_path(origin,cell)
		var candidate: float = board.cell_to_world(cell).x-board.cell_to_world(origin).x
		if route.size()==5 and candidate>score:
			target = cell
			score = candidate
	board.hovered_cell = target
	scene._visual_cell_hovered(target)
	await process_frame
	await RenderingServer.frame_post_draw
	var output := ProjectSettings.globalize_path("res://../../work/reference-ui.png")
	var error := root.get_texture().get_image().save_png(output)
	print("REFERENCE_CAPTURE_SAVED ",output," ",error)
	assert(board.cell_to_world(target).x>board.cell_to_world(origin).x,"actual rightward destination")
	scene._on_cell_clicked(target)
	assert(scene.player_units[0]["position"]==target,"real movement escapes market spawn area")
	assert(scene.player_units[0]["ap"]==0,"real preview cost deducted")
	await create_timer(0.8).timeout
	assert(scene._unit_tokens["p0"].position.distance_to(board.cell_to_world(target))<0.1,"rendered agent reaches destination")
	print("MARKET_RIGHTWARD_MOVE_PASSED")
	scene.queue_free()
	await process_frame
	quit(error)
