extends SceneTree
## Integration fixture: real scene and movement; forced outcome tests return plumbing.
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var args:=OS.get_cmdline_user_args()
	var confirm_path:=""
	var capture_dir:=""
	var outcome:="victory"
	var scene=load("res://scenes/combat_mission_ui.tscn").instantiate()
	for i in range(args.size()-1):
		if args[i]=="--handoff":scene.handoff_path=args[i+1]
		elif args[i]=="--qa-confirm":confirm_path=args[i+1]
		elif args[i]=="--qa-captures":capture_dir=args[i+1]
		elif args[i]=="--qa-outcome":outcome=args[i+1]
	root.add_child(scene)
	if scene.handoff.get("session", {}).has("audio_path"):
		assert(not scene._audio._music_owned)
		for attempt in range(100):
			if scene._audio_released: break
			await create_timer(0.1).timeout
		assert(scene._audio_released and scene._audio._music_owned)
		print("UNIFIED_AUDIO_OWNERSHIP_READY")
	await create_timer(2.2).timeout
	assert(scene.battle_started)
	var original: Vector2i=scene._cell_position(scene.player_units[0])
	var moved:=false
	for cell: Vector2i in scene._battlefield.reachable_cells(original,1):
		if cell==original or scene._is_cell_occupied(cell,0,-1):continue
		var ap: int=scene.player_units[0].ap
		scene._move_active_unit_to(cell)
		assert(scene._cell_position(scene.player_units[0])==cell and scene.player_units[0].ap==ap-1)
		moved=true;break
	assert(moved)
	await create_timer(.6).timeout
	if outcome=="defeat":
		for unit: Dictionary in scene.player_units:unit.hp=0
	scene.objective_completed=outcome=="victory"
	scene._end_combat(outcome)
	await create_timer(.75).timeout
	print("UNIFIED_RESULTS_SIZE ",scene._results.size)
	var session: Dictionary=scene.handoff.session
	assert(FileAccess.file_exists(session.prepared_path))
	assert(not FileAccess.file_exists(session.result_path))
	if not capture_dir.is_empty():
		DirAccess.make_dir_recursive_absolute(capture_dir)
		await process_frame;await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png(capture_dir.path_join("godot-results.png"))==OK)
	print("UNIFIED_NATIVE_RESULTS_WAITING")
	while not FileAccess.file_exists(confirm_path):await create_timer(.05).timeout
	assert(not FileAccess.file_exists(session.result_path),"no return until confirmation")
	# Exercise the actual button signal, not a fabricated result file.
	scene._results._extract_btn.pressed.emit()
	assert(FileAccess.file_exists(session.result_path))
	print("UNIFIED_NATIVE_RESULT_CONFIRMED")
