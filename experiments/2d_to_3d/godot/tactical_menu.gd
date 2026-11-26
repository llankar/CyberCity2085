extends Control

var directory: String
var status: Label


func _ready() -> void:
 directory = OS.get_environment("CYBERCITY_TACTICAL_SESSION")
 var background := ColorRect.new()
 background.color = Color(.024,.04,.055)
 add_child(background)
 background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 var center := CenterContainer.new()
 add_child(center)
 center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 var options := VBoxContainer.new()
 options.custom_minimum_size.x = 560
 options.add_theme_constant_override("separation", 14)
 center.add_child(options)
 var heading := Label.new()
 heading.text = "CYBERCITY 2085  //  3D SKIRMISH"
 heading.add_theme_color_override("font_color", Color(.25,.86,1))
 heading.add_theme_font_size_override("font_size", 32)
 options.add_child(heading)
 status = Label.new()
 status.text = "Choose a battlefield"
 status.add_theme_font_size_override("font_size", 20)
 options.add_child(status)
 var manifest := JSON.new()
 if manifest.parse(FileAccess.get_file_as_string(directory.path_join("scenarios.json"))) != OK:
  status.text = "Launch this menu with run_tactical_preview.py"
  return
 var search := LineEdit.new()
 search.placeholder_text = "Filter battlefields by name"
 search.clear_button_enabled = true
 search.custom_minimum_size.y = 44
 options.add_child(search)
 var scroll := ScrollContainer.new()
 scroll.custom_minimum_size.y = 425
 scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
 scroll.follow_focus = true
 options.add_child(scroll)
 var cards := VBoxContainer.new()
 cards.size_flags_horizontal = Control.SIZE_EXPAND_FILL
 cards.add_theme_constant_override("separation", 8)
 scroll.add_child(cards)
 var smoke_button: Button
 for map: Dictionary in manifest.data.maps:
  var id: String = map.id
  var button := Button.new()
  button.text = str(map.title)
  button.custom_minimum_size.y = 58
  button.add_theme_font_size_override("font_size", 24)
  button.pressed.connect(_select.bind(id))
  cards.add_child(button)
  if id == "metro":
   smoke_button = button
 search.text_changed.connect(func(query: String) -> void:
  var words := query.strip_edges().to_lower().split(" ", false)
  var visible_count := 0
  for button: Button in cards.get_children():
   var title := button.text.to_lower()
   button.visible = true
   for word in words:
    if not title.contains(word):
     button.visible = false
     break
   visible_count += int(button.visible)
  scroll.scroll_vertical = 0
  status.text = "No matching battlefields"
  if visible_count == 1:
   status.text = "1 battlefield"
  elif visible_count > 1:
   status.text = "%d battlefields" % visible_count
 )
 var quit := Button.new()
 quit.text = "Exit"
 quit.custom_minimum_size.y = 44
 quit.pressed.connect(get_tree().quit)
 options.add_child(quit)
 if cards.get_child_count() > 0:
  cards.get_child(0).grab_focus()
 if OS.get_environment("CYBERCITY_TACTICAL_SMOKE") == "1" and smoke_button != null:
  await get_tree().process_frame
  search.text = "metro interchange"
  search.text_changed.emit(search.text)
  if not smoke_button.visible or status.text != "1 battlefield":
   push_error("Battlefield filter did not isolate Metro Interchange")
   get_tree().quit(18)
   return
  smoke_button.pressed.emit()


func _select(id: String) -> void:
 var scene := "res://tactical_battlefield.tscn"
 var destination := directory.path_join("map-selection.txt")
 var temporary := destination + ".tmp"
 var file := FileAccess.open(temporary, FileAccess.WRITE)
 if file == null:
  status.text = "Could not start the battle session."
  return
 file.store_string(id)
 file.close()
 if DirAccess.rename_absolute(temporary, destination) != OK:
  status.text = "Could not publish the selected battlefield."
  return
 print("TACTICAL_MENU_SELECTED map=", id)
 status.text = "Loading battlefield…"
 var error := get_tree().change_scene_to_file(scene)
 if error != OK:
  push_error("Could not open battlefield: %s" % error_string(error))
  get_tree().quit(1)


func _unhandled_key_input(event: InputEvent) -> void:
 if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
  get_tree().quit()
