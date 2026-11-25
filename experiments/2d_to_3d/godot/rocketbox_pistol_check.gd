extends Node3D
func _ready() -> void:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03/motion01/"
	var authored_study := "--unvanquished-study" in OS.get_cmdline_user_args()
	if authored_study:root="E:/CyberCity2085-3d-lab/generated/phase2/unvanquished_weapon01/"
	var reference = JSON.parse_string(FileAccess.get_file_as_string(root+"pistol_fit01/weapon_surface_reference.json"))
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var combined := "--combined-model" in OS.get_cmdline_user_args() or authored_study
	assert(doc.append_from_file(root+("pistol_fit01/human_pistol.glb" if combined else "human_motion.glb"),state) == OK)
	var model := doc.generate_scene(state,120 if authored_study else 30,false,false)
	add_child(model); model.position = Vector3(.7,0,-1.3)
	var prop: Node3D
	if not combined: prop = preload("res://rocketbox_pistol_attachment.gd").attach(model)
	var rig := model.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var player := model.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var meshes := model.find_children("EquippedPistol_*", "MeshInstance3D", true, false) if combined else prop.find_children("*", "MeshInstance3D", true, false)
	assert(meshes.size() == 9 and reference.size() == 9)
	if authored_study:
		assert(rig.get_bone_count()==122 and model.find_children("*","MeshInstance3D",true,false).size()==30)
		assert(player.get_animation_list().size()==1)
	player.play("Pistol_Attack_Study" if authored_study else "Pistol_Shoot")
	var skin_probe := preload("res://skin_motion_check.gd").new()
	var worst := 0.0
	for sample in reference:
		player.seek(float(sample.time_s),true); rig.force_update_all_bone_transforms()
		if not combined: (prop.get_parent() as BoneAttachment3D).on_skeleton_update()
		var actual := PackedVector3Array()
		for node in meshes:
			var mesh := node as MeshInstance3D
			if combined:
				actual.append_array(skin_probe.skinned_points(mesh,rig,1))
				continue
			for surface in range(mesh.mesh.get_surface_count()):
				for vertex in mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]: actual.append(mesh.global_transform * vertex)
		var expected := PackedVector3Array()
		for name in sample.parts:
			for vertex in sample.parts[name]: expected.append(Vector3(vertex[0],vertex[2],-vertex[1])+model.position)
		for pair in [[actual,expected],[expected,actual]]:
			for point in pair[0]:
				var nearest := INF
				for target in pair[1]: nearest = minf(nearest,point.distance_to(target))
				worst = maxf(worst,nearest)
	print("ROCKETBOX_PISTOL_BIND_ERROR ",worst)
	assert(worst < 0.001, "Native weapon differs from measured Blender fit")
	skin_probe.free()
	var output := FileAccess.open(root+"pistol_fit01/"+("native_combined_check.json" if combined else "native_check.json"),FileAccess.WRITE)
	output.store_string(JSON.stringify({"glb_sha256":FileAccess.get_sha256(root+"pistol_fit01/human_pistol.glb") if combined else null,"weapon_parts":9,"times":9,"bidirectional_surface_error_m":worst,"nonzero_actor_placement":true,"contact_acceptance":false,"source_game_parity_accepted":false},"  "))
	print("UNV_COMBINED_PISTOL_OK" if authored_study else ("ROCKETBOX_COMBINED_PISTOL_OK" if combined else "ROCKETBOX_PISTOL_BIND_OK"))
	get_tree().quit(0)
