extends Control
## Independent environment selector. No campaign or alternative combat engine.
const CATALOG := preload("res://preproduction_catalog.json")
func _ready() -> void:
 var backdrop:=ColorRect.new()
 backdrop.color=Color(.025,.045,.065)
 backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 add_child(backdrop)
 var scroll := ScrollContainer.new()
 scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 scroll.offset_left=32
 scroll.offset_top=24
 scroll.offset_right=-32
 scroll.offset_bottom=-24
 add_child(scroll)
 var box:=VBoxContainer.new()
 box.size_flags_horizontal=Control.SIZE_EXPAND_FILL
 box.add_theme_constant_override("separation",18)
 scroll.add_child(box)
 var heading:=Label.new()
 heading.text="CYBERCITY 2085 // ENVIRONMENT LAB"
 heading.add_theme_font_size_override("font_size",32)
 box.add_child(heading)
 var caption:=Label.new()
 var available := 0
 for entry in CATALOG.data:
  if entry.has("scene"):available += 1
 caption.text="%d environment previews available. %d conversions planned." % [available, CATALOG.data.size()-available]
 box.add_child(caption)
 var buttons:Array[Button]=[]
 for entry in CATALOG.data:
  var button:=Button.new()
  var scene_path := str(entry.get("scene",""))
  var label := str(entry.map).replace("_"," ").capitalize()
  button.text=label if not scene_path.is_empty() else label+" // Planned"
  if entry.has("scope"):button.text+=" // "+str(entry.scope)
  button.custom_minimum_size=Vector2(0,52)
  button.add_theme_font_size_override("font_size",24)
  button.disabled=scene_path.is_empty()
  box.add_child(button)
  buttons.append(button)
  if not button.disabled:
   button.pressed.connect(func():assert(get_tree().change_scene_to_file(scene_path)==OK))
 if "--menu-smoke" in OS.get_cmdline_user_args():
  await get_tree().process_frame
  if get_tree().has_meta("environment_menu_returned"):
   print("ENVIRONMENT_MENU_ROUNDTRIP_PASS")
   get_tree().quit()
  else:
   get_tree().set_meta("environment_menu_test",true)
   var index:=4
   for argument in OS.get_cmdline_user_args():
    if argument.begins_with("--review-index="):index=int(argument.get_slice("=",1))
   assert(index>=0 and index<buttons.size() and not buttons[index].disabled)
   buttons[index].pressed.emit()
