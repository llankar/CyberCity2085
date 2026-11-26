extends "res://neural176.gd"
## Presentation pass: continuous tactical overview and action framing.
func _ready() -> void:
	super._ready()
	delivery_folder=ROOT+("visible185/" if "--visible185" in OS.get_cmdline_user_args() else "assemblies184/" if "--assemblies184" in OS.get_cmdline_user_args() else "district183/" if "--district183" in OS.get_cmdline_user_args() else "presentation182/")
	DirAccess.make_dir_recursive_absolute(delivery_folder)

func update_camera(t: float) -> void:
	var focus:=Vector3(-.5,.7,1)
	var size_value:=17.0
	# Broader gunfight framing retains both sides and the crate in view.
	var action:=smoothstep(2,4,t)*(1-smoothstep(11,12,t))
	size_value=lerpf(size_value,12,action)
	focus=focus.lerp(Vector3(-.5,.7,1.1),action)
	# Move in for the approach/melee, then retain caster and target for PSI.
	var melee:=smoothstep(12,14,t)*(1-smoothstep(16,17,t))
	size_value=lerpf(size_value,7.5,melee)
	focus=focus.lerp(Vector3(.7,.7,1.5),melee)
	var psychic:=smoothstep(17,17.5,t)*(1-smoothstep(20.5,21.5,t))
	size_value=lerpf(size_value,10,psychic)
	focus=focus.lerp(Vector3(-1.5,.7,1),psychic)
	var treatment:=smoothstep(21,23,t)*(1-smoothstep(27,30,t))
	size_value=lerpf(size_value,7.5,treatment)
	focus=focus.lerp(Vector3(-.2,.65,1.7),treatment)
	var yaw:=deg_to_rad(40+12*sin(t*.1))
	camera.position=focus+Vector3(sin(yaw)*22,lerpf(17,10,treatment),cos(yaw)*22)
	camera.look_at(focus)
	camera.size=size_value

	# End with a low orbit that visibly exercises building occlusion.
	var reveal:=smoothstep(27,29,t)
	var low_focus:=Vector3(-.5,.3,1)
	var low_yaw:=deg_to_rad(35+20*sin(t*.12))
	camera.position=camera.position.lerp(low_focus+Vector3(sin(low_yaw)*28,5,cos(low_yaw)*28),reveal)
	camera.look_at(focus.lerp(low_focus,reveal))
	camera.size=lerpf(size_value,20,reveal)
