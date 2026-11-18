extends SceneTree
var output: String
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var args:=OS.get_cmdline_user_args()
	output=ProjectSettings.globalize_path("user://unified-test")
	var outcome:="victory"
	for i in range(args.size()-1):
		if args[i]=="--output":output=args[i+1]
		elif args[i]=="--outcome":outcome=args[i+1]
	DirAccess.make_dir_recursive_absolute(output)
	var session:={"protocol_version":2,"session_id":"test-session","mission_id":"test-mission","result_path":output.path_join("result.json"),"prepared_path":output.path_join("prepared.json"),"ack_path":output.path_join("ack.json")}
	var dialog=load("res://scripts/mission_results.gd").new();root.add_child(dialog)
	dialog.show_results(outcome,{"session":session,"turn_number":4,"initial_enemy_count":3,"enemies_killed":1,"agents":[{"name":"Vera","hp":7,"max_hp":11}],"support":[]},output)
	await create_timer(.2).timeout
	assert(dialog.visible and FileAccess.file_exists(session.prepared_path))
	assert(dialog.size==Vector2(root.size) and dialog.size.x>0,"result control fills its actual viewport")
	assert(not FileAccess.file_exists(session.result_path),"opening Results cannot release the mission")
	dialog._on_extract()
	assert(FileAccess.file_exists(session.result_path) and dialog._confirmed)
	var result: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(session.result_path))
	assert(result.phase=="confirmed" and result.outcome==outcome and result.agents[0].hp==7)
	assert(not result.has("xp_per_agent") and not result.has("funds_earned"))
	assert(dialog._extract_btn.disabled)
	dialog._publish(session.ack_path,{"protocol_version":2,"session_id":"wrong-session","status":"accepted"})
	await create_timer(.1).timeout
	print("UNIFIED_RESULT_CONFIRMATION_PASSED ",outcome)
	dialog._publish(session.ack_path,{"protocol_version":2,"session_id":"test-session","status":"accepted"})
	await create_timer(2.0).timeout
	push_error("Python acknowledgement did not release the child")
	quit(1)
