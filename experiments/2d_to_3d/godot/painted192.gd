extends "res://materials186.gd"
## Separate full encounter trial using the existing painted, now articulated robot.
func load_glb(relative: String, place: Vector3) -> Node3D:
	if relative=="security_opaque137/robot_actions.glb":relative="robot191/robot_actions.glb"
	return super.load_glb(relative,place)
func _ready() -> void:
	super._ready()
	delivery_folder=ROOT+"painted192/"
	DirAccess.make_dir_recursive_absolute(delivery_folder)
	for name_value in ["Idle","Walk","Melee","Hit","Death"]:assert(players[2].has_animation(name_value))
	print("PAINTED192_READY actual painted articulated robot; death tracks=",players[2].get_animation("Death").get_track_count())
	if "--wreck-review" in OS.get_cmdline_user_args():
		set_process(false);review_wreck.call_deferred()
func muzzle_position(source: int) -> Vector3:
	if source==2:return actors[2].to_global(Vector3(-.65,1.9,.35))
	return super.muzzle_position(source)
var recoil_end := 0.0
func fire(source: int,target_index: int) -> void:
	super.fire(source,target_index)
	if source==2:
		clip(2,"Idle");recoil_end=time_value+.18
func travel(index: int,from: Vector3,to: Vector3,start: float,end: float,walk: String,t: float) -> void:
	super.travel(index,from,to,start,end,walk,t)
	if index==2:
		if t<20:actors[2].rotation.x=.035*maxf(0,(recoil_end-t)/.18)
		if t>=17.5 and t<20:face(2,actors[3].position)
		if t>=20:
			actors[2].position.z=-.2+1.25*smoothstep(20,21.1,t)
			actors[2].position.y=.025

		if frame==630:print("PAINTED192_FALL_STATE ",players[2].current_animation," ",players[2].current_animation_position," actor= ",actors[2].rotation)

func review_wreck() -> void:
	var probe:=preload("res://skin_motion_check.gd").new()
	var rig:=actors[2].find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	var reports:=[]
	camera.size=8;camera.position=Vector3(6,7,10);camera.look_at(Vector3(0,.4,1))
	for item in [["current",.723],["toward_caster",-1.13]]:
		actors[2].position=Vector3(-1,.025,1.05);actors[2].rotation=Vector3(0,float(item[1]),0)
		players[2].play("Death");players[2].seek(1.5,true);players[2].advance(0);rig.force_update_all_bone_transforms()
		var minimum:=INF;var inside:=0;var count:=0
		for mesh in actors[2].find_children("*","MeshInstance3D",true,false):
			for point in probe.skinned_points(mesh,rig,16,true):
				minimum=minf(minimum,point.y);inside+=int(crate_bounds.has_point(point));count+=1
		reports.append({"pose":item[0],"sampled_min_y":minimum,"sampled_vertices_inside_crate":inside,"samples":count})
		await RenderingServer.frame_post_draw;await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(delivery_folder+"wreck_review_"+item[0]+".png")
	probe.free();FileAccess.open(delivery_folder+"wreck_review.json",FileAccess.WRITE).store_string(JSON.stringify(reports))
	print("PAINTED192_WRECK_REVIEW ",reports);get_tree().quit()
