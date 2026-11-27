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
var target_hint: Label
var control_hints: Label
var target_line: MeshInstance3D
var outcome_panel: PanelContainer
var outcome_title: Label
var outcome_details: Label
var outcome_close: Button
var selected_ally := ALLY
var effects: Effects
var cutaway := Cutaway.new()
var actors := {}
var move_markers: Array[MeshInstance3D] = []
var open_move_material: StandardMaterial3D
var cover_move_material: StandardMaterial3D
var actor_models: Dictionary[String, PackedScene] = {}
var last_sequence := -1
var smoke := false
var benchmark_combat := false
var combat_frame_times: Array[float] = []
var combat_frame_previous_usec := 0
var smoke_outcome := ""
var closing := false
var pending_command := {}
var smoke_command_sent_usec := 0
var smoke_destination: Array[int]
var playing_events := false
var attack_mode := "fire"
var smoke_hp := 0
var smoke_patient := ALLY


func _ready() -> void:
 get_tree().auto_accept_quit = false
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
 var actor_fill := DirectionalLight3D.new()
 actor_fill.name = "Tactical actor fill"
 actor_fill.rotation_degrees = Vector3(-27, 145, 0)
 actor_fill.light_color = Color(.77, .85, 1.0)
 actor_fill.light_energy = .34
 actor_fill.light_cull_mask = TacticalActor.FILL_LIGHT_LAYER
 actor_fill.shadow_enabled = false
 add_child(actor_fill)
 mailbox = Mailbox.new(session)
 cutaway.configure(self, [], review_camera, true)
 smoke = OS.get_environment("CYBERCITY_TACTICAL_SMOKE") == "1"
 benchmark_combat = OS.get_environment("CYBERCITY_TACTICAL_BENCHMARK_COMBAT") == "1"
 smoke_outcome = OS.get_environment("CYBERCITY_TACTICAL_SMOKE_OUTCOME")
 var hud := CanvasLayer.new()
 add_child(hud)
 var hud_stack := VBoxContainer.new()
 hud_stack.position = Vector2(20, 24)
 hud_stack.add_theme_constant_override("separation", 6)
 hud.add_child(hud_stack)
 selection = Label.new()
 selection.add_theme_color_override("font_color", Color(.59,.91,1))
 selection.add_theme_font_size_override("font_size", 23)
 hud_stack.add_child(selection)
 status = Label.new()
 status.add_theme_font_size_override("font_size", 19)
 hud_stack.add_child(status)
 target_hint = Label.new()
 target_hint.add_theme_font_size_override("font_size", 18)
 hud_stack.add_child(target_hint)
 control_hints = Label.new()
 control_hints.add_theme_font_size_override("font_size", 16)
 hud.add_child(control_hints)
 control_hints.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
 control_hints.grow_vertical = Control.GROW_DIRECTION_BEGIN
 control_hints.offset_left = 20
 control_hints.offset_bottom = -20
 for label: Label in [status, selection, target_hint, control_hints]:
  label.add_theme_color_override("font_outline_color", Color(.025,.047,.063))
  label.add_theme_constant_override("outline_size", 5)
 update_control_hints()
 target_line = MeshInstance3D.new()
 var guide_mesh := CylinderMesh.new()
 guide_mesh.height = 1
 guide_mesh.top_radius = .016
 guide_mesh.bottom_radius = .016
 guide_mesh.radial_segments = 6
 var guide_material := StandardMaterial3D.new()
 guide_material.albedo_color = Color(.28,.90,1)
 guide_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
 target_line.mesh = guide_mesh
 target_line.material_override = guide_material
 target_line.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
 target_line.hide()
 add_child(target_line)
 effects = Effects.new()
 add_child(effects)
 var marker_mesh := TorusMesh.new()
 marker_mesh.inner_radius = .265
 marker_mesh.outer_radius = .31
 marker_mesh.rings = 16
 marker_mesh.ring_segments = 6
 open_move_material = StandardMaterial3D.new()
 open_move_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
 open_move_material.albedo_color = Color(.15,.66,.74)
 cover_move_material = open_move_material.duplicate() as StandardMaterial3D
 cover_move_material.albedo_color = Color(.98,.65,.19)
 for index in 4:
  var marker := MeshInstance3D.new()
  marker.mesh = marker_mesh
  marker.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  marker.hide()
  add_child(marker)
  move_markers.append(marker)


 outcome_panel = PanelContainer.new()
 outcome_panel.position = Vector2(20, 110)
 outcome_panel.custom_minimum_size = Vector2(330, 145)
 outcome_panel.hide()
 hud.add_child(outcome_panel)
 var results := VBoxContainer.new()
 results.add_theme_constant_override("separation", 10)
 outcome_panel.add_child(results)
 outcome_title = Label.new()
 outcome_title.add_theme_font_size_override("font_size", 32)
 results.add_child(outcome_title)
 outcome_details = Label.new()
 results.add_child(outcome_details)
 outcome_close = Button.new()
 outcome_close.text = "Close skirmish"
 outcome_close.pressed.connect(close_battlefield)
 results.add_child(outcome_close)


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
 if closing:
  return
 if combat_frame_previous_usec > 0:
  var now := Time.get_ticks_usec()
  combat_frame_times.append((now - combat_frame_previous_usec) / 1000.0)
  combat_frame_previous_usec = now
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
  if closing:
   return
 var readout: Array[String] = []
 for unit: Dictionary in state.units:
  var id: String = unit.id
  var point := cell_position(unit.cell)
  if not actors.has(id):
   var actor := TacticalActor.new()
   add_child(actor)
   if not actor.configure(id.begins_with("ally:"), id == "ally:1", point, actor_models):
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
 refresh_target_hint(get_viewport().get_mouse_position())
 status.text = "%s  //  Round %d  %s\n%s" % [
  scenario_title, state.round, state.turn, "  |  ".join(readout)]
 if not mailbox.message.is_empty():
  status.text += "\n" + mailbox.message
 if state.outcome != null:
  show_outcome(state)
 if last_sequence == 0 and OS.get_environment("CYBERCITY_TACTICAL_BENCHMARK") == "1":
  run_render_benchmark()
 if smoke:
  match last_sequence:
   0:
    if actor_models.size() != 2 or actors["ally:0"].animation == actors["ally:1"].animation:
     push_error("Tactical allies must share their import and own separate animation players")
     get_tree().quit(22)
     return
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
    if not benchmark_combat and not verify_move_hover(state.units[0]):
     get_tree().quit(23)
     return
    if benchmark_combat:
     DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
     review_size = minf(review_size, 14.0)
     focus_selected()
     for frame in 45:
      await get_tree().process_frame
     combat_frame_previous_usec = Time.get_ticks_usec()
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
    var aim_point := review_camera.unproject_position(target_center(hostile))
    var motion := InputEventMouseMotion.new()
    motion.position = aim_point
    var target_data: Dictionary = unit_state(ALLY).get("targeting", {}).get("enemy:0", {})
    var fire_context: Dictionary = target_data.get("fire", {})
    _unhandled_input(motion)
    var expected_chance := "%d%% hit chance" % int(fire_context.get("hit_percent", -1))
    if not target_line.visible or not target_hint.text.ends_with(expected_chance):
     push_error("Valid shot did not show the hit chance supplied by the combat engine")
     get_tree().quit(23)
     return
    var melee_context: Dictionary = target_data.get("melee", {})
    if not melee_context.is_empty() and not melee_context.in_range:
     attack_mode = "melee"
     _unhandled_input(motion)
     if target_line.visible or not target_hint.text.ends_with("Out of range"):
      push_error("Out-of-range melee showed a targeting guide or an incorrect hint")
      get_tree().quit(23)
      return
     print("TACTICAL_TARGET_HOVER_OK melee out of range")
     attack_mode = "fire"
    refresh_target_hint(aim_point)
    print("TACTICAL_TARGET_HOVER_OK fire ", expected_chance)
    fire_at(aim_point)
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
    var outcome := effects.get_node_or_null("AttackOutcome") as Label3D
    var hit := bool(mailbox.attack.get("hit", false))
    var damage := int(mailbox.attack.get("damage", 0))
    var expected_outcome := "MISS" if not hit else ("NO DAMAGE" if damage <= 0 else "-%d HP" % damage)
    if outcome == null or outcome.text != expected_outcome:
     push_error("Attack outcome label does not match the combat response")
     get_tree().quit(24)
     return
    print("TACTICAL_ATTACK_OUTCOME_OK ", expected_outcome)
    var hit_audio := int(bool(mailbox.attack.get("hit", false)) and int(mailbox.attack.get("damage",0)) > 0)
    if recorded.size() != 2 + hit_audio or not str(recorded[1].file).ends_with("fire_pistol_01.wav"):
     push_error("Unexpected tactical shot audio")
     get_tree().quit(17)
     return
    if smoke_outcome == "victory":
     verify_smoke_outcome("victory", 2)
     return
    if not benchmark_combat:
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
    if smoke_outcome == "defeat":
     send({"action": "end_turn", "actor": ALLY})
     return
    smoke_patient = ALLY if mailbox.events.is_empty() else mailbox.events[0].target
    smoke_hp = int(unit_state(smoke_patient).hp)
    use_action("first_aid", smoke_patient)
   4:
    if smoke_outcome == "defeat":
     verify_smoke_outcome("defeat", 0)
     return
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
    if benchmark_combat:
     if not blocked:
      await oracle.animation.animation_finished
     combat_frame_previous_usec = 0
     combat_frame_times.sort()
     var count := combat_frame_times.size()
     if count < 2:
      get_tree().quit(24)
      return
     print("TACTICAL_COMBAT_FRAME_TIMES map=%s viewport=%s frames=%d median_ms=%.2f p95_ms=%.2f max_ms=%.2f psi=%s" % [
      scenario_title, get_viewport().get_visible_rect().size, count, combat_frame_times[count >> 1],
      combat_frame_times[ceili(count*.95)-1], combat_frame_times[-1], "blocked" if blocked else "cast"])
     print("TACTICAL_EXCHANGE_OK map=", scenario_title, " round=", state.round)
     get_tree().root.propagate_notification(NOTIFICATION_WM_CLOSE_REQUEST)
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
    control_hints.hide()
    target_hint.hide()
    target_line.hide()
    update_review_camera()
    cutaway.update(.15)
    await RenderingServer.frame_post_draw
    if get_viewport().get_texture().get_image().save_png(review_folder + "tactical_squad_close.png") != OK:
     get_tree().quit(15)
     return
    print("TACTICAL_EXCHANGE_OK map=", scenario_title, " round=", state.round)
    get_tree().root.propagate_notification(NOTIFICATION_WM_CLOSE_REQUEST)
    if not closing:
     push_error("Window close did not begin tactical shutdown")
     get_tree().quit(21)


func _notification(what: int) -> void:
 if what == NOTIFICATION_WM_CLOSE_REQUEST and is_inside_tree():
  close_battlefield()


func show_outcome(state: Dictionary) -> void:
 var standing := 0
 var squad_size := 0
 for unit: Dictionary in state.units:
  if str(unit.id).begins_with("ally:"):
   squad_size += 1
   standing += int(unit.hp > 0)
 outcome_title.text = "Victory" if state.outcome == "victory" else "Defeat"
 outcome_title.modulate = Color(.28,.88,.71) if state.outcome == "victory" else Color(1,.35,.30)
 outcome_details.text = "%s  //  Round %d\nAgents standing: %d / %d" % [
  scenario_title, state.round, standing, squad_size]
 status.hide()
 selection.hide()
 target_hint.hide()
 target_line.hide()
 outcome_panel.show()


func verify_smoke_outcome(expected: String, standing: int) -> void:
 if not outcome_panel.visible or outcome_title.text != expected.capitalize() or not outcome_details.text.ends_with("%d / 2" % standing):
  push_error("The %s outcome did not reach the skirmish panel" % expected)
  get_tree().quit(24)
  return
 await RenderingServer.frame_post_draw
 if get_viewport().get_texture().get_image().save_png(review_folder + "tactical_%s.png" % expected) != OK:
  get_tree().quit(25)
  return
 outcome_close.pressed.emit()
 if not closing:
  get_tree().quit(26)
  return
 print("TACTICAL_OUTCOME_PANEL_OK result=", expected, " map=", scenario_title)


func close_battlefield() -> void:
 if closing:
  return
 closing = true
 if effects != null:
  effects.stop_sounds()
  # Allow the audio server to process the stop before its shutdown.
  await get_tree().create_timer(.12).timeout
 get_tree().quit()



func update_control_hints() -> void:
 control_hints.text = ("Click: select or move  //  Right click: %s  //  F / M / P: attack mode\n" +
  "A: aid  //  Shift+A: aid ally  //  B: defend  //  O: overwatch\n" +
  "Tab: next agent  //  T: end turn  //  Q / E: rotate  //  Wheel: zoom  //  Middle drag: pan  //  Home: focus  //  Esc: close") % attack_mode

func run_render_benchmark() -> void:
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 await benchmark_view("overview-orbit", true)
 review_size = minf(review_size, 14.0)
 focus_selected()
 await benchmark_view("tactical-idle", false)
 await benchmark_view("tactical-orbit", true)
 get_tree().quit()


func benchmark_view(label: String, orbit: bool) -> void:
 for index in 45:
  await get_tree().process_frame
 var durations: Array[float] = []
 var previous := Time.get_ticks_usec()
 var initial_yaw := review_yaw
 for index in 180:
  if orbit:
   review_yaw = initial_yaw + TAU * index / 180.0
   update_review_camera()
  await get_tree().process_frame
  var current := Time.get_ticks_usec()
  durations.append((current - previous) / 1000.0)
  previous = current
 durations.sort()
 print("TACTICAL_FRAME_TIMES map=%s viewport=%s frames=%d median_ms=%.2f p95_ms=%.2f vsync=%d view=%s zoom=%.1f" % [
  scenario_title, get_viewport().get_visible_rect().size, durations.size(),
  durations[90], durations[170], DisplayServer.window_get_vsync_mode(), label, review_size])


func send(command: Dictionary) -> void:
 if playing_events:
  return
 var error := mailbox.send(command)
 if error == OK:
  pending_command = command
  target_line.hide()
  target_hint.text = ""
  target_hint.hide()
  for marker in move_markers:
   marker.hide()
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
  if closing:
   return
  var attacker: TacticalActor = actors[event.actor]
  var from := cell_position(event.from_cell)
  attacker.update_state(from, 1)
  if attacker.movement != null and attacker.movement.is_running():
   await attacker.movement.finished
   if closing:
    return
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


func same_cell(left: Array, right: Array) -> bool:
 return right.size() == 2 and int(left[0]) == int(right[0]) and int(left[1]) == int(right[1])


func contains_cell(cells: Array, cell: Array) -> bool:
 return cells.any(func(candidate: Array) -> bool: return same_cell(cell, candidate))


func verify_move_hover(unit: Dictionary) -> bool:
 var candidates := {}
 var moves: Array = unit.get("moves", [])
 var covered: Array = unit.get("covered_moves", [])
 for row in range(28):
  for column in range(40):
   var cell := [column, row]
   if same_cell(cell, unit.cell):
    continue
   var point := review_camera.unproject_position(cell_position(cell))
   if not get_viewport().get_visible_rect().has_point(point) or not actor_at(point, "").is_empty():
    continue
   var expected := "Cannot move here"
   if contains_cell(covered, cell):
    expected = "Move to cover"
   elif contains_cell(moves, cell):
    expected = "Move"
   if not candidates.has(expected):
    candidates[expected] = point
 if not candidates.has("Cannot move here") or candidates.size() < 2:
  push_error("No visible smoke test cells for both reachable and unreachable ground")
  return false
 for expected: String in candidates:
  var hover := InputEventMouseMotion.new()
  hover.position = candidates[expected]
  _unhandled_input(hover)
  if not target_hint.visible or target_hint.text != expected:
   push_error("Expected movement hover label '%s', got '%s'" % [expected, target_hint.text])
   return false
  print("TACTICAL_MOVE_HOVER_OK ", expected)
 return true


func refresh_target_hint(screen_point: Vector2) -> void:
 target_hint.text = ""
 target_hint.hide()
 target_line.hide()
 if playing_events or mailbox.pending:
  return
 var id := actor_at(screen_point, "enemy:")
 if id.is_empty():
  var ground: Variant = ground_under_cursor(screen_point)
  if ground is Vector3 and actor_at(screen_point, "ally:").is_empty():
   var cell := ground_cell(ground)
   var selected := unit_state(selected_ally)
   if not selected.is_empty() and not same_cell(cell, selected.get("cell", [])) and (
    cell[0] >= 0 and cell[0] < 40 and cell[1] >= 0 and cell[1] < 28
   ):
    var moves: Array = selected.get("moves", [])
    var covered: Array = selected.get("covered_moves", [])
    if contains_cell(covered, cell):
     target_hint.text = "Move to cover"
    elif contains_cell(moves, cell):
     target_hint.text = "Move"
    else:
     target_hint.text = "Cannot move here"
    target_hint.show()
  return
 var enemy := unit_state(id)
 var targets: Dictionary = unit_state(selected_ally).get("targeting", {})
 var context: Dictionary = targets.get(id, {}).get(attack_mode, {})
 var label := "Action unavailable"
 if not context.is_empty():
  if not context.in_range:
   label = "Out of range"
  elif context.line_blocked:
   label = "Line blocked"
  elif not context.can_pay:
   label = "Insufficient AP"
  else:
   label = "%d%% hit chance" % int(context.hit_percent)
   var origin := target_center(actors[selected_ally])
   var endpoint := target_center(actors[id])
   var axis := endpoint-origin
   target_line.position = (origin+endpoint)/2
   target_line.quaternion = Quaternion(Vector3.UP, axis.normalized())
   target_line.scale.y = axis.length()
   target_line.show()
 target_hint.show()
 target_hint.text = "%s  //  %s  //  %s" % [enemy.name, attack_mode.capitalize(), label]


func refresh_selection() -> void:
 var active: TacticalActor = actors[selected_ally]
 cutaway.actors = [] if active.fallen else [active]
 var selected := unit_state(selected_ally)
 var moves: Array = selected.get("moves", [])
 var covered: Array = selected.get("covered_moves", [])
 for index in move_markers.size():
  var marker := move_markers[index]
  marker.visible = index < moves.size()
  if marker.visible:
   marker.position = cell_position(moves[index]) + Vector3.UP*.07
   marker.material_override = cover_move_material if moves[index] in covered else open_move_material
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


func ground_cell(ground: Vector3) -> Array:
 return [floori(ground.x + 20), floori(14 - ground.z)]


func ground_under_cursor(screen_point: Vector2) -> Variant:
 return Plane(Vector3.UP, 0).intersects_ray(
  review_camera.project_ray_origin(screen_point), review_camera.project_ray_normal(screen_point))


func _unhandled_input(event: InputEvent) -> void:
 if closing:
  return
 if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
  close_battlefield()
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
   update_control_hints()
 if event is InputEventMouseMotion:
  refresh_target_hint(event.position)
 elif event is InputEventKey:
  refresh_target_hint(get_viewport().get_mouse_position())
 if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_RIGHT:
  fire_at(event.position)
 if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
  var ally := actor_at(event.position, "ally:")
  if not ally.is_empty() and not playing_events and not mailbox.pending:
   selected_ally = ally
   refresh_selection()
   refresh_target_hint(get_viewport().get_mouse_position())
   return
  var ground: Variant = ground_under_cursor(event.position)
  if ground is Vector3:
   send({"action": "move", "actor": selected_ally,
    "destination": ground_cell(ground)})
