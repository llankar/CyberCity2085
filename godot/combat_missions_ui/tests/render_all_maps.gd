extends SceneTree
## Real OpenGL draw pass for every surveyed map, plus representative captures.
func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var scene = load("res://scenes/combat_mission_ui.tscn").instantiate()
	root.add_child(scene)
	await process_frame
	await process_frame
	var layout = load("res://scripts/map_wall_layout.gd")
	var count := 0
	var started := Time.get_ticks_msec()
	for filename: String in DirAccess.get_files_at(scene.project_root.path_join("assets/maps")):
		if not filename.ends_with(".walls.json"): continue
		var path: String = scene.project_root.path_join("assets/maps").path_join(filename)
		var geometry: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
		var tex = scene._load_tex("assets/maps/"+str(geometry["image"]))
		if tex == null:
			push_error("Missing map texture: "+filename)
			quit(1)
			return
		scene.map_texture = tex
		scene.cover_nodes = layout.cover_nodes(geometry)
		scene.handoff["map"]["path"] = "assets/maps/"+str(geometry["image"])
		scene._battlefield.configure(Vector2(5120,2880),tex,scene.cover_nodes,Vector2i(20,14))
		scene._build_visual_obstacles()
		scene._camera.position = scene._battlefield.cell_to_world(Vector2i(20,14))
		scene._camera.zoom = Vector2.ONE*0.24
		await process_frame
		await RenderingServer.frame_post_draw
		count += 1
		if filename in ["city_exterior_neon_market_alley.walls.json","city_interior_research_lab.walls.json","wasteland_outdoor_01_dust_road_ambush.walls.json"]:
			var output: String = scene.project_root.path_join("work/"+filename.replace(".walls.json","-render.png"))
			root.get_texture().get_image().save_png(output)
	print("ALL_MAPS_RENDERED: ",count," real OpenGL frames; elapsed_ms=",Time.get_ticks_msec()-started)
	scene.queue_free()
	await process_frame
	quit()
