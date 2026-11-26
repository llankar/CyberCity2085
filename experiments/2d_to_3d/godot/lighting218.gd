extends "res://industry216.gd"
## Local lighting follows the authored shop emitters, retaining tactical fill.
var shop_lights: Array[Dictionary] = []
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"lighting218/"
 DirAccess.make_dir_recursive_absolute(delivery_folder)
 for node in get_children():
  if node is DirectionalLight3D:node.light_energy=.95
  if node is WorldEnvironment:node.environment.ambient_light_energy=.5
 for mesh in find_children("Kiosk207_LuminousValance*","MeshInstance3D",true,false):
  var material=mesh.get_active_material(0)
  if not material is StandardMaterial3D:continue
  var lamp:=OmniLight3D.new()
  lamp.name="Shop218_Practical"
  add_child(lamp)
  lamp.global_position=mesh.global_transform*mesh.get_aabb().get_center()+Vector3(0,-.18,0)
  lamp.light_color=material.emission
  lamp.light_energy=.9
  lamp.omni_range=4.5
  lamp.omni_attenuation=1.6
  # Small source radius softens the transition on nearby curved armor.
  lamp.light_size=.22
  shop_lights.append({"source":mesh,"lamp":lamp})
 print("LIGHTING218_READY practical shop emitters: ",shop_lights.size())
func _process(delta: float) -> void:
 super._process(delta)
 for pair in shop_lights:
  var source=pair.source as MeshInstance3D
  var material=source.get_active_material(0) as StandardMaterial3D
  # The cutaway already controls the source alpha. Hidden signs cast no light.
  pair.lamp.light_energy=.9*material.albedo_color.a if source.is_visible_in_tree() else 0.0
