extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var board=load("res://scripts/visual_battlefield.gd").new()
	var legacy=load("res://scripts/battlefield.gd").new()
	root.add_child(board);root.add_child(legacy)
	var layout=load("res://scripts/map_wall_layout.gd")
	var assets:=ProjectSettings.globalize_path("res://../../assets/maps")
	var count:=0
	for filename: String in DirAccess.get_files_at(assets):
		if not filename.ends_with(".walls.json"):continue
		var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(assets.path_join(filename)))
		var covers: Array[Dictionary]=layout.cover_nodes(data)
		var tex:=PlaceholderTexture2D.new()
		var dimensions: Array=data.get("image_size",[7680,4320])
		tex.size=Vector2(dimensions[0],dimensions[1])
		board.configure(Vector2(5120,2880),tex,covers,Vector2i(20,14))
		legacy.configure(Vector2(5120,2880),null,covers,Vector2i(20,14))
		assert(board._blocked==legacy._blocked and board._opaque_cells==legacy._opaque_cells,filename+": collision/LOS data identical")
		var x_scale: float=board._u_axis.length()/tex.size.x
		var y_scale: float=board._v_axis.length()/tex.size.y
		assert(is_equal_approx(x_scale,y_scale),filename+": equal source pixel axis scales")
		for row in range(28):
			for col in range(40):
				var cell:=Vector2i(col,row)
				assert(board.world_to_cell(board.cell_to_world(cell))==cell,filename+": cell picking inverse")
		var first: Vector2i=board.nearest_open_cell(Vector2i(5,5))
		var last: Vector2i=board.nearest_open_cell(Vector2i(30,20))
		assert(board.find_path(first,last)==legacy.find_path(first,last),filename+": same route/AP distance")
		assert(board.has_los(first,last)==legacy.has_los(first,last),filename+": same LOS")
		assert(board.reachable_cells(first,4)==legacy.reachable_cells(first,4),filename+": same reachable cells")
		for wall: Dictionary in data.get("walls",[]):
			if wall.get("outline_uv",[]).size()<3:continue
			var prop=load("res://scripts/visual_obstacle.gd").new()
			root.add_child(prop)
			prop.configure(wall,board,null)
			assert(prop.height==0 and prop.top==prop.ground,filename+": no fabricated extrusion")
			for i in range(prop.top.size()):
				var uv:=Vector2(wall.outline_uv[i][0],wall.outline_uv[i][1])
				assert((prop.position+prop.top[i]).distance_to(board.uv_to_world(uv))<.01,filename+": cap UV exactly joins source")
			prop.free()
		count+=1
	assert(count==122)
	board.free();legacy.free()
	print("COMBAT_21_CATALOG_PASSED ",count)
	quit()
