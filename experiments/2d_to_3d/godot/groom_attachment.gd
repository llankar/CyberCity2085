extends RefCounted
## Static authored neutral groom follows the actual head joint; no jaw rig claim.
static func enable_vertex_palette(groom: Node3D) -> void:
	for mesh in groom.find_children("*", "MeshInstance3D", true, false):
		for surface in range(mesh.mesh.get_surface_count()):
			var colors: PackedColorArray = mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_COLOR]
			assert(not colors.is_empty(), "Authored groom palette missing")
			var material := mesh.get_active_material(surface).duplicate() as StandardMaterial3D
			assert(material != null)
			material.vertex_color_use_as_albedo = true
			# glTF COLOR_0 contains linear RGB; applying sRGB decoding twice is wrong.
			material.vertex_color_is_srgb = false
			mesh.set_surface_override_material(surface, material)

static func attach(model: Node3D, folder: String = "einar_groom_occlusion03") -> Node3D:
	assert(folder in ["einar_groom02", "einar_groom_full02", "einar_groom_full02_layered", "einar_groom_occlusion03", "einar_groom02_layered_lod"])
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/" + folder + "/"
	var metadata = JSON.parse_string(FileAccess.get_file_as_string(root + "groom_report.json"))
	assert(metadata is Dictionary)
	var skeleton := model.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var joint := -1
	for index in range(skeleton.get_bone_count()):
		if str(skeleton.get_bone_name(index)).get_slice("_", 0) == str(metadata.head_joint).get_slice("_", 0): joint = index
	assert(joint >= 0)
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(root + "authored_groom.glb", state) == OK)
	var groom := document.generate_scene(state) as Node3D
	enable_vertex_palette(groom)
	var attachment := BoneAttachment3D.new()
	attachment.name = "AuthoredGroomHeadAttachment"
	attachment.bone_name = skeleton.get_bone_name(joint)
	skeleton.add_child(attachment); attachment.add_child(groom)
	groom.transform = skeleton.get_bone_global_rest(joint).affine_inverse()
	attachment.on_skeleton_update()
	return groom
