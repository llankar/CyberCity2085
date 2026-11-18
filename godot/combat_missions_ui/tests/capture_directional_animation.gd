extends SceneTree
var scene
var output: String
var frames: Array[Dictionary]=[]
var token_keys: Array[String]=["p0","e0","p2","p3"]
func _initialize() -> void:call_deferred("run")
func save_frame(name: String) -> void:
	assert(root.get_texture().get_image().save_png(output.path_join(name+".png"))==OK)
func run() -> void:
	var base:=ProjectSettings.globalize_path("res://../..").trim_suffix("/")
	output=base.path_join("work/directional-animation/native")
	var args:=OS.get_cmdline_user_args()
	var roster:= "--roster" in args
	if roster:token_keys.insert(1,"p1")
	for i in range(args.size()-1):
		if args[i]=="--output":output=args[i+1]
	DirAccess.make_dir_recursive_absolute(output);root.size=Vector2i(1920,1080)
	var payload={"asset_base_dir":base,"audio":{"enabled":false},"campaign":{"corp_name":"CYBERCITY 2085"},"mission":{"title":"Animations directionnelles — vérification native","objective_text":"Contrôle des unités","objective_type":"hack","starting_enemy_count":3,"risk_level":3},"map":{"path":"assets/maps/cybercity_inner_02_safehouse.png","environment":"city"},"squad":[{"name":"Rook","role":"samurai","hp":24,"max_hp":24},{"name":"Oracle","role":"psi","hp":20,"max_hp":20}],"support_assets":[{"name":"Mantis","asset_type":"power_armor","hp":40},{"name":"Robot","asset_type":"combat_robot","hp":36}]}
	var file:=FileAccess.open(output.path_join("handoff.json"),FileAccess.WRITE);file.store_string(JSON.stringify(payload));file.close()
	seed(2085);scene=load("res://scenes/combat_mission_ui.tscn").instantiate();scene.handoff_path=output.path_join("handoff.json");root.add_child(scene)
	scene.environment_depth_enabled=true;scene._set_visual_quality(2)
	await create_timer(2.2).timeout;scene._banner.hide()
	scene.player_units[0]["visual_asset"]="agent_diverse_01_neon_blade" if roster else "agent_diverse_04_trench_sniper"
	if roster:scene.player_units[1]["visual_asset"]="agent_diverse_03_magenta_pistol"
	scene.enemy_units[0]["visual_asset"]="enemy_grunt"
	stage_positions();scene._spawn_all_tokens();scene._resize_tokens()
	for key: String in token_keys:assert(scene._unit_tokens[key].atlas!=null,key+" must use real directional resources")
	scene._frame_squad();scene._camera.zoom=Vector2.ONE*minf(scene._close_zoom(),scene._overview_zoom()*1.65);scene._camera.force_update_scroll()
	await process_frame;await RenderingServer.frame_post_draw
	# Matched native before view: only switch these four actors to their existing
	# static fallback; keep the same camera, source textures, map and game data.
	if "--static-only" in args:
		for key: String in token_keys:
			var unit=scene._unit_tokens[key];unit.manifest={};unit.atlas=null;unit._frame_bounds={};unit._recalc_dims();unit.queue_redraw()
		await process_frame;await RenderingServer.frame_post_draw
		save_frame("before-static-1920x1080")
		print("DIRECTIONAL_STATIC_REFERENCE_PASSED");quit();return
	var state:=JSON.stringify([scene.player_units,scene.enemy_units,scene.objective])
	# Deterministic pose demonstration through the real combat renderer. Time is
	# controlled only in this fixture; the real click/movement follows below.
	for key: String in token_keys:scene._unit_tokens[key].set_process(false)
	for direction in range(8):
		for phase in range(4):
			for key: String in token_keys:
				var unit=scene._unit_tokens[key];unit.play_action("move");unit.facing=direction;unit.frame_time=(phase+.1)/8.0;unit._process(0)
			await process_frame;await RenderingServer.frame_post_draw
			save_frame("directions-%02d-%02d"%[direction,phase])
			frames.append({"direction":direction,"phase":phase,"file":"directions-%02d-%02d.png"%[direction,phase]})
	assert(JSON.stringify([scene.player_units,scene.enemy_units,scene.objective])==state)
	for key: String in token_keys:
		var unit=scene._unit_tokens[key];unit.play_action("idle");unit.set_process(true)
	for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1920,1080),Vector2i(2560,1440)]:
		root.size=dimensions;await process_frame;await process_frame;scene._frame_squad();await RenderingServer.frame_post_draw
		save_frame("scene-%dx%d"%[dimensions.x,dimensions.y])
	root.size=Vector2i(1920,1080);await process_frame;scene._frame_squad()
	scene._camera.zoom=Vector2.ONE*minf(scene._close_zoom(),scene._overview_zoom()*1.65);scene._camera.force_update_scroll()
	var report: Dictionary=await capture_movement(0,"movement")
	if roster:report["secondary_movement"]=await capture_movement(1,"movement-secondary")
	report.merge({"directions":frames,"projection":"top_down","coverage":"idle_and_move_only","campaign_written":false})
	var captured_assets: Dictionary={}
	for key: String in token_keys:
		var unit=scene._unit_tokens[key]
		captured_assets[key]={"key":unit.visual_key,"texture_sha256":unit.manifest.texture_sha256}
	report["captured_assets"]=captured_assets
	var proof:=FileAccess.open(output.path_join("animation-report.json"),FileAccess.WRITE);proof.store_string(JSON.stringify(report,"  "));proof.close()
	print("DIRECTIONAL_GAME_CAPTURE_PASSED")
	quit()
func capture_movement(player_index: int,prefix: String) -> Dictionary:
	scene.active_player_index=player_index;scene.selected_action="MOVE";scene._sync_display()
	var board=scene._battlefield;var start: Vector2i=scene._cell_position(scene.player_units[player_index]);var destination:=Vector2i(-1,-1);var expected_cost:=0
	for cell: Vector2i in board.reachable_cells(start,4):
		if scene._is_cell_occupied(cell,player_index,-1):continue
		var route: Array[Vector2i]=board.find_path(start,cell)
		if route.size()>expected_cost+1:destination=cell;expected_cost=route.size()-1
	assert(destination.x>=0 and expected_cost>=2)
	var ap: int=scene.player_units[player_index].ap
	await process_frame
	var event:=InputEventMouseButton.new();event.button_index=MOUSE_BUTTON_LEFT;event.pressed=false;event.position=root.get_canvas_transform()*board.cell_to_world(destination)
	board._unhandled_input(event)
	assert(scene.player_units[player_index].position==destination and scene.player_units[player_index].ap==ap-expected_cost)
	var move_frames: Array[Dictionary]=[];var movement_images: Array[Image]=[];var started:=Time.get_ticks_msec()
	for i in range(40):
		await create_timer(.045).timeout;await RenderingServer.frame_post_draw
		var token=scene._unit_tokens["p%d"%player_index]
		move_frames.append({"file":"%s-%02d.png"%[prefix,i],"elapsed_ms":Time.get_ticks_msec()-started,"clip":token.clip,"frame":token.frame_index,"world_position":[token.position.x,token.position.y]})
		movement_images.append(root.get_texture().get_image())
	await create_timer(2.0).timeout
	for i in range(movement_images.size()):
		assert(movement_images[i].save_png(output.path_join("%s-%02d.png"%[prefix,i]))==OK)
	assert(scene._unit_tokens["p%d"%player_index].position.distance_to(board.cell_to_world(destination))<.1)
	assert(scene._unit_tokens["p%d"%player_index].clip=="idle")
	return {"actual_movement":move_frames,"ap_before":ap,"ap_after":scene.player_units[player_index].ap,"route_cost":expected_cost}
func stage_positions() -> void:
	var arena: Array[Vector2i]=load("res://scripts/map_wall_layout.gd").largest_floor_region(scene._battlefield,Vector2i(18,14))
	var occupied: Array[Vector2i]=[]
	for group: Array in [scene.player_units,scene.enemy_units]:
		for i in range(group.size()):
			var desired:=Vector2i(13+i*3,16) if group==scene.player_units else Vector2i(23+i*2,12)
			var best:=Vector2i(-1,-1);var score:=99999
			for cell: Vector2i in arena:
				var d:=absi(cell.x-desired.x)+absi(cell.y-desired.y)
				if cell not in occupied and d<score:best=cell;score=d
			assert(best.x>=0);group[i]["position"]=best;occupied.append(best)
