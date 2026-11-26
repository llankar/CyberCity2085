extends "res://counter219.gd"
## Static aircraft art comparison only. Existing vehicle178 remains animated.
func model_bounds(model: Node3D) -> AABB:
 var result:=AABB()
 var first:=true
 for mesh in model.find_children("*","MeshInstance3D",true,false):
  var box: AABB=mesh.global_transform*mesh.get_aabb()
  result=box if first else result.merge(box)
  first=false
 return result
func aircraft_path() -> String:
 return "paint220/stealth_vtol/review/optimized.glb"
func load_glb(relative: String,place: Vector3) -> Node3D:
 if relative!="vtol_finish135/vtol_actions.glb":return super.load_glb(relative,place)
 var original:=super.load_glb(relative,place)
 var old_bounds:=model_bounds(original)
 var candidate:=super.load_glb(aircraft_path(),place)
 candidate.rotation.y=PI/2
 var initial_bounds:=model_bounds(candidate)
 var ratio:=old_bounds.size.x/initial_bounds.size.x
 candidate.scale*=ratio
 var fitted:=model_bounds(candidate)
 candidate.global_position+=old_bounds.get_center()-fitted.get_center()
 original.free()
 print("AIRCRAFT_ART_PREVIEW path=",aircraft_path()," width=",old_bounds.size.x," scale=",ratio)
 return candidate
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"aircraft221/"
 DirAccess.make_dir_recursive_absolute(delivery_folder)
func update_camera(t: float) -> void:
 super.update_camera(t)
 # Brief establishing shot includes the aircraft before normal action framing.
 var establishing:=1.0-smoothstep(1.5,3.5,t)
 camera.position+=Vector3(-1,0,-3)*establishing
 camera.size=lerpf(camera.size,24.5,establishing)
