extends Node3D
## Real imported skinned baseline versus rigid socket, with live model reuse.
func key(value: String) -> String:
	return value.trim_prefix("EquippedPistol_").replace(".","_").replace(" ","_")

func bounds(points: PackedVector3Array) -> AABB:
	assert(not points.is_empty())
	var result:=AABB(points[0],Vector3.ZERO)
	for point in points:result=result.expand(point)
	return result

func _ready() -> void:
	var folder:="E:/CyberCity2085-3d-lab/generated/phase2/amjviz_modules153/"
	var path:="E:/CyberCity2085-3d-lab/generated/phase2/amjviz_wardrobe150/human_actions.glb"
	var document:=GLTFDocument.new();var state:=GLTFState.new()
	assert(document.append_from_file(path,state)==OK)
	var model:=document.generate_scene(state,120,false,false) as Node3D;add_child(model)
	var rig:=model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	var player:=model.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	var body: MeshInstance3D
	var largest:=0
	for mesh in model.find_children("*","MeshInstance3D",true,false):
		var vertices:=0
		for surface in range(mesh.mesh.get_surface_count()):vertices+=mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX].size()
		if vertices>largest:largest=vertices;body=mesh
	assert(largest>10000)
	var body_id:=body.get_instance_id();var mesh_id:=body.mesh.get_instance_id();var rig_id:=rig.get_instance_id()
	player.play("ShootStudy");player.seek(38./120.,true);player.pause()
	var modules:=preload("res://equipment_modules153.gd").new();modules.configure(model,path)
	assert(player.assigned_animation=="ShootStudy" and not player.is_playing() and absf(player.current_animation_position-38./120.)<.000001)
	var others:={}
	for mesh in modules.variants.firewarden.find_children("*","MeshInstance3D",true,false):others[key(str(mesh.name))]=mesh
	assert(others.size()==9)
	var initial_nodes:=model.find_children("*","Node",true,false).size()
	var probe:=preload("res://skin_motion_check.gd").new()
	var worst:=0.;var cases:=0
	for clip in player.get_animation_list():
		for fraction in [0.,.5,1.]:
			player.play(clip);player.seek(player.get_animation(clip).length*fraction,true);player.pause()
			rig.force_update_all_bone_transforms();modules.attachment.on_skeleton_update()
			for old in modules.originals:
				assert(others.has(key(str(old.name))),"Original prop part missing in external module")
				var other: MeshInstance3D=others[key(str(old.name))]
				var points:=PackedVector3Array()
				for surface in range(other.mesh.get_surface_count()):
					for vertex in other.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:points.append(other.global_transform*vertex)
				var first:=bounds(probe.skinned_points(old,rig,1));var second:=bounds(points)
				worst=maxf(worst,maxf(first.position.distance_to(second.position),first.end.distance_to(second.end)))
			for variant in ["p320","firewarden"]:
				modules.choose(variant,clip)
				for name in modules.variants:assert(modules.variants[name].visible==(name==variant and clip=="ShootStudy"))
				for old in modules.originals:assert(not old.visible)
			assert(body.get_instance_id()==body_id and body.mesh.get_instance_id()==mesh_id and rig.get_instance_id()==rig_id)
			assert(model.find_children("*","Node",true,false).size()==initial_nodes)
			cases+=1
	probe.free()
	var report:={"body_glb_sha256":FileAccess.get_sha256(path),"modules_sha256":FileAccess.get_sha256(folder+"modules.json"),
		"pose_cases":cases,"variant_swaps":cases*2,"maximum_baseline_part_bounds_error_m":worst,
		"body_mesh_rig_reused":true,"node_count_constant":true,"paused_pose_preserved":true,"body_mesh_name":body.name,"scope":"Native socket transform/bounds and actual visibility swaps; not palm/contact/art or canonical game mapping acceptance"}
	var file:=FileAccess.open(folder+"native_modules.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "));file.close()
	if worst>=.0005:push_error("External baseline module does not match original skin: %s"%worst);get_tree().quit(1);return
	print("REAL_EQUIPMENT_SOCKET_NATIVE_PASS ",JSON.stringify(report));get_tree().quit()
