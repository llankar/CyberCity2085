extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	root.size=Vector2i(800,450)
	var board=load("res://scripts/visual_battlefield.gd").new()
	root.add_child(board);board.quality=0
	var empty: Array[Dictionary]=[]
	var cell:=Vector2i(20,14)
	for color: Color in [Color(.06,.07,.08),Color(.72,.64,.52),Color(.28,.32,.34)]:
		var source:=Image.create(1,1,false,Image.FORMAT_RGB8);source.fill(color)
		board.configure(Vector2(800,450),ImageTexture.create_from_image(source),empty,Vector2i(1,1))
		board.move_range_cells.clear();board.queue_redraw()
		await process_frame;await RenderingServer.frame_post_draw
		var before:=root.get_texture().get_image()
		board.move_range_cells.assign([cell]);board.queue_redraw()
		await process_frame;await RenderingServer.frame_post_draw
		var after:=root.get_texture().get_image()
		var center: Vector2i=Vector2i(board.cell_to_world(cell))
		var visible:=0
		for y in range(center.y-6,center.y+7):
			for x in range(center.x-7,center.x+8):
				var a:=before.get_pixel(x,y);var b:=after.get_pixel(x,y)
				if absf(a.r-b.r)+absf(a.g-b.g)+absf(a.b-b.b)>.22:visible+=1
		assert(visible>=25,"reachable cell must stand out against light and dark terrain")
		assert(board.move_range_cells==[cell] and board._blocked.is_empty(),"visibility changes never alter reachable cells or collisions")
	board.free()
	print("MOVEMENT_VISIBILITY_CHECKS_PASSED")
	quit()
