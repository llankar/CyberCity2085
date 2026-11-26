extends "res://medic209.gd"
var sensor_materials:Array[Dictionary]=[]
func load_glb(relative: String,place: Vector3) -> Node3D:
 if relative=="security_opaque137/robot_actions.glb":relative="robot210/robot_actions.glb"
 return super.load_glb(relative,place)
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"finish210/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 for mesh in actors[2].find_children("*","MeshInstance3D",true,false):
  for surface in mesh.mesh.get_surface_count():
   var mat:=mesh.get_active_material(surface) as StandardMaterial3D
   if mat and mat.emission_enabled:sensor_materials.append({"material":mat,"energy":mat.emission_energy_multiplier})
 assert(not sensor_materials.is_empty())
 print("FINISH210_READY heavy robot metal/sensors; existing animations and medic helmet")
func _process(delta: float) -> void:
 super._process(delta)
 for entry in sensor_materials:
  entry.material.emission_energy_multiplier=entry.energy*(1-smoothstep(20,21,time_value))
