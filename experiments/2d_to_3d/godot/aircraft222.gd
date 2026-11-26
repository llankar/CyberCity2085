extends "res://aircraft221.gd"
func aircraft_path() -> String:
 return "vtol222/vtol_actions.glb"
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"aircraft222/"
 DirAccess.make_dir_recursive_absolute(delivery_folder)
 print("AIRCRAFT222_READY generated inner fan geometry animated; no gear transfer")
