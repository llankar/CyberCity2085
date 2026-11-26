extends "res://laboratory247.gd"

const Mailbox = preload("res://tactical_mailbox.gd")
const TacticalActor = preload("res://tactical_actor.gd")
const ALLY := "ally:0"
const CAST_CAPTURE := "E:/CyberCity2085-3d-lab/generated/phase2/warehouse333/tactical_cast.png"
var mailbox: Mailbox
var status: Label
var actors := {}
var last_sequence := -1
var smoke := false
var pending_command := {}


func _ready() -> void:
 await super._ready()
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
 if mailbox == null or mailbox.sequence == last_sequence or not mailbox.refresh():
  return
 last_sequence = mailbox.sequence
 var state := mailbox.state
 var readout: Array[String] = []
 for unit: Dictionary in state.units:
  var id: String = unit.id
  var point := Vector3(float(unit.cell[0])-19.5, 0, 13.5-float(unit.cell[1]))
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
 status.text = "Round %d   %s\n%s\nLeft click: move   Right click on hostile: fire   T: end turn" % [
  state.round, state.turn, "  |  ".join(readout)]
 if not mailbox.message.is_empty():
  status.text += "\n" + mailbox.message
 if state.outcome != null:
  status.text += "\n%s" % str(state.outcome).capitalize()
 if smoke:
  match last_sequence:
   0:
    send({"action": "move", "actor": ALLY, "destination": [20, 14]})
   1:
    var cell: Array = state.units[0].cell
    if int(cell[0]) != 20 or int(cell[1]) != 14 or int(state.units[0].ap) >= 3:
     get_tree().quit(2)
     return
    var ally: TacticalActor = actors[ALLY]
    var hostile: TacticalActor = actors["enemy:0"]
    if ally.animation.current_animation != ally.clips.walk:
     get_tree().quit(6)
     return
    await ally.movement.finished
    if not ally.position.is_equal_approx(Vector3(.5, 0, -.5)):
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
    if get_viewport().get_texture().get_image().save_png(CAST_CAPTURE) != OK:
     get_tree().quit(9)
     return
    send({"action": "end_turn", "actor": ALLY})
   3:
    print("TACTICAL_WAREHOUSE_EXCHANGE_OK round=", state.round)
    get_tree().quit()


func send(command: Dictionary) -> void:
 var error := mailbox.send(command)
 if error == OK:
  pending_command = command
 if error != OK and error != ERR_BUSY:
  push_error("Tactical command write failed: %s" % error_string(error))
  if smoke:
   get_tree().quit(3)


func target_center(actor: TacticalActor) -> Vector3:
 return actor.global_position + Vector3.UP * .85


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
