extends SceneTree

const ASSET := "vehicle_aerial_military_01_vtol_gunship"

func _initialize() -> void:
	call_deferred("_check")

func _check() -> void:
	var scene = load("res://scenes/combat_mission_ui.tscn").instantiate()
	root.add_child(scene)
	await process_frame
	var token = scene._unit_tokens.get("v0")
	assert(token != null and token.visual_key == ASSET and token.atlas != null)
	assert(token.unit_id >= 1000 and token.unit_data["ap"] == 0)
	var ground: Vector2 = token.position
	token.set_process(false)
	scene._banner.hide()
	scene._camera.zoom = Vector2.ONE * scene._close_zoom()
	scene._camera.position = ground - Vector2(0, token._body_height() * 0.4)
	scene._camera.force_update_scroll()
	for direction in range(8):
		token.facing = direction
		for phase in range(2):
			token.frame_time = 0.5 * phase
			token._process(0.0)
			token.queue_redraw()
			await process_frame
			await RenderingServer.frame_post_draw
			assert(token.clip == "idle" and token.frame_index == phase)
			assert(token._art_sprite.texture == token.atlas and token.position == ground)
	var args := OS.get_cmdline_user_args()
	if args.size() == 3:
		assert(root.get_texture().get_image().save_png(args[2]) == OK)
	print("PARKED_VTOL_ANIMATION_PASSED")
	quit()
