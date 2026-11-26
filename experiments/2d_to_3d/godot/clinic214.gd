extends "res://recovery213.gd"
func load_glb(relative: String,place: Vector3) -> Node3D:
 if relative=="showcase174/environment.glb":relative="showcase214/environment.glb"
 var model:=super.load_glb(relative,place)
 if relative.begins_with("showcase") and relative.ends_with("/environment.glb"):
  # Register the thicker service-light assemblies with the existing cutaway
  # pass before combat169 builds its occlusion bounds/material list.
  for group in model.find_children("Street211_LightAssembly*","Node3D",true,false):
   group.name="Occludable_"+str(group.name)
 return model
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"clinic214/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 print("CLINIC214_READY camera-facing authored clinic service facade")
