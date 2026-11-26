extends Control
## Independent environment selector. No campaign or alternative combat engine.
const ENTRIES := [
 ["NEON MARKET // retained environment", "res://market251.tscn"],
 ["RESIDENTIAL // reconstruction pending", ""],
 ["RESEARCH LAB // work in progress", "res://laboratory248.tscn"],
 ["FACTORY // partial reconstruction", "res://factory249.tscn"],
 ["SUBWAY // first assembly", "res://metro250.tscn"],
 ["WASTELAND // reconstruction pending", ""]
]
func _ready() -> void:
 var backdrop:=ColorRect.new()
 backdrop.color=Color(.025,.045,.065)
 backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 add_child(backdrop)
 var box:=VBoxContainer.new()
 box.position=Vector2(420,140)
 box.add_theme_constant_override("separation",18)
 add_child(box)
 var heading:=Label.new()
 heading.text="CYBERCITY 2085 // ENVIRONMENT LAB"
 heading.add_theme_font_size_override("font_size",32)
 box.add_child(heading)
 var caption:=Label.new()
 caption.text="Experimental art review. Combat integration and artistic completion remain open."
 box.add_child(caption)
 var buttons:Array[Button]=[]
 for entry in ENTRIES:
  var button:=Button.new()
  button.text=entry[0]
  button.custom_minimum_size=Vector2(1080,75)
  button.add_theme_font_size_override("font_size",24)
  button.disabled=str(entry[1]).is_empty()
  box.add_child(button)
  buttons.append(button)
  if not button.disabled:
   button.pressed.connect(func():assert(get_tree().change_scene_to_file(entry[1])==OK))
 if "--menu-smoke" in OS.get_cmdline_user_args():
  await get_tree().process_frame
  if get_tree().has_meta("environment_menu_returned"):
   print("ENVIRONMENT_MENU_ROUNDTRIP_PASS")
   get_tree().quit()
  else:
   get_tree().set_meta("environment_menu_test",true)
   assert(not buttons[4].disabled)
   buttons[4].pressed.emit()
