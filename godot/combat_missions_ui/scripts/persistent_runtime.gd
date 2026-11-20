extends Node
## Application-lifetime host. Missions are scene instances, not new OS processes.
const Mailbox = preload("res://scripts/session_mailbox.gd")
const PARKED_LEASE_SECONDS := 10.0
const ACTIVE_LEASE_SECONDS := 120.0
var directory := ""
var runtime_id := ""
var asset_root := ""
var _warming := true
var owner_pid := 0
var _packed: PackedScene
var _mission: Node = null
var _busy := false
var _parking := false
var _clock := 0.0
var _last_command := ""
var _heartbeat: Variant = null
var _lease_age := 0.0
var _session_id := ""
var _pending_status: Dictionary = {}

func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	for i in range(args.size()-1):
		if args[i]=="--runtime-dir": directory=args[i+1]
		elif args[i]=="--runtime-id": runtime_id=args[i+1]
		elif args[i]=="--owner-pid": owner_pid=int(args[i+1])
		elif args[i]=="--asset-root": asset_root=args[i+1]
	if directory.is_empty() or runtime_id.is_empty(): get_tree().quit(2); return
	get_tree().root.title="CyberCity 2085"
	_park_window()
	_publish("booting")
	_packed=load("res://scenes/combat_mission_ui.tscn") as PackedScene
	if _packed==null: _publish("error","Mission scene unavailable"); return
	var units:=asset_root.path_join("assets/units")
	var warmed:=0
	for file in DirAccess.get_files_at(units):
		if (file.begins_with("agent_diverse_") or file in ["agent_samurai_512.png","agent_psi_512.png","robot_combat_512.png"]) and file.ends_with("_512.png"):
			preload("res://scripts/runtime_texture_cache.gd").load_texture(units.path_join(file))
			warmed+=1
			if warmed%4==0:await get_tree().process_frame
	_warming=false
	_publish("idle")

func _process(delta: float) -> void:
	_clock+=delta
	_lease_age+=delta
	if _clock<0.1:return
	_clock=0.0
	_flush_status()
	var heartbeat: Variant=_read("heartbeat.json")
	if heartbeat is Dictionary and heartbeat.get("runtime_id")==runtime_id and heartbeat.get("sequence")!=_heartbeat:
		_heartbeat=heartbeat.get("sequence");_lease_age=0
	var lease_limit := PARKED_LEASE_SECONDS if _mission == null and not _busy else ACTIVE_LEASE_SECONDS
	if _lease_age > lease_limit:
		get_tree().quit()
		return
	if _busy or _warming or _packed==null:return
	var command: Variant=_read("command.json")
	if not command is Dictionary or command.get("protocol_version")!=2 or command.get("runtime_id")!=runtime_id:return
	var id:=str(command.get("command_id",""))
	if id.is_empty() or id==_last_command:return
	_last_command=id
	match str(command.get("event","")):
		"mission": _load_mission(command)
		"park":
			if str(command.get("session_id",""))==_session_id: finish_mission(_mission)
		"shutdown": get_tree().quit()

func _load_mission(command: Dictionary) -> void:
	_busy=true
	if _mission!=null:
		await _dispose_mission()
	_session_id=str(command.get("session_id",""))
	_publish("loading")
	var viewport: Variant=command.get("viewport")
	if viewport is Array and viewport.size()==2 and viewport[0]>0 and viewport[1]>0:
		get_tree().root.size=Vector2i(int(viewport[0]),int(viewport[1]))
	_mission=_packed.instantiate()
	_mission.handoff_path=str(command.get("handoff_path",""))
	add_child(_mission)
	for attempt in range(120):
		if _mission.battle_started or not _mission._recovery_error.is_empty():break
		await get_tree().process_frame
	if not _mission.battle_started:
		_publish("error","Mission initialization refused");_busy=false;return
	if DisplayServer.get_name()!="headless":
		DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_NO_FOCUS,false)
	if DisplayServer.get_name()!="headless" and OS.get_name()!="Windows":
		var position: Variant=command.get("position")
		if position is Array and position.size()==2:get_tree().root.position=Vector2i(int(position[0]),int(position[1]))
		DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_NO_FOCUS,false)
		DisplayServer.window_move_to_foreground()
	_publish("busy")
	_busy=false

func finish_mission(scene: Node) -> void:
	if _parking or (scene!=null and scene!=_mission):return
	_parking=true
	call_deferred("_park")

func _park() -> void:
	_busy=true
	_park_window()
	await _dispose_mission()
	_publish("idle")
	_busy=false;_parking=false

func _dispose_mission() -> void:
	if _mission == null:
		return
	var scene := _mission
	_mission = null
	scene.set_process(false)
	if is_instance_valid(scene._audio):
		scene._audio.stop_playback()
	scene.queue_free()
	await get_tree().process_frame

func _read(file: String) -> Variant:
	var path:=directory.path_join(file)
	var contents := FileAccess.get_file_as_string(path) if FileAccess.file_exists(path) else ""
	return JSON.parse_string(contents) if not contents.is_empty() else null

func _publish(state: String,message: String="") -> void:
	_pending_status = {"protocol_version":2,"runtime_id":runtime_id,
		"state":state,"session_id":_session_id,"message":message,"pid":OS.get_process_id()}
	_flush_status()

func _flush_status() -> void:
	if not _pending_status.is_empty() and Mailbox.publish(directory.path_join("status.json"), _pending_status):
		_pending_status.clear()

func _park_window() -> void:
	if DisplayServer.get_name()=="headless":return
	# Godot forbids Window.hide() on the main window; the native owner hides it on Windows.
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_NO_FOCUS,true)
	get_tree().root.position=Vector2i(-32000,-32000)

func _exit_tree() -> void:
	preload("res://scripts/runtime_texture_cache.gd").clear()
