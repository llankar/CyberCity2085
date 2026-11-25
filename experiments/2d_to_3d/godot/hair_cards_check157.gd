extends Node3D
## Actual candidate body preservation across source clips; not hair artistic approval.
func _ready() -> void:
	var root:="E:/CyberCity2085-3d-lab/generated/phase2/"
	var actors:Array[Node3D]=[]
	for path in [root+"face_review156/human_face035.glb",root+"hair_cards157/human.glb"]:
		var doc:=GLTFDocument.new();var state:=GLTFState.new()
		assert(doc.append_from_file(path,state)==OK)
		var model:=doc.generate_scene(state,120,false,false);add_child(model);actors.append(model)
	var players:Array[AnimationPlayer]=[];var rigs:Array[Skeleton3D]=[];var bodies:Array[MeshInstance3D]=[]
	for model in actors:
		players.append(model.find_children("*","AnimationPlayer",true,false)[0])
		rigs.append(model.find_children("*","Skeleton3D",true,false)[0])
		assert(rigs[-1].get_bone_count()==262)
		for mesh in model.find_children("*","MeshInstance3D",true,false):
			if str(mesh.name)=="Character":bodies.append(mesh)
	assert(bodies.size()==2 and players[0].get_animation_list()==players[1].get_animation_list())
	var probe:=preload("res://skin_motion_check.gd").new();var worst:=0.;var cases:=0
	for clip in players[0].get_animation_list():
		for fraction in [0.,.5,1.]:
			var bounds:Array[AABB]=[]
			for i in range(2):
				players[i].play(clip);players[i].seek(players[i].current_animation_length*fraction,true);players[i].pause();rigs[i].force_update_all_bone_transforms()
				var points:PackedVector3Array=probe.skinned_points(bodies[i],rigs[i],8)
				assert(not points.is_empty());var box:=AABB(points[0],Vector3.ZERO)
				for point in points:assert(point.is_finite());box=box.expand(point)
				bounds.append(box)
			worst=maxf(worst,maxf(bounds[0].position.distance_to(bounds[1].position),bounds[0].end.distance_to(bounds[1].end)));cases+=1
			print("HAIR_BODY_SAMPLE ",clip," fraction=",fraction," boxes=",bounds)
			await get_tree().process_frame
	assert(worst<.0005,"Body changed while fitting hair")
	var output:=FileAccess.open(root+"hair_cards157/native_body.json",FileAccess.WRITE)
	output.store_string(JSON.stringify({"samples":cases,"body_bounds_max_error_m":worst,"glb_sha256":FileAccess.get_sha256(root+"hair_cards157/human.glb"),"scope":"21 sampled body bounds, not full hair deformation/contact/art"},"  "));output.close();probe.free()
	print("HAIR157_NATIVE_BODY_PASS samples=",cases," error_m=",worst);get_tree().quit()
