extends SceneTree
## Presentation invariants; existing action regression covers real combat rules.
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var lighting = load("res://scripts/visual_lighting.gd")
	var board = load("res://scripts/visual_battlefield.gd").new()
	var empty: Array[Dictionary] = []
	board.configure(Vector2(5120,2880),null,empty,Vector2i(20,14))
	root.add_child(board)
	var image := Image.create(96,54,false,Image.FORMAT_RGBA8)
	image.fill(Color(.03,.04,.05))
	for index in range(16):
		image.fill_rect(Rect2i(3+(index%8)*12,3+(index/8)*25,5,5),Color(0.1,.85,1))
	var texture := ImageTexture.create_from_image(image)
	var glow = lighting.new()
	root.add_child(glow)
	for pair in [["rain","city_exterior_neon_market_alley.png","city"],["interior","city_interior_blacksite_lab.png","interior"],["rain","city_industrial_factory_floor.png","industrial"],["dust","wasteland_outdoor_01.png","wasteland"]]:
		glow.configure(texture,board,pair[0],pair[1])
		assert(glow.profile==pair[2], "environment profile")
		assert(glow.points.size()>0 and glow.points.size()<=12, "bounded lights from actual source pixels")
		var first: Array[Dictionary] = glow.points.duplicate(true)
		glow.configure(texture,board,pair[0],pair[1])
		assert(glow.points==first, "reconfiguration reuses samples without duplicates")
		assert(glow.glow==lighting.glow_texture(), "shared soft texture")
	assert(texture.get_image().get_data()==image.get_data(), "source pixels remain untouched")
	var unit = load("res://scripts/unit_visual.gd").new()
	root.add_child(unit)
	unit.setup({"hp":20,"max_hp":24},0,true,texture,Vector2(180,180))
	var height: float = unit._body_height()
	var body: Rect2 = unit._visible_body_rect()
	for level in range(3):
		unit.visual_quality=level
		unit.queue_redraw()
		assert(unit._body_height()==height and unit._visible_body_rect()==body, "quality never changes body dimensions")
	assert(is_equal_approx(height,180*.70*1.10), "2.1 character size retained")
	var route: Array[Vector2i] = [Vector2i(5,5),Vector2i(6,5),Vector2i(7,5),Vector2i(7,6)]
	board.show_path(route)
	for dimensions in [Vector2(1280,720),Vector2(1920,1080),Vector2(2560,1440)]:
		board.configure(dimensions*4,null,empty,Vector2i(20,14))
		for zoom in [.4,1.0,2.0]:
			board.scale=Vector2.ONE*zoom
			board.show_path(route)
			assert(board._route_preview_geometry().cost==3, "route decoration retains true AP cost")
			for cell: Vector2i in route: assert(board.world_to_cell(board.cell_to_world(cell))==cell)
	var hud = load("res://scripts/visual_hud.gd").new()
	for viewport in [Vector2(1280,720),Vector2(1920,1080),Vector2(2560,1440)]:
		hud.fit_viewport(viewport)
		var fitted: String = hud._fit("LONG AGENT NAME AND EQUIPMENT",90,18)
		assert(ThemeDB.fallback_font.get_string_size(fitted,HORIZONTAL_ALIGNMENT_LEFT,-1,18).x<=90, "ellipsis fits inside its panel")
		var panel: Rect2 = hud._target_panel_rect(Vector2(hud.size.x-10,hud.size.y-10))
		assert(Rect2(Vector2.ZERO,hud.size).encloses(panel), "target panel stays on screen at every resolution")
		var bottom_pixel: Vector2 = hud.get_global_transform_with_canvas()*Vector2(hud.size.x*.5,hud.size.y-10)
		assert(hud.blocks_map_input(bottom_pixel), "HUD gaps cannot fire at units behind the footer")
	assert(hud._hover_box("MOVE",Color.CYAN,.5)==hud._hover_box("MOVE",Color.CYAN,.9), "hover style resources are reused")
	hud.free()
	var fx = load("res://scripts/combat_visual_fx.gd").new()
	root.add_child(fx)
	for level in range(3):
		fx.quality=level
		for index in range(100): fx.burst("explosion",Vector2(10,10),Vector2(100,100))
		assert(fx.effects.size()<=fx.LIMIT, "effect cap includes secondary smoke")
		fx._process(4.0)
		assert(fx.effects.is_empty() and not fx.is_processing(), "completed effects release redraw work")
	fx.free();unit.free();glow.free();board.free()
	print("COMBAT_POLISH_CHECKS_PASSED")
	quit()
