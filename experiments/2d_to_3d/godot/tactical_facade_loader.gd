extends RefCounted

static func load_model(parent: Node3D,source_path: String,expected_cells: int) -> Node3D:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/tactical_facades01/"
	var report = JSON.parse_string(FileAccess.get_file_as_string(folder+"geometry_report.json"))
	assert(report is Dictionary and int(report.source_cells)==expected_cells)
	assert(str(report.source_sha256)==FileAccess.get_sha256(source_path))
	assert(str(report.glb_sha256)==FileAccess.get_sha256(folder+"facades.glb"))
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	assert(doc.append_from_file(folder+"facades.glb",state)==OK)
	var model := doc.generate_scene(state)
	parent.add_child(model)
	assert(model.find_children("*","MeshInstance3D",true,false).size()==int(report.meshes))
	print("TACTICAL_FACADE_MODEL_LOADED cells=",expected_cells," meshes=",report.meshes)
	return model
