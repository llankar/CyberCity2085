extends RefCounted
## Reuse the licensed prop and measured rest grip with the shared character rig.

static func yup(values: Array) -> Vector3:
	return Vector3(values[0], values[2], -values[1])

static func attach(model: Node3D) -> Node3D:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/"
	var metadata = JSON.parse_string(FileAccess.get_file_as_string(root + "einar_pistol_fit01_surfaces/fit_report.json"))
	assert(metadata is Dictionary)
	var skeleton := model.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var joint := -1
	for index in range(skeleton.get_bone_count()):
		if str(skeleton.get_bone_name(index)).get_slice("_", 0) == str(metadata.joint).get_slice("_", 0): joint = index
	assert(joint >= 0)
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(root + "firewarden_pistol01/pistol.glb", state) == OK)
	var weapon := document.generate_scene(state) as Node3D
	var forward := yup(metadata.weapon_forward_rest).normalized()
	var up := yup(metadata.weapon_up_rest).normalized()
	var basis := Basis(up.cross(forward).normalized(), up, forward)
	assert(absf(basis.determinant() - 1) < 0.0001)
	var placement := Transform3D(basis, yup(metadata.rest_grip_world) - basis * yup(metadata.weapon_source_grip_anchor))
	var attachment := BoneAttachment3D.new()
	attachment.name = "MeasuredPistolWristAttachment"
	attachment.bone_name = skeleton.get_bone_name(joint)
	skeleton.add_child(attachment)
	attachment.add_child(weapon)
	weapon.transform = skeleton.get_bone_global_rest(joint).affine_inverse() * placement
	attachment.on_skeleton_update()
	return weapon
