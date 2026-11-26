extends "res://storefront197.gd"
func load_glb(relative: String,place: Vector3) -> Node3D:
 if relative=="showcase174/environment.glb":relative="showcase198/environment.glb"
 return super.load_glb(relative,place)
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"art198/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 print("ART198_READY market materials and conflicting dressing cleanup")

func update_camera(t: float) -> void:
 super.update_camera(t)
 if t<27:return
 # Keep the end orbit over the actual map instead of exposing the void below
 # its finite painted floor. Still rotate and exercise building occlusion.
 var blend:=smoothstep(27,29,t)
 var focus:=Vector3(-.5,.65,1)
 var yaw:=deg_to_rad(40+(t-27)*22)
 var destination:=focus+Vector3(sin(yaw)*22,15,cos(yaw)*22)
 camera.position=camera.position.lerp(destination,blend)
 camera.look_at(focus)
 camera.size=lerpf(camera.size,14,blend)
