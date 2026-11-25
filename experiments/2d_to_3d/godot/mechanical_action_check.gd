extends RefCounted
## Native articulated geometry checks, separate from artistic acceptance.

func verify_strike(actor: Node3D) -> void:
	var player := actor.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	assert(player.has_animation("Melee"))
	player.play("Melee")
	var animation := player.get_animation("Melee")
	assert(animation.loop_mode == Animation.LOOP_NONE)
	var skeleton := actor.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var hand: MeshInstance3D
	for candidate in actor.find_children("*", "MeshInstance3D", true, false):
		if str(candidate.name).replace(".", "_").replace("-", "_") == "GEO_hand_joint_L_Evaluated": hand = candidate
	assert(hand != null)
	var probe := preload("res://skin_motion_check.gd").new()
	var positions: Array[Vector3] = []
	for time_s in [0.0, 0.5, animation.length]:
		player.seek(time_s, true)
		skeleton.force_update_all_bone_transforms()
		positions.append(probe.skinned_points(hand, skeleton, 1)[0])
	assert(positions[0].distance_to(positions[1]) > 0.6, "Hand did not perform the actual strike")
	assert(positions[0].distance_to(positions[2]) < 0.0001, "Strike did not recover to rest")
	probe.free()
	print("MECHANICAL_STRIKE_STAGE_OK reach=", positions[0].distance_to(positions[1]), " recovered=true")
