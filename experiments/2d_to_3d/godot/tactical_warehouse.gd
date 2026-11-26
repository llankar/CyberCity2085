extends "res://laboratory247.gd"

const Mailbox = preload("res://tactical_mailbox.gd")
const TacticalActor = preload("res://tactical_actor.gd")
const ALLY := "ally:0"
@export var scenario_title := "Warehouse"
var mailbox: Mailbox
var status: Label
var actors := {}
var last_sequence := -1
var smoke := false
var pending_command := {}
var smoke_destination: Array[int]
var playing_events := false


func _ready() -> void:
 await super._ready()
 for child in get_children():
  if child is CanvasLayer:
   child.hide()
 var session := OS.get_environment("CYBERCITY_TACTICAL_SESSION")
 if session.is_empty():
  push_error("Launch this scene with run_tactical_preview.py")
  get_tree().quit(1)
  return
 mailbox = Mailbox.new(session)
 smoke = OS.get_environment("CYBERCITY_TACTICAL_SMOKE") == "1"
 var hud := CanvasLayer.new()
 add_child(hud)
 status = Label.new()
 status.position = Vector2(20, 85)
 status.add_theme_font_size_override("font_size", 22)
 hud.add_child(status)


func _process(_delta: float) -> void:
 if mailbox == null or playing_events or mailbox.sequence == last_sequence or not mailbox.refresh():
  return
 last_sequence = mailbox.sequence
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
   if not actor.configure(id == ALLY, point):
    push_error("Could not load retained tactical actor: " + id)
    get_tree().quit(5)
    return
   actors[id] = actor
  var model: TacticalActor = actors[id]
  model.update_state(point, int(unit.hp))
  readout.append("%s  HP %d  AP %d" % [id, unit.hp, unit.ap])
 if mailbox.success and pending_command.get("action") == "fire":
  var shooter: TacticalActor = actors[ALLY]
  var victim: TacticalActor = actors[pending_command.target]
  shooter.fire_at(victim.position)
 pending_command.clear()
 status.text = "%s  //  Round %d   %s\n%s\nLeft click: move   Right click on hostile: fire   T: end turn\nQ / E: rotate   Wheel: zoom   Esc: close" % [
  scenario_title, state.round, state.turn, "  |  ".join(readout)]
 if not mailbox.message.is_empty():
  status.text += "\n" + mailbox.message
 if state.outcome != null:
  status.text += "\n%s" % str(state.outcome).capitalize()
 if smoke:
  match last_sequence:
   0:
    var start: Array = state.units[0].cell
    smoke_destination = [int(start[0])+1, int(start[1])]
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
    await RenderingServer.frame_post_draw
    if get_viewport().get_texture().get_image().save_png(review_folder + "tactical_cast.png") != OK:
     get_tree().quit(9)
     return
    send({"action": "end_turn", "actor": ALLY})
   3:
    print("TACTICAL_EXCHANGE_OK map=", scenario_title, " round=", state.round)
    get_tree().quit()


func send(command: Dictionary) -> void:
 if playing_events:
  return
 var error := mailbox.send(command)
 if error == OK:
  pending_command = command
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
  status.text = "%s  //  Enemy phase\n%s → %s   %d damage" % [
   scenario_title, event.actor, event.target, event.damage]
  await get_tree().create_timer(.42).timeout
  if smoke:
   print("TACTICAL_PHASE_EVENT_PLAYED actor=", event.actor, " damage=", event.damage)


func fire_at(screen_position: Vector2) -> void:
 var nearest := ""
 var radius := 26.0
 for id: String in actors:
  var actor: TacticalActor = actors[id]
  var center := target_center(actor)
  if not id.begins_with("enemy:") or actor.fallen or review_camera.is_position_behind(center):
   continue
  var distance := screen_position.distance_to(review_camera.unproject_position(center))
  if distance < radius:
   nearest = id
   radius = distance
 if not nearest.is_empty():
  send({"action": "fire", "actor": ALLY, "target": nearest})


func _unhandled_input(event: InputEvent) -> void:
 super._unhandled_input(event)
 if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
  get_tree().quit()
  return
 if mailbox == null or mailbox.state.get("outcome") != null:
  return
 if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_T:
  send({"action": "end_turn", "actor": ALLY})
 if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_RIGHT:
  fire_at(event.position)
 if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
  var ray := review_camera.project_ray_normal(event.position)
  var origin := review_camera.project_ray_origin(event.position)
  var ground: Variant = Plane(Vector3.UP, 0).intersects_ray(origin, ray)
  if ground is Vector3:
   send({"action": "move", "actor": ALLY,
    "destination": [floori(ground.x + 20), floori(14 - ground.z)]})
