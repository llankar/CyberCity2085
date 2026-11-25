extends RefCounted
## Genuine source hair cards in fitted neutral world space, mounted to the head.
static func attach(model: Node3D) -> Node3D:
	var rig := model.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var bone := rig.find_bone("Bip01 Head")
	assert(bone >= 0)
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	assert(doc.append_from_file("E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_hair08/fitted_hair.glb",state)==OK)
	var hair := doc.generate_scene(state) as Node3D
	for mesh in hair.find_children("*", "MeshInstance3D", true, false):
		var material := mesh.get_active_material(0).duplicate() as StandardMaterial3D
		material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
		material.alpha_scissor_threshold = .4
		material.cull_mode = BaseMaterial3D.CULL_DISABLED
		material.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
		var image := material.albedo_texture.get_image()
		image.generate_mipmaps()
		material.albedo_texture = ImageTexture.create_from_image(image)
		mesh.set_surface_override_material(0,material)
	var mount := BoneAttachment3D.new()
	mount.name = "AuthoredQuiffHeadMount"; mount.bone_name = "Bip01 Head"
	rig.add_child(mount); mount.add_child(hair)
	hair.transform = (rig.global_transform * rig.get_bone_global_rest(bone)).affine_inverse()*model.global_transform
	mount.on_skeleton_update()
	for mesh in model.find_children("*", "MeshInstance3D", true, false):
		for surface in range(mesh.mesh.get_surface_count()):
			var material := mesh.get_active_material(surface) as StandardMaterial3D
			if material and material.resource_name=="sm004_helmet":
				var hidden := material.duplicate() as StandardMaterial3D
				hidden.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA; hidden.albedo_color.a=0
				mesh.set_surface_override_material(surface,hidden)
	return hair
