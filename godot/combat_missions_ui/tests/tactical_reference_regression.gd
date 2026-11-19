extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var board = load("res://scripts/visual_battlefield.gd").new()
	root.add_child(board)
	board.top_down=false # Preserve the explicit isometric fallback contract.
	var empty: Array[Dictionary] = []
	board.configure(Vector2(5120,2880),null,empty,Vector2i(20,14))
	var route: Array[Vector2i] = [Vector2i(10,10),Vector2i(11,10),Vector2i(11,11),Vector2i(12,11)]
	board.show_path(route)
	var preview: Dictionary = board._route_preview_geometry()
	assert(preview["cost"]==3,"actual AP cost, not decorative waypoints")
	assert(board.path_cells==route,"preview never moves tactical cells")
	assert(preview["points"][1]==board.cell_to_world(route[1]),"real path centers")
	var center: Vector2 = board.cell_to_world(route[-1])
	var tip: Vector2 = preview["arrow"][0]
	var offset := (tip-center).abs()
	assert(is_equal_approx(offset.x/(board.iso_tw*board.DESTINATION_SCALE)+offset.y/(board.iso_th*board.DESTINATION_SCALE),1.0),"arrow ends at destination boundary")
	for zoom in [0.4,0.9,2.0]:
		board.scale = Vector2.ONE*zoom
		assert(is_equal_approx(board._screen_unit()*zoom,1.0),"constant screen stroke")
	var no_path: Array[Vector2i] = []
	board.show_path(no_path)
	assert(board._route_preview_geometry().is_empty(),"cleared path hides arrow and AP badge")
	var mission = load("res://scripts/combat_mission_ui.gd").new()
	mission._battlefield = board
	mission._camera = Camera2D.new()
	for viewport in [Vector2(1280,720),Vector2(1920,1080),Vector2(2560,1440)]:
		mission.size = viewport
		board.configure(viewport*4,null,empty,Vector2i(20,14))
		var initial: float = mission._overview_zoom()
		assert(is_equal_approx(initial*board.iso_tw*2.0,200.0*clampf(viewport.y/941.0,.75,1.7)),"reference framing across resolutions")
		mission._camera.zoom = Vector2.ONE*initial
		mission._zoom_at(viewport*0.5,100.0)
		assert(is_equal_approx(mission._camera.zoom.x,mission._close_zoom()),"closer zoom is available")
		mission._zoom_at(viewport*0.5,0.5)
		assert(mission._camera.zoom.x < initial,"zooming out remains possible")
	mission._camera.free()
	mission._camera = null
	mission._battlefield = null
	mission.free()
	var image := Image.create(100,100,false,Image.FORMAT_RGBA8)
	image.fill(Color.TRANSPARENT)
	image.fill_rect(Rect2i(30,20,40,80),Color.WHITE)
	var unit = load("res://scripts/unit_visual.gd").new()
	root.add_child(unit)
	unit.setup({"hp":7,"max_hp":24},0,false,ImageTexture.create_from_image(image),Vector2(400,400))
	assert(is_equal_approx(unit._body_height(),400*0.70*1.10),"ten percent larger body without moving grid cells")
	for zoom in [0.4,0.9,2.0]:
		unit.scale = Vector2.ONE*zoom
		var bar: Rect2 = unit._health_bar_rect()
		var body: Rect2 = unit._visible_body_rect()
		assert(is_equal_approx(bar.size.y*zoom,6.0),"six-pixel health bar")
		assert(is_equal_approx((body.position.y-bar.end.y)*zoom,8.0),"bar anchors above visible head, not transparent margins")
		assert(bar.size.x*zoom>=47.9 and bar.size.x*zoom<=108.1,"readable health width")
	var fills: Array[float] = unit._health_segment_fills()
	assert(fills.size()==4 and fills[0]==1 and is_equal_approx(fills[1],1.0/6.0) and fills[2]==0,"partial segment reflects real HP")
	unit.unit_data["hp"]=-9
	assert(unit._health_segment_fills()==[0.0,0.0,0.0,0.0],"negative HP clamped")
	unit.unit_data["hp"]=500
	assert(unit._health_segment_fills()==[1.0,1.0,1.0,1.0],"overheal clamped")
	var atlas_image := Image.create(200,100,false,Image.FORMAT_RGBA8)
	atlas_image.fill(Color.TRANSPARENT)
	atlas_image.fill_rect(Rect2i(30,20,40,80),Color.WHITE)
	atlas_image.fill_rect(Rect2i(130,40,40,60),Color.WHITE)
	var frame_bounds: Dictionary = unit._measure_atlas_bounds(atlas_image,Vector2i(100,100))
	assert(is_equal_approx(frame_bounds[0].position.y,0.2) and is_equal_approx(frame_bounds[1].position.y,0.4),"animated frames retain their own visible head bounds")
	var audio = load("res://scripts/audio_manager.gd").new()
	root.add_child(audio)
	var sound := AudioStreamWAV.new()
	sound.mix_rate = 8000
	var data := PackedByteArray()
	data.resize(32000)
	sound.data = data
	audio._streams["synthetic"] = sound
	audio.configure_soundtrack({"battle_music_path":"synthetic","start_position":1.25})
	await process_frame
	assert(audio._music_player.get_playback_position()>=1.2,"handoff resumes music position")
	audio.configure_soundtrack({"battle_music_path":"synthetic","start_position":0.0})
	assert(audio._music_player.get_playback_position()>=1.2,"same soundtrack does not restart")
	audio.free()
	unit.free()
	board.free()
	await process_frame
	print("TACTICAL_REFERENCE_CHECKS_PASSED")
	quit()
