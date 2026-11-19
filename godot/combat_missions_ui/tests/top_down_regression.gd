extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var board=load("res://scripts/visual_battlefield.gd").new()
	var unit=load("res://scripts/unit_visual.gd").new()
	root.add_child(board);root.add_child(unit)
	var profiles=load("res://scripts/map_presentation.gd")
	var layout=load("res://scripts/map_wall_layout.gd")
	var directory:=ProjectSettings.globalize_path("res://../../assets/maps")
	var count:=0
	for filename: String in DirAccess.get_files_at(directory):
		if not filename.ends_with(".walls.json"):continue
		var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(directory.path_join(filename)))
		var covers: Array[Dictionary]=layout.cover_nodes(data)
		var tex:=PlaceholderTexture2D.new()
		tex.size=Vector2(data.image_size[0],data.image_size[1])
		board.human_height_ratio=profiles.human_height_ratio({"path":data.image})
		for resolution: Vector2 in [Vector2(1280,720),Vector2(1920,1080),Vector2(2560,1440)]:
			board.configure(resolution*4,tex,covers,Vector2i(20,14))
			assert(board.top_down and board._u_axis.y==0 and board._v_axis.x==0,"source orientation preserved")
			assert(is_equal_approx(board._u_axis.length()/tex.size.x,board._v_axis.length()/tex.size.y),"no image stretching")
			unit.cell_size=Vector2.ONE*board.iso_tw*2
			unit.terrain_scale=board.token_terrain_scale()
			assert(is_equal_approx(unit._body_height()/board.source_rect.size.x,board.human_height_ratio),"token/map art scale survives resolution changes")
			for y in range(28):
				for x in range(40):
					var cell:=Vector2i(x,y)
					assert(board.world_to_cell(board.cell_to_world(cell))==cell)
			for wall: Dictionary in data.walls:
				for pair: Array in wall.get("outline_uv",[]):
					var uv:=Vector2(pair[0],pair[1])
					var expected: Vector2=board.source_rect.position+uv*board.source_rect.size
					assert(board.uv_to_world(uv).distance_to(expected)<.01,"all obstacle vertices stay on source art")
			var points: PackedVector2Array=board._iso_corners(Vector2i(18,14))
			assert(is_zero_approx(points[1].y-points[0].y) and is_zero_approx(points[2].x-points[1].x),"top-view cell outlines match projection")
		count+=1
	assert(count==122)
	assert(is_equal_approx(profiles.human_height_ratio({"path":"cybercity_inner_02_safehouse.png"}),.02),"reviewed interior profile")
	assert(is_equal_approx(profiles.human_height_ratio({"path":"wasteland_outdoor_01_dust_road_ambush.png"}),.015),"reviewed open-wasteland profile")
	assert(profiles.human_height_ratio({"path":"unknown.png","presentation":{"human_height_ratio":.075}})==.075)
	board.top_down=false
	var covers: Array[Dictionary]=[]
	board.configure(Vector2(5120,2880),null,covers,Vector2i(20,14))
	assert(board._u_axis.y>0 and board._v_axis.x<0 and board.token_terrain_scale()==1.0,"old isometric renderer remains available")
	unit.free();board.free()
	print("TOP_DOWN_CHECKS_PASSED 122 maps, three resolutions, source walls and scale")
	quit()
