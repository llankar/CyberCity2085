extends RefCounted
## Inspection-only framing and compact evidence for the independent 3D stage.
var stage
var initial_target:Vector3
var initial_size:float
var initial_yaw:float
var initial_elevation:float
var initial_orbit:bool
var sources:Dictionary
var enabled:=false
var caption:Label

func configure(owner_stage,paths:Dictionary) -> void:
	stage=owner_stage;sources=paths
	initial_target=stage.target;initial_size=stage.camera.size
	initial_yaw=stage.yaw;initial_elevation=stage.elevation;initial_orbit=stage.orbit_mode

func frame(key:String) -> bool:
	if "--sprite-review" in OS.get_cmdline_user_args():return false
	assert(key in ["human","robot","pair"])
	if key=="pair":
		stage.target=(stage.subjects[0].position+stage.subjects[1].position)*.5+Vector3.UP*.9
		stage.camera.size=6.2
	else:
		var index:=0 if key=="human" else 1
		var height:float=stage.human_height if index==0 else stage.robot_height
		stage.target=stage.subjects[index].position+Vector3.UP*height*.5
		stage.camera.size=4.2
	stage.update_camera();return true

func restore() -> void:
	stage.target=initial_target;stage.camera.size=initial_size
	stage.yaw=initial_yaw;stage.elevation=initial_elevation;stage.orbit_mode=initial_orbit;stage.update_camera()

func toggle_hud() -> void:
	stage.hud.visible=not stage.hud.visible

func apply_args() -> void:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--review-frame="):
			assert(frame(argument.trim_prefix("--review-frame=")),"Calibrated sprite review must retain its camera")
			enabled=true
	if "--clean-capture" in OS.get_cmdline_user_args():
		stage.hud.hide();enabled=true
	if enabled:
		caption=Label.new();caption.text="EXPERIMENTAL 3D / NOT FINAL ART   |   F focus selected   G overview   H diagnostics"
		caption.add_theme_font_size_override("font_size",13)
		caption.position=Vector2(16,stage.get_viewport().get_visible_rect().size.y-28)
		stage.hud.get_parent().add_child(caption)

func verify_inputs() -> void:
	if "--sprite-review" in OS.get_cmdline_user_args():return
	var previous:int=stage.selected
	var key:=InputEventKey.new();key.pressed=true
	for index in range(2):
		stage.selected=index;key.keycode=KEY_F;stage._unhandled_input(key)
		assert(is_equal_approx(stage.camera.size,4.2))
		var height:float=stage.human_height if index==0 else stage.robot_height
		assert(stage.target.distance_to(stage.subjects[index].position+Vector3.UP*height*.5)<.0001)
	stage.yaw+=.2;stage.elevation+=.1
	key.keycode=KEY_G;stage._unhandled_input(key)
	assert(stage.target==initial_target and is_equal_approx(stage.camera.size,initial_size))
	assert(stage.yaw==initial_yaw and stage.elevation==initial_elevation and stage.orbit_mode==initial_orbit)
	var visible:bool=stage.hud.visible
	key.keycode=KEY_H;stage._unhandled_input(key);assert(stage.hud.visible!=visible)
	stage._unhandled_input(key);assert(stage.hud.visible==visible)
	stage.selected=previous
	print("REVIEW163_INPUT_PASS focus_human,focus_robot,overview,diagnostics_toggle")

func write_capture_proof(path:String) -> void:
	if not enabled:return
	var models:Dictionary={}
	for key in sources:models[key]={"path":sources[key],"sha256":FileAccess.get_sha256(sources[key])}
	var output:=FileAccess.open(path+".json",FileAccess.WRITE);assert(output!=null)
	output.store_string(JSON.stringify({"capture_sha256":FileAccess.get_sha256(path),"models":models,
		"camera_size":stage.camera.size,"target":[stage.target.x,stage.target.y,stage.target.z],
		"yaw":stage.yaw,"elevation":stage.elevation,"diagnostics_visible":stage.hud.visible,
		"render_texture_size":[stage.get_viewport().get_texture().get_width(),stage.get_viewport().get_texture().get_height()],
		"projected_human_reference_height_px":absf(stage.camera.unproject_position(stage.subjects[0].position+Vector3.UP*stage.human_height).y-stage.camera.unproject_position(stage.subjects[0].position).y),
		"sprite_review":"--sprite-review" in OS.get_cmdline_user_args(),"overview":"--overview" in OS.get_cmdline_user_args(),
		"scope":"Actual stage framing only; unchanged geometry/materials/lights, NOT final art acceptance"},"  "));output.close()
