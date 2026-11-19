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
	var enemy_target: String = "enemy_commander" if "--enemy-commander" in args else ""
	if "--enemy-sniper" in args:
		enemy_target = "enemy_sniper"
	for i in range(args.size()-1):
		if args[i]=="--enemy-asset":
			enemy_target=args[i+1]
	var map_name:="cybercity_inner_02_safehouse"
	var enemy_theme:=""
	var target_only:= "--target-only" in args
	var roster:= "--roster" in args
	var psi_doctor:= "--psi-doctor" in args
	var street_medic:= "--street-medic" in args
	var longcoat_gunner:= "--longcoat-gunner" in args
	var hooded_infiltrator:= "--hooded-infiltrator" in args
	var holo_hacker:= "--holo-hacker" in args
	var blue_mohawk_scout:= "--blue-mohawk-scout" in args
	var ronin_duelist:= "--ronin-duelist" in args
	var rail_sniper:= "--rail-sniper" in args
	var violet_fixer:= "--violet-fixer" in args
	var silver_pistol:= "--silver-pistol" in args
	var armored_vanguard:= "--armored-vanguard" in args
	var chrome_medic:= "--chrome-medic" in args
	var heavy_breacher:= "--heavy-breacher" in args
	var yellow_strike:= "--yellow-strike" in args
	var red_enforcer:= "--red-enforcer" in args
	var drone_handler:= "--drone-handler" in args
	var cyber_doc:= "--cyber-doc" in args
	var twin_blade:= "--twin-blade" in args
	var veteran_inquisitor:= "--veteran-inquisitor" in args
	var dreadlock_rifle:= "--dreadlock-rifle" in args
	var hooded_psion:= "--hooded-psion" in args
	var redline_runner:= "--redline-runner" in args
	var agent_psi:= "--agent-psi" in args
	var samurai:= "--agent-samurai" in args
	if target_only:
		assert(roster,"--target-only requires --roster")
		token_keys=["p1"]
	elif roster:token_keys.insert(1,"p1")
	for i in range(args.size()-1):
		if args[i]=="--output":output=args[i+1]
		elif args[i]=="--map":map_name=args[i+1]
		elif args[i]=="--enemy-theme":enemy_theme=args[i+1]
	DirAccess.make_dir_recursive_absolute(output);root.size=Vector2i(1920,1080)
	var payload={"asset_base_dir":base,"audio":{"enabled":false},"campaign":{"corp_name":"CYBERCITY 2085"},"mission":{"title":"Animations directionnelles — vérification native","objective_text":"Contrôle des unités","objective_type":"hack","starting_enemy_count":3,"risk_level":3},"map":{"path":"assets/maps/%s.png"%map_name,"environment":"wasteland" if map_name.begins_with("wasteland") else "city"},"squad":[{"name":"Rook","role":"samurai","hp":24,"max_hp":24},{"name":"Oracle","role":"psi","hp":20,"max_hp":20}],"support_assets":[{"name":"Mantis","asset_type":"power_armor","hp":40},{"name":"Robot","asset_type":"combat_robot","hp":36}]}
	if not enemy_theme.is_empty():payload["mission"]["enemy_theme"]=enemy_theme
	var file:=FileAccess.open(output.path_join("handoff.json"),FileAccess.WRITE);file.store_string(JSON.stringify(payload));file.close()
	seed(2085);scene=load("res://scenes/combat_mission_ui.tscn").instantiate();scene.handoff_path=output.path_join("handoff.json");root.add_child(scene)
	scene.environment_depth_enabled=true;scene._set_visual_quality(2)
	await create_timer(2.2).timeout;scene._banner.hide()
	scene.player_units[0]["visual_asset"]="agent_diverse_01_neon_blade" if roster else "agent_diverse_04_trench_sniper"
	if roster:
		scene.player_units[1]["visual_asset"]="agent_diverse_14_armored_vanguard" if armored_vanguard else ("agent_diverse_15_chrome_medic" if chrome_medic else ("agent_diverse_12_violet_fixer" if violet_fixer else ("agent_diverse_13_silver_pistol" if silver_pistol else ("agent_diverse_10_ronin_duelist" if ronin_duelist else ("agent_diverse_11_rail_sniper" if rail_sniper else ("agent_diverse_08_holo_hacker" if holo_hacker else ("agent_diverse_09_blue_mohawk_scout" if blue_mohawk_scout else ("agent_diverse_02_longcoat_gunner" if longcoat_gunner else ("agent_diverse_07_hooded_infiltrator" if hooded_infiltrator else ("agent_diverse_05_psi_doctor" if psi_doctor else ("agent_diverse_06_street_medic" if street_medic else "agent_diverse_03_magenta_pistol")))))))))))
		if heavy_breacher:scene.player_units[1]["visual_asset"]="agent_diverse_16_heavy_breacher"
		elif yellow_strike:scene.player_units[1]["visual_asset"]="agent_diverse_17_yellow_strike"
		elif red_enforcer:scene.player_units[1]["visual_asset"]="agent_diverse_18_red_enforcer"
		elif drone_handler:scene.player_units[1]["visual_asset"]="agent_diverse_19_drone_handler"
		elif cyber_doc:scene.player_units[1]["visual_asset"]="agent_diverse_20_cyber_doc"
		elif twin_blade:scene.player_units[1]["visual_asset"]="agent_diverse_21_twin_blade_adept"
		elif veteran_inquisitor:scene.player_units[1]["visual_asset"]="agent_diverse_22_veteran_inquisitor"
		elif dreadlock_rifle:scene.player_units[1]["visual_asset"]="agent_diverse_23_dreadlock_rifle"
		elif hooded_psion:scene.player_units[1]["visual_asset"]="agent_diverse_24_hooded_psion"
		elif redline_runner:scene.player_units[1]["visual_asset"]="agent_diverse_25_redline_runner"
		elif agent_psi:scene.player_units[1]["visual_asset"]="agent_psi"
		elif samurai:scene.player_units[1]["visual_asset"]="agent_samurai"
	if enemy_theme.is_empty():
		scene.enemy_units[0]["visual_asset"]=enemy_target if not enemy_target.is_empty() else "enemy_grunt"
	elif not enemy_target.is_empty():
		var theme_prefix := "enemy_%s_" % enemy_theme
		assert(enemy_target.begins_with(theme_prefix))
		scene.enemy_units[0]["enemy_subtype"]=enemy_target.trim_prefix(theme_prefix)
	if not enemy_target.is_empty():token_keys=["e0"]
	stage_positions();scene._spawn_all_tokens();scene._resize_tokens()
	for key: String in token_keys:assert(scene._unit_tokens[key].atlas!=null,key+" must use real directional resources")
	scene._frame_squad();scene._camera.zoom=Vector2.ONE*minf(scene._close_zoom(),scene._overview_zoom()*1.65);scene._camera.force_update_scroll()
	await process_frame;await RenderingServer.frame_post_draw
	if not enemy_target.is_empty():
		var enemy=scene._unit_tokens["e0"]
		assert(enemy.visual_key==enemy_target,"capture must exercise the requested enemy atlas")
		enemy.set_process(false)
		for action in ["idle","move","fire","melee","cover","hit","death","psi"]:
			if not enemy.manifest.animations.has(action):continue
			assert(enemy.play_action(action))
			enemy.facing=1
			enemy.frame_time=0.6 if action=="idle" else 0.2
			enemy._process(0)
			await process_frame;await RenderingServer.frame_post_draw
			save_frame(enemy_target+"-"+action)
		print("DIRECTIONAL_TARGET_CAPTURE_PASSED ",enemy_target)
		quit();return
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
	var melee_frames: Array[Dictionary]=[]
	var blade=scene._unit_tokens["p0"]
	for key: String in token_keys:scene._unit_tokens[key].play_action("idle")
	if not target_only:
		for direction in range(8):
			for phase in range(2):
				assert(blade.play_action("melee"));blade.facing=direction;blade.frame_time=(phase+.1)/8.0;blade._process(0)
				await process_frame;await RenderingServer.frame_post_draw
				var melee_file="melee-%02d-%02d"%[direction,phase]
				save_frame(melee_file);melee_frames.append({"direction":direction,"phase":phase,"file":melee_file+".png"})
	var magenta_actions: Array[Dictionary]=[]
	if roster and not psi_doctor and not street_medic and not longcoat_gunner and not hooded_infiltrator and not holo_hacker and not blue_mohawk_scout and not ronin_duelist and not rail_sniper and not violet_fixer and not silver_pistol and not armored_vanguard and not chrome_medic and not heavy_breacher and not yellow_strike and not red_enforcer and not drone_handler and not cyber_doc and not twin_blade and not veteran_inquisitor and not dreadlock_rifle and not hooded_psion and not redline_runner and not agent_psi:
		var magenta=scene._unit_tokens["p1"]
		var actions := ["melee","cover","hit","death"] if samurai else ["fire","melee","cover","hit","death"]
		for action in actions:
			for direction in range(8):
				assert(magenta.play_action(action));magenta.facing=direction;magenta.frame_time=0.2;magenta._process(0)
				await process_frame;await RenderingServer.frame_post_draw
				var action_file="%s-%s-%02d"%["samurai" if samurai else "magenta",action,direction]
				save_frame(action_file);magenta_actions.append({"action":action,"direction":direction,"file":action_file+".png"})
	var psi_actions: Array[Dictionary]=[]
	if psi_doctor:
		var psi_unit=scene._unit_tokens["p1"]
		for action in ["melee","cover","hit","death","psi","heal"]:
			for direction in range(8):
				assert(psi_unit.play_action(action));psi_unit.facing=direction;psi_unit.frame_time=0.2;psi_unit._process(0)
				await process_frame;await RenderingServer.frame_post_draw
				var psi_file="psi-doctor-%s-%02d"%[action,direction]
				save_frame(psi_file);psi_actions.append({"action":action,"direction":direction,"file":psi_file+".png"})
	var medic_actions: Array[Dictionary]=[]
	if street_medic:
		var medic=scene._unit_tokens["p1"]
		for action in ["fire","melee","cover","hit","death","heal"]:
			for direction in range(8):
				assert(medic.play_action(action));medic.facing=direction;medic.frame_time=0.2;medic._process(0)
				await process_frame;await RenderingServer.frame_post_draw
				var medic_file="street-medic-%s-%02d"%[action,direction]
				save_frame(medic_file);medic_actions.append({"action":action,"direction":direction,"file":medic_file+".png"})
	var new_agent_actions: Array[Dictionary]=[]
	if longcoat_gunner or hooded_infiltrator or holo_hacker or blue_mohawk_scout or ronin_duelist or rail_sniper or violet_fixer or silver_pistol or armored_vanguard or chrome_medic or heavy_breacher or yellow_strike or red_enforcer or drone_handler or cyber_doc or twin_blade or veteran_inquisitor or dreadlock_rifle or hooded_psion or redline_runner or agent_psi:
		var new_agent=scene._unit_tokens["p1"]
		var new_prefix="armored-vanguard" if armored_vanguard else ("chrome-medic" if chrome_medic else ("violet-fixer" if violet_fixer else ("silver-pistol" if silver_pistol else ("ronin-duelist" if ronin_duelist else ("rail-sniper" if rail_sniper else ("longcoat-gunner" if longcoat_gunner else ("hooded-infiltrator" if hooded_infiltrator else ("holo-hacker" if holo_hacker else "blue-mohawk-scout"))))))))
		if heavy_breacher:new_prefix="heavy-breacher"
		elif yellow_strike:new_prefix="yellow-strike"
		elif red_enforcer:new_prefix="red-enforcer"
		elif drone_handler:new_prefix="drone-handler"
		elif cyber_doc:new_prefix="cyber-doc"
		elif twin_blade:new_prefix="twin-blade"
		elif veteran_inquisitor:new_prefix="veteran-inquisitor"
		elif dreadlock_rifle:new_prefix="dreadlock-rifle"
		elif hooded_psion:new_prefix="hooded-psion"
		elif redline_runner:new_prefix="redline-runner"
		elif agent_psi:new_prefix="agent-psi"
		var actions=["melee","cover","hit","death","heal"] if chrome_medic or cyber_doc else (["fire","melee","cover","hit","death","psi"] if hooded_psion else (["melee","cover","hit","death","psi"] if drone_handler or agent_psi else (["fire","melee","cover","hit","death"] if longcoat_gunner or blue_mohawk_scout or rail_sniper or violet_fixer or silver_pistol or armored_vanguard or heavy_breacher or yellow_strike or red_enforcer or veteran_inquisitor or dreadlock_rifle or redline_runner else ["melee","cover","hit","death"])))
		for action in actions:
			for direction in range(8):
				assert(new_agent.play_action(action));new_agent.facing=direction;new_agent.frame_time=0.2;new_agent._process(0)
				await process_frame;await RenderingServer.frame_post_draw
				var action_file="%s-%s-%02d"%[new_prefix,action,direction]
				save_frame(action_file);new_agent_actions.append({"action":action,"direction":direction,"file":action_file+".png"})
	if target_only:
		var target=scene._unit_tokens["p1"];target.play_action("idle");target.set_process(true)
		for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1920,1080),Vector2i(2560,1440)]:
			root.size=dimensions;await process_frame;await process_frame;scene._frame_squad();await RenderingServer.frame_post_draw
			save_frame("scene-%dx%d"%[dimensions.x,dimensions.y])
		root.size=Vector2i(1920,1080);await process_frame;scene._frame_squad()
		var movement: Dictionary=await capture_movement(1,"movement-target")
		var target_report={"directions":frames,"new_agent_actions":new_agent_actions,"target_movement":movement,"projection":"top_down","coverage":"single_asset_complete","campaign_written":false,"map":map_name,"captured_assets":{"p1":{"key":target.visual_key,"texture_sha256":target.manifest.texture_sha256}}}
		var target_proof:=FileAccess.open(output.path_join("animation-report.json"),FileAccess.WRITE);target_proof.store_string(JSON.stringify(target_report,"  "));target_proof.close()
		print("DIRECTIONAL_TARGET_CAPTURE_PASSED ",target.visual_key)
		quit();return
	var sniper_actions: Array[Dictionary]=[]
	if not roster:
		var sniper=scene._unit_tokens["p0"]
		for action in ["fire","melee","cover","hit","death"]:
			for direction in range(8):
				assert(sniper.play_action(action));sniper.facing=direction;sniper.frame_time=0.2;sniper._process(0)
				await process_frame;await RenderingServer.frame_post_draw
				var sniper_file="sniper-%s-%02d"%[action,direction]
				save_frame(sniper_file);sniper_actions.append({"action":action,"direction":direction,"file":sniper_file+".png"})
	var grunt_actions: Array[Dictionary]=[]
	var grunt=scene._unit_tokens["e0"]
	for action in ["fire","melee","cover","hit","death"]:
		for direction in range(8):
			assert(grunt.play_action(action));grunt.facing=direction;grunt.frame_time=0.2;grunt._process(0)
			await process_frame;await RenderingServer.frame_post_draw
			var grunt_file="grunt-%s-%02d"%[action,direction]
			save_frame(grunt_file);grunt_actions.append({"action":action,"direction":direction,"file":grunt_file+".png"})
	var heavy_actions: Array[Dictionary]=[]
	for heavy_key: String in ["p2","p3"]:
		var heavy=scene._unit_tokens[heavy_key]
		for action in ["fire","melee","cover","hit","death"]:
			for direction in range(8):
				assert(heavy.play_action(action));heavy.facing=direction;heavy.frame_time=0.2;heavy._process(0)
				await process_frame;await RenderingServer.frame_post_draw
				var heavy_file="%s-%s-%02d"%[heavy.visual_key,action,direction]
				save_frame(heavy_file);heavy_actions.append({"unit":heavy.visual_key,"action":action,"direction":direction,"file":heavy_file+".png"})
	for key: String in token_keys:
		var unit=scene._unit_tokens[key];unit.play_action("idle");unit.set_process(true)
	for dimensions: Vector2i in [Vector2i(1280,720),Vector2i(1920,1080),Vector2i(2560,1440)]:
		root.size=dimensions;await process_frame;await process_frame;scene._frame_squad();await RenderingServer.frame_post_draw
		save_frame("scene-%dx%d"%[dimensions.x,dimensions.y])
	root.size=Vector2i(1920,1080);await process_frame;scene._frame_squad()
	scene._camera.zoom=Vector2.ONE*minf(scene._close_zoom(),scene._overview_zoom()*1.65);scene._camera.force_update_scroll()
	var report: Dictionary=await capture_movement(0,"movement")
	if roster:report["secondary_movement"]=await capture_movement(1,"movement-secondary")
	report.merge({"directions":frames,"melee":melee_frames,"magenta_actions":magenta_actions,"psi_actions":psi_actions,"medic_actions":medic_actions,"new_agent_actions":new_agent_actions,"sniper_actions":sniper_actions,"grunt_actions":grunt_actions,"heavy_actions":heavy_actions,"projection":"top_down","coverage":"complete_authored_fixture_roster","campaign_written":false})
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
