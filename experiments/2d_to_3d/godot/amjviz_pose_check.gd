extends Node3D
## Static FK study: verify actual body plus nine real weapon-part surfaces.

func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/amjviz_combat146/"
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(folder+"shoot_equipped.glb",state)==OK)
	var model := document.generate_scene(state,24,false,false)
	add_child(model)
	var rig := model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	assert(rig.get_bone_count()==262)
	rig.force_update_all_bone_transforms()
	var meshes := {}
	for mesh in model.find_children("*","MeshInstance3D",true,false):
		meshes[str(mesh.name).replace(".","_").replace(" ","_")]=mesh
	var references: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(folder+"equipped_pose_reference.json"))
	assert(meshes.size()==10 and references.size()==10)
	var probe := preload("res://skin_motion_check.gd").new()
	var checker := preload("res://cyborg_ready_check.gd").new()
	var result: Dictionary = checker.compare_sample(meshes,rig,probe,references)
	probe.free();checker.free()
	var report := {"glb_sha256":FileAccess.get_sha256(folder+"shoot_equipped.glb"),
		"reference_sha256":FileAccess.get_sha256(folder+"equipped_pose_reference.json"),
		"meshes":meshes.size(),"bones":rig.get_bone_count(),"maximum_bound_error_m":result.error,
		"floor_m":result.floor,"scope":"One static FK shooting pose; body/weapon export bounds, not contacts/art/full animation"}
	var file := FileAccess.open(folder+"native_equipped_pose.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "));file.close()
	if result.error>=.0005:
		push_error("Static equipped-pose export mismatch: %s"%result.error);get_tree().quit(1);return
	print("AMJVIZ_EQUIPPED_POSE_NATIVE_PASS meshes=10 bones=262 error_m=",result.error)
	get_tree().quit()
