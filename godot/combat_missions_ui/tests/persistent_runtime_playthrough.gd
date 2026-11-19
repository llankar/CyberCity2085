extends SceneTree
## Test harness around the real persistent host, with a legal-action QA player.
var _seen := {}
var captures := ""
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var args:=OS.get_cmdline_user_args()
	for i in range(args.size()-1):
		if args[i]=="--qa-output":captures=args[i+1]
	seed(41)
	var host=root.get_node_or_null("PersistentCombatRuntime")
	if host==null:
		host=load("res://scenes/runtime_host.tscn").instantiate()
		root.add_child(host)
	while true:
		if host._mission!=null and host._mission.battle_started and not _seen.has(host._session_id):
			_seen[host._session_id]=true
			await play(host._mission,host._session_id)
		await create_timer(0.05).timeout

func play(scene,session_id: String) -> void:
	var output:=captures.path_join(session_id)
	DirAccess.make_dir_recursive_absolute(output)
	var agent=preload("res://tests/campaign_agent.gd").new()
	var started:=Time.get_ticks_msec()
	var decisions:=0
	while not scene._audio_released:await create_timer(0.05).timeout
	await capture(output.path_join("combat.png"))
	while is_instance_valid(scene) and not scene.battle_ended and decisions<800 and scene.turn_number<=60:
		if scene.turn_side=="player":
			decisions+=1
			if not agent.act(scene):
				scene._on_action_pressed("END TURN");scene._on_action_pressed("END TURN")
		await create_timer(0.08).timeout
	if not scene.battle_ended:push_error("No natural mission end");quit(2);return
	await create_timer(0.75).timeout
	preload("res://scripts/session_mailbox.gd").publish(output.path_join("playthrough.json"),{
		"session_id":session_id,"pid":OS.get_process_id(),"outcome":scene._results._outcome,
		"outcome_forced":false,"mission_id":scene.handoff.mission.id,"turns":scene.turn_number,
		"moves":agent.moves,"attacks":agent.attacks,"objective_interactions":agent.interactions,
		"objective_completed":scene.objective_completed,"elapsed_seconds":float(Time.get_ticks_msec()-started)/1000,
		"log":scene.combat_log})
	await capture(output.path_join("results.png"))
	while is_instance_valid(scene) and not FileAccess.file_exists(output.path_join("confirm.request")):
		await create_timer(0.05).timeout
	if is_instance_valid(scene):scene._results._extract_btn.pressed.emit()

func capture(path: String) -> void:
	if DisplayServer.get_name()=="headless":return
	await process_frame;await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(path)
