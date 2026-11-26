extends "res://cyber207.gd"
func load_glb(relative: String,place: Vector3) -> Node3D:
 if relative=="showcase174/environment.glb":relative="showcase208/environment.glb"
 return super.load_glb(relative,place)
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"district208/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 print("DISTRICT208_READY industrial facade finish and clinic advertising")
