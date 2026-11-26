extends "res://art198.gd"
func load_glb(relative: String,place: Vector3) -> Node3D:
 if relative=="showcase174/environment.glb":relative="showcase199/environment.glb"
 return super.load_glb(relative,place)
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"roof199/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 print("ROOF199_READY three distinct rooftop identities")

func update_camera(t: float) -> void:
 super.update_camera(t)
 if "--roof-review" in OS.get_cmdline_user_args():
  camera.position=Vector3(-26,24,20);camera.look_at(Vector3(0,.5,0));camera.size=32
func capture() -> void:
 super.capture()
 if "--roof-review" in OS.get_cmdline_user_args() and frame==90:
  get_viewport().get_texture().get_image().save_png(delivery_folder+"roof_overview.png")
  print("ROOF199_OVERVIEW_CAPTURED")
  get_tree().quit()
