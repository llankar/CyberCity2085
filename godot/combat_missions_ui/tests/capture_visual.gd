extends SceneTree
## Captures the real mission scene using a real rendering driver (not --headless).
func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var args := OS.get_cmdline_user_args()
	for i in range(args.size()-1):
		if args[i] == "--capture-size":
			var dimensions := args[i+1].split("x")
			root.size = Vector2i(int(dimensions[0]),int(dimensions[1]))
	var scene := load("res://scenes/combat_mission_ui.tscn").instantiate() as Control
	root.add_child(scene)
	await create_timer(1.5).timeout
	if "--capture-target" in args:
		scene.selected_action = "Rifle Burst"
		scene._sync_display()
	await process_frame
	await RenderingServer.frame_post_draw
	var output := "/workspace/CyberCity2085/work/combat-visual.png"
	for i in range(args.size()-1):
		if args[i] == "--capture": output = args[i+1]
	var err := root.get_texture().get_image().save_png(output)
	print("CAPTURE_SAVED ", output, " ", err)
	scene.queue_free()
	await process_frame
	quit(0 if err == OK else 1)
