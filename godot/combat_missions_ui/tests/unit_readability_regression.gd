extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	root.size = Vector2i(400,240)
	var backdrop := ColorRect.new()
	backdrop.color = Color(0.12,0.10,0.08)
	backdrop.size = Vector2(400,240)
	root.add_child(backdrop)
	var image := Image.create(64,64,false,Image.FORMAT_RGBA8)
	image.fill(Color.TRANSPARENT)
	image.fill_rect(Rect2i(10,10,44,44),Color(0.16,0.22,0.28,0.45))
	var texture := ImageTexture.create_from_image(image)
	var unit = load("res://scripts/unit_visual.gd").new()
	root.add_child(unit)
	unit.position = Vector2(280,180)
	unit.setup({"hp":24,"max_hp":24},0,false,texture,Vector2(400,400))
	var raw := Sprite2D.new()
	raw.texture = texture
	raw.centered = false
	raw.position = Vector2(80-unit._body_height()/2,180-unit._body_height())
	raw.scale = Vector2.ONE*unit._body_height()/64
	root.add_child(raw)
	await process_frame
	await RenderingServer.frame_post_draw
	var capture := root.get_texture().get_image()
	var background := capture.get_pixel(200,117)
	var original := capture.get_pixel(80,117)
	var enhanced := capture.get_pixel(280,117)
	assert(enhanced.r>original.r+0.05 and enhanced.g>original.g+0.08 and enhanced.b>original.b+0.1,"solid, brighter art must separate from terrain")
	assert(absf(enhanced.r-0.239)<0.025 and absf(enhanced.b-0.374)<0.025,"source alpha must not fade the living body")
	assert(absf(background.r-0.12)<0.01,"transparent margins must preserve terrain")
	assert(unit._art_sprite.texture==texture and unit._art_sprite.region_rect==Rect2(0,0,64,64),"static source and frame geometry preserved")
	# The same material must follow atlas animation frames without changing size.
	var atlas_image := Image.create(128,64,false,Image.FORMAT_RGBA8)
	atlas_image.fill(Color.TRANSPARENT)
	atlas_image.blit_rect(image,Rect2i(0,0,64,64),Vector2i(64,0))
	unit.atlas = ImageTexture.create_from_image(atlas_image)
	unit.manifest = {"frame_size":[64,64],"animations":{"idle":{"rows":[[1],[1],[1],[1],[1],[1],[1],[1]],"fps":8,"loop":true}}}
	unit.queue_redraw()
	await process_frame
	await RenderingServer.frame_post_draw
	capture = root.get_texture().get_image()
	var animated := capture.get_pixel(280,117)
	assert(absf(animated.r-enhanced.r)<0.01 and absf(animated.b-enhanced.b)<0.01,"animated and static bodies have matching opacity and lighting")
	assert(unit._art_sprite.region_rect==Rect2(64,0,64,64),"atlas frame selection remains exact")
	# Every living unit has a colored outline before selection or targeting.
	var ally_edge := capture.get_pixel(236,117)
	assert(ally_edge.g>ally_edge.r+0.15,"unselected ally must have a clear cyan outline")
	unit.is_enemy = true
	unit.queue_redraw()
	await process_frame
	await RenderingServer.frame_post_draw
	var enemy_edge := root.get_texture().get_image().get_pixel(236,117)
	assert(enemy_edge.r>enemy_edge.g+0.15,"untargeted enemy must have a clear red outline")
	assert(not unit.is_active and not unit.is_targeted,"outline is independent of selection")
	unit.is_enemy = false
	unit.set_active(true)
	await process_frame
	await RenderingServer.frame_post_draw
	assert(unit._art_material.get_shader_parameter("focus_strength")==1.0,"active silhouette uses cyan emphasis without body transparency")
	assert(unit.modulate.a==1.0,"selection never pulses body opacity")
	unit.set_active(false)
	unit.is_enemy = true
	unit.set_targeted(true)
	await process_frame
	await RenderingServer.frame_post_draw
	assert(unit._art_material.get_shader_parameter("focus_strength")==1.0,"targeted enemy receives silhouette emphasis")
	var rim: Color = unit._art_material.get_shader_parameter("rim_color")
	assert(rim.r>rim.b,"enemy silhouette uses red, not ally cyan")
	var body: Rect2 = unit._visible_body_rect()
	assert(unit._target_frame_rect().get_center().is_equal_approx(body.get_center()),"brackets center on visible art")
	unit.unit_data["hp"] = 0
	unit.queue_redraw()
	await process_frame
	await RenderingServer.frame_post_draw
	assert(not unit._art_sprite.visible,"dead unit without death clip stays hidden")
	print("UNIT_READABILITY_CHECKS_PASSED")
	quit()
