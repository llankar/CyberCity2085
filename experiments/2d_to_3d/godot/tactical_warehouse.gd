extends "res://laboratory247.gd"

const Mailbox = preload("res://tactical_mailbox.gd")
const TacticalActor = preload("res://tactical_actor.gd")
const Effects = preload("res://tactical_effects.gd")
const Cutaway = preload("res://source_cutaway271.gd")
const ALLY := "ally:0"
@export var scenario_title := "Warehouse"
var mailbox: Mailbox
var status: Label
var selection: Label
var selected_ally := ALLY
var effects: Effects
var cutaway := Cutaway.new()
var actors := {}
var last_sequence := -1
var smoke := false
var pending_command := {}
var smoke_command_sent_usec := 0
var smoke_destination: Array[int]
var playing_events := false
var attack_mode := "fire"
var smoke_hp := 0
var smoke_patient := ALLY


func _ready() -> void:
 var session := OS.get_environment("CYBERCITY_TACTICAL_SESSION")
 if session.is_empty():
  push_error("Launch this scene with run_tactical_preview.py")
  get_tree().quit(1)
  return
 var path := session.path_join("battlefield.json")
 var deadline := Time.get_ticks_msec() + 5000
 while not FileAccess.file_exists(path) and Time.get_ticks_msec() < deadline:
  await get_tree().process_frame
 var presentation := JSON.new()
 if presentation.parse(FileAccess.get_file_as_string(path)) != OK or not apply_presentation(presentation.data):
  push_error("Could not open the selected 3D battlefield")
  get_tree().quit(16)
  return
 await super._ready()
 if review_camera == null:
  return
 for child in get_children():
  if child is CanvasLayer:
   child.hide()
 mailbox = Mailbox.new(session)
 cutaway.configure(self, [], review_camera, true)
 smoke = OS.get_environment("CYBERCITY_TACTICAL_SMOKE") == "1"
 var hud := CanvasLayer.new()
 add_child(hud)
 status = Label.new()
 status.position = Vector2(20, 85)
 status.add_theme_font_size_override("font_size", 22)
 hud.add_child(status)
 selection = Label.new()
 selection.position = Vector2(20, 48)
 selection.add_theme_font_size_override("font_size", 23)
 hud.add_child(selection)
 effects = Effects.new()
 add_child(effects)


func apply_presentation(config: Dictionary) -> bool:
 var scene := load(config.preview_scene) as PackedScene
 if scene == null:
  return false
 # Read the preview settings without adding its scripted tour to the tree.
 var preview := scene.instantiate()
 scenario_title = config.title
 review_folder = preview.review_folder
 review_model_name = preview.review_model_name
 use_market_ground = preview.use_market_ground
 market_ground_filename = preview.market_ground_filename
 review_ambient_color = preview.review_ambient_color
 review_ambient_energy = preview.review_ambient_energy
 review_key_energy = preview.review_key_energy
 review_size = minf(preview.review_size, 31.0)
 save_review_capture = false
 preview.free()
 return true


func _process(delta: float) -> void:
 if cutaway.camera != null:
  cutaway.update(delta)
 if effects != null:
  effects.step(delta, effects.clock + delta)
 if mailbox == null or playing_events or mailbox.sequence == last_sequence or not mailbox.refresh():
  return
 last_sequence = mailbox.sequence
 if smoke and smoke_command_sent_usec > 0:
  print("TACTICAL_REPLY action=%s sequence=%d ms=%.2f" % [
   pending_command.action, last_sequence, (Time.get_ticks_usec()-smoke_command_sent_usec)/1000.0])
  smoke_command_sent_usec = 0
 var state := mailbox.state
 if not mailbox.events.is_empty():
  playing_events = true
  await play_phase_events(mailbox.events)
  playing_events = false
 var readout: Array[String] = []
 for unit: Dictionary in state.units:
  var id: String = unit.id
  var point := cell_position(unit.cell)
  if not actors.has(id):
   var actor := TacticalActor.new()
   add_child(actor)
   if not actor.configure(id.begins_with("ally:"), id == "ally:1", point):
    push_error("Could not load retained tactical actor: " + id)
    get_tree().quit(5)
    return
   actors[id] = actor
  var model: TacticalActor = actors[id]
  model.update_state(point, int(unit.hp))
  var stance := "  OVERWATCH" if unit.overwatch else "  DEFENDING" if unit.defending else ""
  readout.append("%s  HP %d  AP %d%s" % [unit.name, unit.hp, unit.ap, stance])
 if mailbox.success:
  var action: String = pending_command.get("action", "")
  if action in ["fire", "melee", "psi", "first_aid"]:
   var actor: TacticalActor = actors[pending_command.actor]
   var target: TacticalActor = actors[pending_command.get("target", pending_command.actor)]
   actor.play_action(target.position, "aid" if action == "first_aid" else action)
   if action == "first_aid":
    effects.tactical_aid(target_center(target))
   else:
    effects.tactical_attack(action, target_center(actor), target_center(target),
     bool(mailbox.attack.get("hit", false)), int(mailbox.attack.get("damage", 0)),
     pending_command.actor == ALLY)
  elif action == "move":
   effects.sound("step", actors[pending_command.actor].global_position, -18)
 pending_command.clear()
 if actors[selected_ally].fallen:
  select_next_ally()
 refresh_selection()
 status.text = "%s  //  Round %d   %s\n%s\nLeft click: select or move   Right click: %s   F / M / P: attack mode\nA: self aid   Shift+A: aid hovered ally   B: defend   O: overwatch\nTab: next agent   T: end turn   Q / E: rotate   Wheel: zoom   Middle drag: pan   Home: focus   Esc: close" % [
  scenario_title, state.round, state.turn, "  |  ".join(readout), attack_mode]
 if not mailbox.message.is_empty():
  status.text += "\n" + mailbox.message
 if state.outcome != null:
  status.text += "\n%s" % str(state.outcome).capitalize()
 if last_sequence == 0 and OS.get_environment("CYBERCITY_TACTICAL_BENCHMARK") == "1":
  run_render_benchmark()
 if smoke:
  match last_sequence:
   0:
    focus_selected()
    if not review_target.is_equal_approx(cell_position(state.units[0].cell)):
     push_error("Camera did not focus the active operative")
     get_tree().quit(19)
     return
    var drag := InputEventMouseMotion.new()
    drag.button_mask = MOUSE_BUTTON_MASK_MIDDLE
    drag.position = get_viewport().get_visible_rect().get_center()
    drag.relative = Vector2(40, 20)
    var focused := review_target
    _unhandled_input(drag)
    if review_target.is_equal_approx(focused):
     push_error("Camera did not pan with middle drag")
     get_tree().quit(20)
     return
    focus_selected()
    # Let the initial actors and materials render before driving input.
    for frame in 3:
     await get_tree().process_frame
    var start: Array = state.units[0].cell
    var enemy: Array = unit_state("enemy:0").cell
    smoke_destination = [int(start[0]) + signi(int(enemy[0]) - int(start[0])),
                         int(start[1]) + signi(int(enemy[1]) - int(start[1]))]
    send({"action": "move", "actor": ALLY, "destination": smoke_destination})
   1:
    var cell: Array = state.units[0].cell
    if int(cell[0]) != smoke_destination[0] or int(cell[1]) != smoke_destination[1] or int(state.units[0].ap) >= 3:
     get_tree().quit(2)
     return
    var ally: TacticalActor = actors[ALLY]
    var hostile: TacticalActor = actors["enemy:0"]
    if ally.animation.current_animation != ally.clips.walk:
     get_tree().quit(6)
     return
    await ally.movement.finished
    if not ally.position.is_equal_approx(cell_position(smoke_destination)):
     get_tree().quit(7)
     return
    fire_at(review_camera.unproject_position(target_center(hostile)))
   2:
    if not mailbox.success or int(state.units[0].ap) != 1:
     push_error(mailbox.message)
     get_tree().quit(4)
     return
    var ally: TacticalActor = actors[ALLY]
    if ally.animation.current_animation != ally.clips.fire:
     get_tree().quit(8)
     return
    var recorded := effects.audio_events
    var hit_audio := int(bool(mailbox.attack.get("hit", false)) and int(mailbox.attack.get("damage",0)) > 0)
    if recorded.size() != 2 + hit_audio or not str(recorded[1].file).ends_with("fire_pistol_01.wav"):
     push_error("Unexpected tactical shot audio")
     get_tree().quit(17)
     return
    await RenderingServer.frame_post_draw
    if get_viewport().get_texture().get_image().save_png(review_folder + "tactical_cast.png") != OK:
     get_tree().quit(9)
     return
    send({"action": "end_turn", "actor": ALLY})
   3:
    if not mailbox.success or int(state.round) != 2 or state.turn != "player":
     push_error(mailbox.message)
     get_tree().quit(10)
     return
    smoke_patient = ALLY if mailbox.events.is_empty() else mailbox.events[0].target
    smoke_hp = int(unit_state(smoke_patient).hp)
    use_action("first_aid", smoke_patient)
   4:
    var patient := unit_state(smoke_patient)
    if not mailbox.success or int(patient.hp) != mini(smoke_hp + 2, int(patient.max_hp)):
     get_tree().quit(11)
     return
    use_action("defend")
   5:
    select_next_ally()
    if selected_ally != "ally:1":
     get_tree().quit(12)
     return
    use_action("psi", "enemy:0")
   6:
    var oracle: TacticalActor = actors["ally:1"]
    var blocked := not mailbox.success and "line blocked" in mailbox.message
    if blocked:
     print("TACTICAL_PSI_BLOCKED map=", scenario_title)
    elif not mailbox.success or oracle.animation.current_animation != oracle.clips.psi:
     push_error(mailbox.message)
     get_tree().quit(13)
     return
    await RenderingServer.frame_post_draw
    if get_viewport().get_texture().get_image().save_png(review_folder + "tactical_psi.png") != OK:
     get_tree().quit(14)
     return
    var longshot: TacticalActor = actors[ALLY]
    review_target = (longshot.position + oracle.position) / 2 + Vector3.UP * .90
    review_distance = 5.0
    review_elevation = 2.5
    review_yaw += PI
    review_camera.size = 3.4
    status.hide()
    selection.hide()
    update_review_camera()
    cutaway.update(.15)
    await RenderingServer.frame_post_draw
    if get_viewport().get_texture().get_image().save_png(review_folder + "tactical_squad_close.png") != OK:
     get_tree().quit(15)
     return
    await get_tree().create_timer(.7).timeout
    print("TACTICAL_EXCHANGE_OK map=", scenario_title, " round=", state.round)
    get_tree().quit()


func run_render_benchmark() -> void:
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 for index in 45:
  await get_tree().process_frame
 var durations: Array[float] = []
 var previous := Time.get_ticks_usec()
 var initial_yaw := review_yaw
 for index in 180:
  review_yaw = initial_yaw + TAU * index / 180.0
  update_review_camera()
  await get_tree().process_frame
  var current := Time.get_ticks_usec()
  durations.append((current - previous) / 1000.0)
  previous = current
 durations.sort()
 print("TACTICAL_FRAME_TIMES map=%s viewport=%s frames=%d median_ms=%.2f p95_ms=%.2f vsync=%d" % [
  scenario_title, get_viewport().get_visible_rect().size, durations.size(),
  durations[90], durations[170], DisplayServer.window_get_vsync_mode()])
 get_tree().quit()


func send(command: Dictionary) -> void:
 if playing_events:
  return
 var error := mailbox.send(command)
 if error == OK:
  pending_command = command
  if smoke:
   smoke_command_sent_usec = Time.get_ticks_usec()
 if error != OK and error != ERR_BUSY:
  push_error("Tactical command write failed: %s" % error_string(error))
  if smoke:
   get_tree().quit(3)


func target_center(actor: TacticalActor) -> Vector3:
 return actor.global_position + Vector3.UP * .85


func cell_position(cell: Array) -> Vector3:
 return Vector3(float(cell[0])-19.5, 0, 13.5-float(cell[1]))


func play_phase_events(events: Array) -> void:
 for event: Dictionary in events:
  var attacker: TacticalActor = actors[event.actor]
  var from := cell_position(event.from_cell)
  attacker.update_state(from, 1)
  if attacker.movement != null and attacker.movement.is_running():
   await attacker.movement.finished
  var melee: bool = event.kind == "attack" and from.distance_to(cell_position(event.to_cell)) <= 1.0
  attacker.fire_at(cell_position(event.to_cell), melee)
  effects.tactical_attack("melee" if melee else "fire", target_center(attacker),
   cell_position(event.to_cell) + Vector3.UP*.85, true, int(event.damage), event.actor == ALLY)
  status.text = "%s  //  Enemy phase\n%s → %s   %d damage" % [
   scenario_title, event.actor, event.target, event.damage]
  await get_tree().create_timer(.42).timeout
  if smoke:
   print("TACTICAL_PHASE_EVENT_PLAYED actor=", event.actor, " damage=", event.damage)


func fire_at(screen_position: Vector2) -> void:
 var nearest := actor_at(screen_position, "enemy:")
 if not nearest.is_empty():
  use_action(attack_mode, nearest)


func actor_at(screen_position: Vector2, side: String) -> String:
 var nearest := ""
 var radius := 26.0
 for id: String in actors:
  var actor: TacticalActor = actors[id]
  var center := target_center(actor)
  if not id.begins_with(side) or actor.fallen or review_camera.is_position_behind(center):
   continue
  var distance := screen_position.distance_to(review_camera.unproject_position(center))
  if distance < radius:
   nearest = id
   radius = distance
 return nearest


func refresh_selection() -> void:
 var active: TacticalActor = actors[selected_ally]
 cutaway.actors = [] if active.fallen else [active]
 for unit: Dictionary in mailbox.state.units:
  if unit.id.begins_with("ally:"):
   actors[unit.id].ring.scale = Vector3.ONE * (1.22 if unit.id == selected_ally else 1.0)
  if unit.id == selected_ally:
   selection.text = "Selected: " + unit.name if int(unit.hp) > 0 else "No living agent"


func select_next_ally() -> void:
 var living: Array[String] = []
 for unit: Dictionary in mailbox.state.units:
  if unit.id.begins_with("ally:") and int(unit.hp) > 0:
   living.append(unit.id)
 if not living.is_empty():
  selected_ally = living[(living.find(selected_ally)+1) % living.size()]
  refresh_selection()


func use_action(action: String, target := "") -> void:
 if mailbox.state.is_empty() or playing_events or mailbox.pending:
  return
 var actions: Array = unit_state(selected_ally).get("actions", [])
 if action not in actions:
  status.text += "\nAction unavailable: " + action.capitalize()
  return
 var command := {"action": action, "actor": selected_ally}
 if not target.is_empty():
  command["target"] = target
 send(command)


func unit_state(id: String) -> Dictionary:
 for unit: Dictionary in mailbox.state.units:
  if unit.id == id:
   return unit
 return {}


func focus_selected() -> void:
 var actor: TacticalActor = actors.get(selected_ally)
 if actor == null or actor.fallen:
  return
 review_target = Vector3(actor.position.x, 0, actor.position.z)
 update_review_camera()


func ground_under_cursor(screen_point: Vector2) -> Variant:
 return Plane(Vector3.UP, 0).intersects_ray(
  review_camera.project_ray_origin(screen_point), review_camera.project_ray_normal(screen_point))


func _unhandled_input(event: InputEvent) -> void:
 if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
  get_tree().quit()
  return
 if review_camera == null:
  return
 super._unhandled_input(event)
 if event is InputEventMouseMotion and event.button_mask & MOUSE_BUTTON_MASK_MIDDLE:
  var previous: Variant = ground_under_cursor(event.position - event.relative)
  var current: Variant = ground_under_cursor(event.position)
  if previous is Vector3 and current is Vector3:
   review_target += previous - current
   review_target.x = clampf(review_target.x, -20.0, 20.0)
   review_target.z = clampf(review_target.z, -14.0, 14.0)
   update_review_camera()
 if mailbox == null or mailbox.state.get("outcome") != null:
  return
 if event is InputEventKey and event.pressed and not event.echo:
  var previous_mode := attack_mode
  match event.keycode:
   KEY_T: use_action("end_turn")
   KEY_A:
    var target := actor_at(get_viewport().get_mouse_position(), "ally:") if event.shift_pressed else selected_ally
    if not target.is_empty():
     use_action("first_aid", target)
   KEY_B: use_action("defend")
   KEY_O: use_action("overwatch")
   KEY_F: attack_mode = "fire"
   KEY_M: attack_mode = "melee"
   KEY_P: attack_mode = "psi"
   KEY_HOME: focus_selected()
   KEY_TAB:
    if not playing_events and not mailbox.state.is_empty():
     select_next_ally()
  if previous_mode != attack_mode and not playing_events:
   status.text = status.text.replace("Right click: " + previous_mode, "Right click: " + attack_mode)
 if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_RIGHT:
  fire_at(event.position)
 if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
  var ally := actor_at(event.position, "ally:")
  if not ally.is_empty() and not playing_events and not mailbox.pending:
   selected_ally = ally
   refresh_selection()
   return
  var ground: Variant = ground_under_cursor(event.position)
  if ground is Vector3:
   send({"action": "move", "actor": selected_ally,
    "destination": [floori(ground.x + 20), floori(14 - ground.z)]})
