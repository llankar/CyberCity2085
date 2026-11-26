extends "res://contact204.gd"
func load_glb(relative: String,place: Vector3) -> Node3D:
 if relative=="showcase174/environment.glb":relative="showcase206/environment.glb"
 return super.load_glb(relative,place)
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"facade206/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 print("FACADE206_READY urban bays on two buildings; tactical map unchanged")
