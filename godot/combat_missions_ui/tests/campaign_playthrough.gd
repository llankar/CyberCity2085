extends SceneTree
## QA player: only selects legal actions. Never assigns HP/AP/positions/objective/outcome.
var decisions := 0
var moves := 0
var attacks := 0
var interactions := 0
var started_ms := 0
var policy := "objective"
var agent = preload("res://tests/campaign_agent.gd").new()

func _initialize() -> void: call_deferred("run")

func run() -> void:
	var args := OS.get_cmdline_user_args()
	var confirm_path := ""
	var captures := ""
	var scene = load("res://scenes/combat_mission_ui.tscn").instantiate()
	for i in range(args.size()-1):
		if args[i] == "--handoff": scene.handoff_path = args[i+1]
		elif args[i] == "--qa-confirm": confirm_path = args[i+1]
		elif args[i] == "--qa-captures": captures = args[i+1]
		elif args[i] == "--qa-outcome": policy = "passive" if args[i+1] == "defeat" else "objective"
	seed(41) # Reproducible QA seed; hit rolls and production probabilities are untouched.
	started_ms = Time.get_ticks_msec()
	root.add_child(scene)
	for attempt in range(200):
		if scene.battle_started: break
		await process_frame
	if not scene.battle_started: fail("Combat did not start"); return
	print("UNIFIED_PLAYTHROUGH_STARTED")
	while not scene._audio_released:
		await create_timer(0.05).timeout
	print("UNIFIED_AUDIO_OWNERSHIP_READY")
	await create_timer(0.3).timeout
	await capture(captures.path_join("godot-combat-start.png"))
	agent.policy=policy
	while not scene.battle_ended and decisions < 800 and scene.turn_number <= 60:
		if scene.turn_side == "player":
			decisions += 1
			if not agent.act(scene):
				scene._on_action_pressed("END TURN")
				scene._on_action_pressed("END TURN")
		await create_timer(0.08).timeout
	if not scene.battle_ended: fail("No natural terminal condition within the QA budget"); return
	await create_timer(0.75).timeout
	var report := {"outcome_forced": false, "policy": policy, "seed": 41,
		"mission_id": scene.handoff.mission.id, "outcome": scene._results._outcome,
		"turns": scene.turn_number, "player_decisions": decisions, "moves": agent.moves,
		"attacks": agent.attacks, "objective_interactions": agent.interactions,
		"objective_completed": scene.objective_completed,
		"elapsed_seconds": float(Time.get_ticks_msec()-started_ms)/1000.0,
		"log": scene.combat_log}
	preload("res://scripts/session_mailbox.gd").publish(captures.path_join("playthrough.json"), report)
	await capture(captures.path_join("godot-results.png"))
	print("UNIFIED_NATIVE_RESULTS_WAITING")
	while not FileAccess.file_exists(confirm_path): await create_timer(0.05).timeout
	scene._results._extract_btn.pressed.emit()
	print("UNIFIED_NATIVE_RESULT_CONFIRMED")


func capture(path: String) -> void:
	if DisplayServer.get_name()=="headless": return
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(path)

func fail(message: String) -> void:
	push_error(message)
	quit(2)
