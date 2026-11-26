extends "res://laboratory247.gd"

const Mailbox = preload("res://tactical_mailbox.gd")
const ALLY := "ally:0"
const ENEMY := "enemy:0"
var mailbox: Mailbox
var status: Label
var actors := {}
var last_sequence := -1
var smoke := false


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
  if not actors.has(id):
   var marker := MeshInstance3D.new()
   var shape := CapsuleMesh.new()
   shape.radius = .26
   shape.height = 1.4
   marker.mesh = shape
   var surface := StandardMaterial3D.new()
   surface.albedo_color = Color.DEEP_SKY_BLUE if id == ALLY else Color.ORANGE_RED
   marker.material_override = surface
   add_child(marker)
   actors[id] = marker
  var model: MeshInstance3D = actors[id]
  model.position = Vector3(float(unit.cell[0])-19.5, .7, 13.5-float(unit.cell[1]))
  model.visible = int(unit.hp) > 0
  readout.append("%s  HP %d  AP %d" % [id, unit.hp, unit.ap])
 status.text = "Round %d   %s\n%s\nClick: move   T: end turn" % [
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
    send({"action": "end_turn", "actor": ALLY})
   2:
    print("TACTICAL_WAREHOUSE_EXCHANGE_OK round=", state.round)
    get_tree().quit()


func send(command: Dictionary) -> void:
 var error := mailbox.send(command)
 if error != OK and error != ERR_BUSY:
  push_error("Tactical command write failed: %s" % error_string(error))
  if smoke:
   get_tree().quit(3)


func _unhandled_input(event: InputEvent) -> void:
 super._unhandled_input(event)
 if mailbox == null or mailbox.state.get("outcome") != null:
  return
 if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_T:
  send({"action": "end_turn", "actor": ALLY})
 if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
  var ray := review_camera.project_ray_normal(event.position)
  var origin := review_camera.project_ray_origin(event.position)
  var ground: Variant = Plane(Vector3.UP, 0).intersects_ray(origin, ray)
  if ground is Vector3:
   send({"action": "move", "actor": ALLY,
    "destination": [floori(ground.x + 20), floori(14 - ground.z)]})
