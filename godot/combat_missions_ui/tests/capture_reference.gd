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
	var target_reference := "--target-reference" in OS.get_cmdline_user_args()
	root.size = Vector2i(1672,941) if target_reference else Vector2i(1600,1000)
	var base := ProjectSettings.globalize_path("res://../..")
	DirAccess.make_dir_recursive_absolute(base.path_join("work"))
	var fixture := base.path_join("work/reference-capture-handoff.json")
	var payload := {"asset_base_dir":base,"audio":{"enabled":false},"campaign":{"corp_name":"CYBERCITY"},"mission":{"title":"Marché souterrain","objective_text":"Atteindre le terminal","objective_type":"extract","starting_enemy_count":3,"risk_level":2},"map":{"path":"assets/maps/wasteland_inner_09_underground_market.png","environment":"wasteland","label":"Marché souterrain"},"squad":[{"name":"Rook","role":"sniper","hp":18,"max_hp":24},{"name":"Vera","role":"sniper","hp":24,"max_hp":24},{"name":"Katana","role":"sniper","hp":12,"max_hp":24}]}
	if target_reference:
		payload["map"]["path"] = "assets/maps/city_exterior_neon_market_alley.png"
		payload["map"]["environment"] = "city"
		payload["mission"]["title"] = "Infiltration // secteur 07"
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
		var desired := origin+Vector2i(0,-3) if target_reference and j==0 else origin+Vector2i(7+j,1-j)
		var cell := nearest_in_arena(arena,desired,occupied)
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
	if target_reference:
		await capture_target_reference(scene,base)
		scene.queue_free()
		await process_frame
		quit()
		return
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

func capture_target_reference(scene: Control, base: String) -> void:
	var move_output := base.path_join("work/reference-agents-move.png")
	root.get_texture().get_image().save_png(move_output)
	scene.selected_action = "FIRE"
	scene.selected_target_index = 0
	scene._sync_display()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var hud = scene._hud
	var token = scene._unit_tokens["e0"]
	assert(token.is_targeted,"actual selected enemy is framed")
	assert(token._target_frame_rect().size.x<token._art_rect.size.x+20*token._screen_pixel().x,"frame follows visible body")
	assert(hud.target_anchor_node==token,"card is attached to actual targeted token")
	assert(not hud.target_info.is_empty(),"live target details")
	assert(hud.blocks_map_input(hud.get_global_transform_with_canvas()*hud._target_rect.get_center()),"card must block click-through attacks")
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.position = hud.get_global_transform_with_canvas()*hud._target_rect.get_center()
	hud._input(click)
	assert(root.is_input_handled(),"painted target panel consumes mouse input")
	var original_anchor: Vector2 = hud._target_anchor
	scene._camera.position += Vector2(24,0)
	await process_frame
	await process_frame
	assert(hud._target_anchor.distance_to(original_anchor)>1,"connector follows camera pan")
	scene._camera.position -= Vector2(24,0)
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(base.path_join("work/reference-agents-target.png"))
	for viewport in [Vector2(1280,720),Vector2(1672,941),Vector2(2560,1440)]:
		hud.fit_viewport(viewport)
		for anchor in [Vector2(40,240),Vector2(hud.size.x-40,240),Vector2(hud.size.x*.5,hud._roster_y-30)]:
			var rect: Rect2 = hud._target_panel_rect(anchor)
			assert(rect.position.x>=16 and rect.end.x<=hud.size.x-16,"target card stays in viewport")
			assert(rect.end.y<hud._roster_y,"target card avoids squad and actions")
	print("UNIT_REFERENCE_PRESENTATION_CHECKS_PASSED")
