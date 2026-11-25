extends Node3D
## Test the declared rigid head binding; does not accept facial expression rigs.
func _ready() -> void:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/"
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(root + "einar_bundle02/human_actions.glb", state) == OK)
	var body := document.generate_scene(state, 30, false, false) as Node3D
	add_child(body); body.position = Vector3(2, 0, 3)
	var groom := preload("res://groom_attachment.gd").attach(body, "einar_groom02_layered_lod")
	var attachment := groom.get_parent() as BoneAttachment3D
	var skeleton := body.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var player := body.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var parts := groom.find_children("*", "MeshInstance3D", true, false)
	assert(parts.size() == 4 and attachment.bone_idx >= 0)
	for part in parts:
		var material := part.get_active_material(0) as StandardMaterial3D
		assert(material.vertex_color_use_as_albedo and not material.vertex_color_is_srgb)
	var maximum := 0.0
	var tested := []
	for clip in ["Idle", "Walk", "Pistol_Shoot", "Punch_Cross", "Death01"]:
		assert(player.has_animation(clip))
		player.play(clip); player.advance(0)
		for sample in range(9):
			player.seek(player.get_animation(clip).length * sample / 8.0, true)
			skeleton.force_update_all_bone_transforms(); attachment.on_skeleton_update()
			var expected := skeleton.global_transform * skeleton.get_bone_global_pose(attachment.bone_idx) * skeleton.get_bone_global_rest(attachment.bone_idx).affine_inverse()
			var actual := groom.global_transform
			maximum = maxf(maximum, maxf(actual.origin.distance_to(expected.origin), maxf(actual.basis.x.distance_to(expected.basis.x), maxf(actual.basis.y.distance_to(expected.basis.y), actual.basis.z.distance_to(expected.basis.z)))))
		tested.append(clip)
	assert(maximum < 0.00001)
	var folder := root + "einar_groom02_layered_lod/"
	var output := FileAccess.open(folder + "native_groom_binding.json", FileAccess.WRITE)
	assert(output != null)
	output.store_string(JSON.stringify({"body_sha256": FileAccess.get_sha256(root + "einar_bundle02/human_actions.glb"), "groom_sha256": FileAccess.get_sha256(folder + "authored_groom.glb"), "clips": tested, "times_per_clip": 9, "parts": 4, "max_head_attachment_transform_error": maximum, "scope": "Rigid head attachment and linear vertex-color material routing; no jaw/expression or art acceptance"}, "  "))
	print("AUTHORED_GROOM_HEAD_BINDING_OK ", maximum)
	get_tree().quit(0)
