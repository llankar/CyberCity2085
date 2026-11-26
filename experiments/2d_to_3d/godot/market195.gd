extends "res://gait194.gd"
## Same encounter and tactical volumes; dressed market counters and clinic identity.
func load_glb(relative: String,place: Vector3) -> Node3D:
	if relative=="showcase174/environment.glb":relative="showcase195/environment.glb"
	var model=super.load_glb(relative,place)
	if relative=="vtol_finish135/vtol_actions.glb":model.position.y=3.8
	return model
func _ready() -> void:
	super._ready()
	delivery_folder=ROOT+"market195/";DirAccess.make_dir_recursive_absolute(delivery_folder)
	print("MARKET195_READY seven dressed counters; original tactical cells retained")
