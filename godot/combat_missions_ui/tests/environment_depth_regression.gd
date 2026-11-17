extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var model=load("res://scripts/environment_depth.gd")
	var shapes=load("res://scripts/natural_prop_shapes.gd")
	var catalog=load("res://scripts/environment_catalog.gd")
	var board=load("res://scripts/visual_battlefield.gd").new()
	root.add_child(board)
	var layout=load("res://scripts/map_wall_layout.gd")
	var assets:=ProjectSettings.globalize_path("res://../../assets/maps")
	var count:=0;var authored:=0
	assert(model.profile({"id":"sofa_n"},"unknown.png").height==0,"a furniture name is not a measured silhouette")
	assert(model.profile({"id":"west_wall"},"city_interior_blacksite_lab.png").height==0,"collision walls are not visual mesh specifications")
	for filename: String in DirAccess.get_files_at(assets):
		if not filename.ends_with(".walls.json"):continue
		var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(assets.path_join(filename)))
		var before:=JSON.stringify(data)
		var image_name: String=data.image
		var placeholder:=PlaceholderTexture2D.new()
		var dimensions: Array=data.image_size
		placeholder.size=Vector2(dimensions[0],dimensions[1])
		board.configure(Vector2(5120,2880),placeholder,layout.cover_nodes(data),Vector2i(20,14))
		var blocked=board._blocked.duplicate()
		var depth=model.new();depth.prepare(placeholder,board,image_name)
		for wall: Dictionary in data.walls:
			var uv:=PackedVector2Array()
			for pair in wall.outline_uv:uv.append(Vector2(pair[0],pair[1]))
			var volume: Dictionary=depth.build_volume(wall,uv,Vector2.ZERO)
			assert(volume.parts.is_empty() and volume.floor.is_empty(),"missing source validation always keeps the original 2D scene")
		assert(board._blocked==blocked and JSON.stringify(data)==before,"catalogue navigation/LOS geometry is immutable")
		count+=1
	for image_name: String in catalog.maps():
		var source_path:=assets.path_join(image_name)
		var texture:=ImageTexture.create_from_image(Image.load_from_file(source_path))
		var empty: Array[Dictionary]=[]
		board.configure(Vector2(5120,2880),texture,empty,Vector2i(20,14))
		var depth=model.new();depth.prepare(texture,board,image_name,source_path)
		assert(depth._verified,"reviewed render records match their real source SHA-256")
		var image_hash:=FileAccess.get_sha256(source_path)
		for id: String in catalog.maps()[image_name].props:
			var prop=load("res://scripts/visual_obstacle.gd").new();root.add_child(prop)
			# Deliberately oversized collision: the visual model must ignore it.
			prop.configure({"id":id,"outline_uv":[[.1,.1],[.9,.1],[.9,.9],[.1,.9]]},board,texture,depth)
			assert(prop.height>0 and prop.height<=board.iso_tw*.64,"bounded category-specific human-scale elevation")
			var entry: Dictionary=catalog.maps()[image_name].props[id]
			for part: Dictionary in prop.parts:
				assert(part.cap.size()==part.uvs.size())
				for uv: Vector2 in part.uvs:assert(uv.x>.1 or uv.y>.1,"part UVs come from the authored source object")
			if entry.family=="table":
				assert(prop.parts.size()==5,"a table has four legs and a thin top, no solid platform")
				var tops:=0
				for part: Dictionary in prop.parts:
					if part.role=="top":tops+=1
				assert(tops==1 and prop._contact_shapes.size()==4,"four separate foot contacts; no collision-sized ground platform")
			if entry.family in ["sofa","armchair"]:
				assert(prop.parts.any(func(part):return part.role=="back") and prop.parts.any(func(part):return part.role=="cushion"),"separate upholstered back, seat and arms")
				for part: Dictionary in prop.parts:
					if part.role in ["back","cushion"]:assert(part.get("source_panel",false),"seat surfaces use an actual reviewed upholstery panel, never rug pixels from a collision cap")
			assert(prop._ground_patches.size()==1,"floor completion is clipped to the source object")
			var side: Dictionary=prop.parts[0].faces[0]
			var midpoint: Vector2=prop.position+(side.points[0]+side.points[1]+side.points[2]+side.points[3])*.25
			var bodies: Array[Rect2]=[Rect2(midpoint-Vector2.ONE,Vector2.ONE*2)]
			prop.update_occlusion_for_units(bodies)
			assert(prop.fade,"actual component surfaces fade for an overlapping unit")
			bodies=[Rect2(Vector2(100000,100000),Vector2.ONE*2)]
			prop.update_occlusion_for_units(bodies)
			assert(not prop.fade,"unrelated units do not fade scenery")
			for i in range(prop.ground.size()):
				assert((prop.ground[i]+prop.position).distance_to(board.uv_to_world(prop.uvs[i]))<.01,"visual sorting never changes surveyed world coordinates")
			if entry.family=="table":assert(prop.parts[-1].role=="top","tabletop paints above separate feet")
			if entry.family in ["sofa","armchair"]:
				assert(prop.parts.any(func(part):return part.has("soft_cap")),"upholstery has rounded shoulder geometry")
			var face: Dictionary=prop.parts[0].faces[0]
			var center: Vector2=(face.points[0]+face.points[1]+face.points[2]+face.points[3])*.25+prop.position
			var body: Array[Rect2]=[Rect2(center-Vector2(1,2),Vector2(2,4))]
			prop.update_occlusion_for_units(body)
			assert(prop.fade,"actual raised faces participate in unit occlusion")
			body=[Rect2(Vector2(100000,100000),Vector2(1,1))]
			prop.update_occlusion_for_units(body)
			assert(not prop.fade,"distant units do not fade props")
			prop.free();authored+=1
		assert(FileAccess.get_sha256(source_path)==image_hash,"source map bytes remain immutable")
		var rejected=model.new();rejected.prepare(texture,board,image_name,"missing.png")
		assert(not rejected._verified,"unverifiable art falls back instead of guessing")
	assert(count==122 and authored==28)
	board.free()
	print("ENVIRONMENT_DEPTH_CHECKS_PASSED ",count," maps; ",authored," source-reviewed component models; unknown geometry kept 2D")
	quit()
