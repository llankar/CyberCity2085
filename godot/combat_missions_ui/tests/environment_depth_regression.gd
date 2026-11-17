extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var model = load("res://scripts/environment_depth.gd")
	var board = load("res://scripts/visual_battlefield.gd").new()
	root.add_child(board)
	var empty: Array[Dictionary]=[]
	board.configure(Vector2(5120,2880),null,empty,Vector2i(20,14))
	var source := Image.create(128,128,false,Image.FORMAT_RGBA8)
	source.fill(Color(.2,.25,.3,1))
	var texture := ImageTexture.create_from_image(source)
	var depth = model.new()
	depth.prepare(texture,board)
	var polygon: PackedVector2Array = model.rect_uv(Rect2(.3,.3,.4,.4))
	var floor: Dictionary=depth.floor_patch(polygon)
	var filled: Image=floor.texture.get_image()
	var sample: Color=filled.get_pixel(filled.get_width()/2,filled.get_height()/2)
	assert(depth.floor_patch(polygon).texture==floor.texture,"floor patches are cached across rebuilds")
	assert(model.material_texture("fabric")==model.material_texture("fabric"),"material textures are shared")
	assert(absf(sample.r-.2)<.04 and absf(sample.g-.25)<.04 and absf(sample.b-.3)<.04, "floor completion preserves surrounding color, no white holes")
	assert(depth.floor_patch(polygon).texture==floor.texture,"floor completion cached across viewport rebuilds")
	assert(texture.get_image().get_data()==source.get_data(),"original source never mutated")
	var probe=load("res://scripts/visual_obstacle.gd").new()
	root.add_child(probe)
	probe.configure({"id":"test_crate","outline_uv":[[.3,.3],[.5,.3],[.5,.5],[.3,.5]]},board,texture,depth)
	var probe_face: Dictionary=probe.parts[0].faces[0]
	var midpoint: Vector2=probe.position
	for point: Vector2 in probe_face.points: midpoint+=point*.25
	var bodies: Array[Rect2]=[Rect2(midpoint-Vector2(3,6),Vector2(6,12))]
	probe.update_occlusion_for_units(bodies)
	assert(probe.fade,"raised side geometry fades for an occluded unit")
	bodies=[Rect2(Vector2(100000,100000),Vector2(10,10))]
	probe.update_occlusion_for_units(bodies)
	assert(not probe.fade,"unrelated props stay opaque")
	probe.free()
	var assets:=ProjectSettings.globalize_path("res://../../assets/maps")
	var layout=load("res://scripts/map_wall_layout.gd")
	var count:=0
	var raised:=0
	for filename: String in DirAccess.get_files_at(assets):
		if not filename.ends_with(".walls.json"):continue
		var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(assets.path_join(filename)))
		var before:=JSON.stringify(data)
		var covers: Array[Dictionary]=layout.cover_nodes(data)
		var tex:=PlaceholderTexture2D.new()
		var dimensions: Array=data.get("image_size",[7680,4320])
		tex.size=Vector2(dimensions[0],dimensions[1])
		board.configure(Vector2(5120,2880),tex,covers,Vector2i(20,14))
		var blocked: Array[Vector2i]=board._blocked.duplicate()
		depth=model.new();depth.prepare(tex,board)
		for wall: Dictionary in data.walls:
			if wall.get("outline_uv",[]).size()<3:continue
			var prop=load("res://scripts/visual_obstacle.gd").new()
			root.add_child(prop)
			prop.configure(wall,board,tex,depth)
			assert(prop.height>=0 and prop.height<=board.iso_tw*2*.91,"human-scale bounded relief")
			for i in range(prop.ground.size()):
				var uv:=Vector2(wall.outline_uv[i][0],wall.outline_uv[i][1])
				assert((prop.position+prop.ground[i]).distance_to(board.uv_to_world(uv))<.01,"footprint remains exactly surveyed")
			if prop.height>0:
				raised+=1
				assert(not prop.parts.is_empty())
				for part: Dictionary in prop.parts:
					assert(part.cap.size()==part.uvs.size())
					for i in range(part.cap.size()):
						var expected: Vector2=board.uv_to_world(part.uvs[i])-prop.position
						assert(is_equal_approx(part.cap[i].x,expected.x),"roof projection stays aligned")
						assert(part.cap[i].y<=expected.y,"positive elevation only")
					for face: Dictionary in part.faces:
						assert(face.points.size()==4 and face.uvs.size()==4)
						assert(part.material!=tex,"facades have dedicated materials, not stretched source roofs")
				if model.profile(wall).kind=="table" and prop.uvs.size()==4: assert(prop.parts.size()==5,"separate tabletop and four legs")
			prop.free()
		assert(board._blocked==blocked and JSON.stringify(data)==before,"no tactical or survey mutations")
		count+=1
	assert(count==122 and raised>1000)
	board.free()
	print("ENVIRONMENT_DEPTH_CHECKS_PASSED ",count," maps; ",raised," volumes")
	quit()
