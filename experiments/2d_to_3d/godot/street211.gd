extends "res://finish210.gd"
func load_glb(relative: String,place: Vector3) -> Node3D:
 if relative=="showcase174/environment.glb":relative="showcase211/environment.glb"
 return super.load_glb(relative,place)
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"street211/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 for mesh in find_children("Lamp211_Emitter*","MeshInstance3D",true,false):
  var light:=OmniLight3D.new();light.name="Street211_LocalLight";add_child(light)
  light.global_position=mesh.global_position-Vector3(0,.16,0)
  light.light_color=Color(.12,.72,.8);light.light_energy=.65;light.omni_range=3.8
 print("STREET211_READY angular lights and retained authored service vent")
