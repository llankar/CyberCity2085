extends SceneTree
## Matched before/after camera and combat state on real maps, using the real view.
func _initialize() -> void: call_deferred("run")
func run() -> void:
	root.size=Vector2i(1920,1080)
	var base:=ProjectSettings.globalize_path("res://../..")
	var output:=base.path_join("work/combat-23-detail")
	DirAccess.make_dir_recursive_absolute(output)
	var fixture:=output.path_join("handoff.json")
	var file:=FileAccess.open(fixture,FileAccess.WRITE)
	file.store_string(JSON.stringify({"asset_base_dir":base,"audio":{"enabled":false},"map":{"path":"assets/maps/cybercity_inner_02_safehouse.png","environment":"city"},"mission":{"title":"Archives du clan — contrôle des volumes","objective_text":"Inspecter la zone centrale","risk_level":3,"objective_type":"hack"},"squad":[{"name":"Rook","role":"samurai","hp":24,"max_hp":24,"portrait_path":"assets/ui/portraits/agent_male_01.png"},{"name":"Oracle","role":"psi","hp":20,"max_hp":20,"portrait_path":"assets/ui/portraits/agent_male_03.png"}]}));file.close()
	seed(2085)
	var scene=load("res://scenes/combat_mission_ui.tscn").instantiate()
	scene.handoff_path=fixture
	root.add_child(scene)
	scene._set_visual_quality(2)
	await create_timer(2.1).timeout
	var board=scene._battlefield
	var arena: Array[Vector2i]=load("res://scripts/map_wall_layout.gd").largest_floor_region(board,Vector2i(19,18))
	var occupied: Array[Vector2i]=[]
	for group: Array in [scene.player_units,scene.enemy_units]:
		for index in range(group.size()):
			var desired:=Vector2i(12+index*6,22) if group==scene.player_units else Vector2i(29,8+index*4)
			var nearest:=arena[0]
			var score:=99999
			for cell: Vector2i in arena:
				var distance:=absi(cell.x-desired.x)+absi(cell.y-desired.y)
				if cell not in occupied and distance<score:nearest=cell;score=distance
			group[index]["position"]=nearest
			occupied.append(nearest)
	scene._resize_tokens()
	scene._camera.zoom=Vector2.ONE*scene._overview_zoom()
	scene._camera.position=board.uv_to_world(Vector2(.47,.51))+Vector2(0,45/scene._camera.zoom.y)
	scene.selected_action="Defend"
	scene._sync_display()
	var state:=JSON.stringify([scene.player_units,scene.enemy_units,scene.objective,scene.cover_nodes])
	var camera: Transform2D=scene._camera.transform
	for enabled in [false,true]:
		scene.environment_depth_enabled=enabled
		scene._build_visual_obstacles()
		scene._update_visual_context()
		await create_timer(.45).timeout
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png(output.path_join("furniture-%s.png"%("after" if enabled else "before")))==OK)
		assert(JSON.stringify([scene.player_units,scene.enemy_units,scene.objective,scene.cover_nodes])==state)
		assert(scene._camera.transform==camera,"depth toggle never reframes the camera")
	# Exercise the real keyboard route, not just a render-only field assignment.
	for expected in [false,true]:
		var event := InputEventKey.new()
		event.keycode=KEY_F10;event.pressed=true
		Input.parse_input_event(event)
		await process_frame
		event.pressed=false;Input.parse_input_event(event)
		await process_frame
		assert(scene.environment_depth_enabled==expected,"F10 switches the actual view")
		assert(JSON.stringify([scene.player_units,scene.enemy_units,scene.objective,scene.cover_nodes])==state)
		assert(scene._camera.transform==camera)
	for level in [0,1,2]:
		scene._set_visual_quality(level)
		var raised:=0
		for prop: Node2D in scene._visual_obstacles:
			if prop.height>0:raised+=1
		assert(raised==0 if level==0 else raised>0,"low quality bypasses volume construction; other tiers restore it")
		assert(JSON.stringify([scene.player_units,scene.enemy_units,scene.objective,scene.cover_nodes])==state)
		assert(scene._camera.transform==camera)
	scene.queue_free();await process_frame
	print("DEPTH_COMPARISON_CAPTURE_PASSED")
	quit()
