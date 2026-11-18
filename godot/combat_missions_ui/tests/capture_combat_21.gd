extends SceneTree
## Real-renderer catalogue QA. Fixtures use genuine source maps and wall surveys.
var scene
var catalogue_report: Array[Dictionary]=[]
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var args := OS.get_cmdline_user_args()
	var output := ProjectSettings.globalize_path("res://../../work/combat-21")
	var baseline := "--baseline" in args
	var polish := "--polish" in args
	var art_review := "--art-review" in args
	var selected_map := ""
	var selected_prefix := ""
	var selected_size := Vector2i.ZERO
	var capture_quality := 2
	var candidate_ratio := -1.0
	var scale_comparison := "--scale-comparison" in args
	var intended_depth := "--flat-environment" not in args
	var reference_catalog := ""
	var focus_object := ""
	for i in range(args.size()-1):
		if args[i]=="--output": output=args[i+1]
		elif args[i]=="--map": selected_map=args[i+1]
		elif args[i]=="--prefix":selected_prefix=args[i+1]
		elif args[i]=="--size":
			var pair := args[i+1].split("x")
			selected_size=Vector2i(int(pair[0]),int(pair[1]))
		elif args[i]=="--quality": capture_quality=int(args[i+1])
		elif args[i]=="--human-ratio":candidate_ratio=float(args[i+1])
		elif args[i]=="--reference-catalog":reference_catalog=args[i+1]
		elif args[i]=="--focus-object":focus_object=args[i+1]
	DirAccess.make_dir_recursive_absolute(output)
	# Persist completed maps across an interrupted desktop/environment session.
	# A changed renderer or resource catalogue invalidates old checkpoints.
	var fingerprint_parts: Array[String]=[]
	for directory: String in ["res://scripts","res://shaders","res://art/environment"]:
		for filename: String in DirAccess.get_files_at(directory):
			if filename.get_extension() in ["gd","gdshader","json"]:fingerprint_parts.append(filename+FileAccess.get_sha256(directory.path_join(filename)))
	fingerprint_parts.append(FileAccess.get_sha256("res://art/environment/props25/library.json"))
	if not reference_catalog.is_empty():fingerprint_parts.append(FileAccess.get_sha256(reference_catalog))
	fingerprint_parts.append(str([selected_size,capture_quality,"--entities" in args,art_review,candidate_ratio,scale_comparison]))
	var fingerprint:=str(fingerprint_parts).sha256_text()
	var focus_art: Dictionary=preload("res://scripts/environment_catalog.gd").art_maps().duplicate(true)
	if not reference_catalog.is_empty():
		var reference: Variant=JSON.parse_string(FileAccess.get_file_as_string(reference_catalog))
		assert(reference is Dictionary and reference.get("maps",{}).size()==122)
		# QA-only replay of a committed catalogue. Source files and campaign stay intact.
		var active_art: Dictionary=preload("res://scripts/environment_catalog.gd").art_maps()
		active_art.clear();active_art.merge(reference.maps)
	var completed: Dictionary={}
	if "--resume" in args and FileAccess.file_exists(output.path_join("native-report.json")):
		var previous: Variant=JSON.parse_string(FileAccess.get_file_as_string(output.path_join("native-report.json")))
		if previous is Array:
			for row: Dictionary in previous:
				if row.get("capture_signature","")==fingerprint:
					catalogue_report.append(row);completed[row.map]=true
	var base := ProjectSettings.globalize_path("res://../..")
	var maps := ["city_exterior_neon_market_alley","city_industrial_factory_floor","city_interior_blacksite_lab","wasteland_outdoor_01_dust_road_ambush"]
	if "--depth-catalogue" in args:
		maps=["cybercity_inner_02_safehouse","city_industrial_factory_floor","city_exterior_neon_market_alley","city_interior_blacksite_lab","wasteland_outdoor_01_dust_road_ambush"]
	if "--expansion-details" in args:
		maps=["city_district_civic_center","cybercity_inner_02_safehouse","city_interior_medical_clinic","city_industrial_power_substation","city_interior_police_records"]
	if "--assembly-details" in args:
		maps=["city_industrial_power_substation","city_industrial_data_vault","city_transit_metro_interchange","city_district_holo_square","wasteland_city_11_ruined_transit_plaza"]
	if "--furniture-details" in args:
		maps=["city_interior_safehouse","cybercity_inner_14_detention_block","wasteland_inner_03_ruined_clinic","city_transit_metro_interchange","city_district_holo_square","wasteland_inner_07_apartment_shelter"]
	if "--all-maps" in args:
		maps=[]
		for filename: String in DirAccess.get_files_at(base.path_join("assets/maps")):
			if filename.ends_with(".walls.json"):maps.append(filename.trim_suffix(".walls.json"))
	for name: String in maps:
		if completed.has(name+".png"):continue
		if not selected_map.is_empty() and name!=selected_map: continue
		if not selected_prefix.is_empty() and not name.begins_with(selected_prefix):continue
		var payload := {"asset_base_dir":base,"audio":{"enabled":false},"campaign":{"corp_name":"CYBERCITY 2085"},"mission":{"title":name.replace("_"," "),"objective_text":"Atteindre et sécuriser le terminal","objective_type":"hack","starting_enemy_count":3,"risk_level":3},"map":{"path":"assets/maps/%s.png"%name,"environment":"wasteland" if "wasteland" in name else "city"},"squad":[{"name":"Rook","role":"samurai","hp":24,"max_hp":24,"portrait_path":"assets/ui/portraits/agent_male_01.png"},{"name":"Longshot","role":"sniper","hp":18,"max_hp":24,"portrait_path":"assets/ui/portraits/agent_male_02.png"},{"name":"Oracle","role":"psi","hp":16,"max_hp":20,"portrait_path":"assets/ui/portraits/agent_male_03.png"}]}
		if candidate_ratio>0:payload.map["presentation"]={"human_height_ratio":candidate_ratio}
		if "--entity-showcase" in args:payload.mission["enemy_theme"]="corp_samurai"
		var file := FileAccess.open(output.path_join("handoff.json"),FileAccess.WRITE)
		if "--entities" in args:
			payload["support_assets"]=[{"name":"Mantis","asset_type":"power_armor","hp":40},{"name":"Combat Robot","asset_type":"combat_robot","hp":36}]
		file.store_string(JSON.stringify(payload));file.close()
		var started_usec:=Time.get_ticks_usec()
		seed(2085)
		scene=load("res://scenes/combat_mission_ui.tscn").instantiate()
		scene.handoff_path=output.path_join("handoff.json")
		root.add_child(scene)
		# Other runtime tests toggle persistent preferences. Capture fixtures must
		# choose their own mode instead of sampling another process's setting.
		scene.environment_depth_enabled=intended_depth
		scene._set_visual_quality(capture_quality)
		await create_timer(.05 if art_review else 2.15).timeout
		if art_review:scene._banner.hide() # Inspect scenery after the transient turn announcement.
		assert(scene.environment_depth_enabled==intended_depth)
		if "--entities" in args:
			scene.enemy_units[1]["visual_asset"]="enemy_corp_37_robot_grunt"
			scene.enemy_units[2]["visual_asset"]="enemy_corp_37_power_armor_grunt"
			scene.enemy_units[2]["enemy_theme"]="corp_37_power_armor"
			scene._spawn_all_tokens()
		if polish or art_review: stage_polish_scene()
		for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1920,1080),Vector2i(2560,1440)]:
			if selected_size!=Vector2i.ZERO and dimensions!=selected_size: continue
			root.size=dimensions
			await process_frame
			await process_frame
			if scene.has_method("_frame_squad"):scene._frame_squad()
			if scale_comparison:
				scene._camera.zoom=Vector2.ONE*scene._overview_zoom()*1.65
				scene._camera.position=scene._battlefield.uv_to_world(Vector2(.5,.5))
				scene._camera.force_update_scroll()
			scene.selected_action="MOVE";scene._sync_display()
			if polish or art_review: preview_polish_route()
			if "--prop-focus" in args or "--new-prop-focus" in args or "--assembly-focus" in args or "--furniture-focus" in args:
				var annotations: Array=focus_art.get(name+".png",{}).get("props",[])
				for annotation: Dictionary in annotations:
					if not bool(annotation.enabled):continue
					if not focus_object.is_empty() and annotation.source_object_id!=focus_object:continue
					if "--new-prop-focus" in args and annotation.get("source_review","")!="detail_crop_sheet":continue
					if "--assembly-focus" in args and not annotation.has("assembly"):continue
					if "--furniture-focus" in args and annotation.asset not in ["single_bed","field_cot","transit_bench2","transit_bench4"]:continue
					var b: Array=annotation.bounds_uv
					scene._camera.zoom=Vector2.ONE*minf(scene._close_zoom(),scene._overview_zoom()*2.2)
					scene._camera.position=scene._battlefield.uv_to_world(Vector2((b[0]+b[2])*.5,(b[1]+b[3])*.5))+Vector2(0,scene.size.y*.06/scene._camera.zoom.y)
					scene._camera.force_update_scroll()
					break
			await process_frame
			await RenderingServer.frame_post_draw
			var path := output.path_join("%s-%dx%d%s.png"%[name,dimensions.x,dimensions.y,"-before" if baseline else ""])
			assert(root.get_texture().get_image().save_png(path)==OK)
			if "--entities" in args and not scene.vehicle_units.is_empty():
				var original_position: Vector2=scene._camera.position
				var original_zoom: Vector2=scene._camera.zoom
				for vehicle_index in range(scene.vehicle_units.size()):
					var vehicle=scene._unit_tokens["v%d"%vehicle_index]
					scene._camera.zoom=Vector2.ONE*minf(scene._close_zoom(),dimensions.y*.38/vehicle._body_height())
					scene._camera.position=vehicle.position-Vector2(0,vehicle._body_height()*.4)
					scene._camera.force_update_scroll()
					await process_frame
					await RenderingServer.frame_post_draw
					var suffix: String="vehicle" if vehicle_index==0 else "vehicle-%d"%vehicle_index
					assert(root.get_texture().get_image().save_png(output.path_join("%s-%dx%d-%s.png"%[name,dimensions.x,dimensions.y,suffix]))==OK)
				scene._camera.position=original_position;scene._camera.zoom=original_zoom
				scene._camera.force_update_scroll()
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
			if art_review:
				await verify_interactions()
			if "--entities" in args:
				for token in scene._unit_tokens.values():
					assert(token._art_sprite.visible and token._cast_shadow.visible)
					assert(token._cast_shadow.texture==token._art_sprite.texture)
					assert(token._cast_shadow.region_rect==token._art_sprite.region_rect)
					assert(token._art_sprite.scale.x==token._art_sprite.scale.y,"source aspect is preserved")
					assert(token.modulate.a==1.0,"no ghost opacity")
					if token.unit_id<1000:
						assert(token.hit_test_screen(token.get_global_transform_with_canvas()*token._visible_body_rect().get_center()),"all combat entity families retain picking")
			if not baseline and not polish and not art_review and scene._battlefield.has_method("uv_to_world"):
				await verify_interactions()
				# Extra close framing verifies the requested larger visible characters.
				scene._camera.zoom=Vector2.ONE*scene._close_zoom()
				var actor: Node2D=scene._unit_tokens["p0"]
				scene._camera.position=actor.position-Vector2(0,scene.size.y*.05/scene._camera.zoom.y)
				await process_frame
				await RenderingServer.frame_post_draw
				root.get_texture().get_image().save_png(output.path_join("%s-%dx%d-close.png"%[name,dimensions.x,dimensions.y]))
		var active_sprites:=0
		var completion_patches:=0
		for prop in scene._visual_obstacles:
			if not prop._sprite.is_empty():
				active_sprites+=1
				completion_patches+=prop.floor.get("patches",[]).size()
		if art_review and scene.environment_depth_enabled and scene._battlefield.top_down:
			var expected: int=preload("res://scripts/environment_catalog.gd").art_walls("assets/maps/"+name+".png").size()
			assert(active_sprites==expected,"every annotated resource must actually render")
			var expected_patches:=0
			for annotation: Dictionary in preload("res://scripts/environment_catalog.gd").art_maps().get(name+".png",{}).get("props",[]):
				if bool(annotation.enabled):expected_patches+=1+annotation.get("erase_overhang_uv",[]).size()
			assert(completion_patches==expected_patches,"authored overhang masks must be rendered with their object")
		catalogue_report.append({"human_ratio_requested":candidate_ratio,"human_ratio_applied":scene._battlefield.human_height_ratio,"scale_comparison_only":scale_comparison,"scale_calibration_status":"NOT VERIFIED","map":name+".png","elapsed_ms":(Time.get_ticks_usec()-started_usec)/1000.0,"static_memory_bytes":OS.get_static_memory_usage(),"props":scene._visual_obstacles.size(),"rendered_sprites":active_sprites,"projection":"top_down" if scene._battlefield.top_down else "isometric","native_render":true,"projection_and_zoom_checked":polish or art_review,"capture_signature":fingerprint,"entity_families_checked":"--entities" in args,"vehicle_count":scene.vehicle_units.size()})
		var report:=FileAccess.open(output.path_join("native-report.json"),FileAccess.WRITE)
		report.store_string(JSON.stringify(catalogue_report,"  "));report.close()
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
			var desired: Vector2i
			if group==scene.player_units:desired=desired_players[index] if index<3 else Vector2i(10+(index-3)*9,20)
			else:desired=desired_enemies[index%3]
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
