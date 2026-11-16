extends SceneTree
## Native rendering compatibility pass for every existing unit/objective/vehicle PNG.
func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	root.size = Vector2i(1280,720)
	var asset_root := ""
	var args := OS.get_cmdline_user_args()
	for i in range(args.size()-1):
		if args[i] == "--asset-root": asset_root = args[i+1]
	if asset_root.is_empty():
		push_error("--asset-root is required")
		quit(1)
		return
	var count := 0
	var layer := Node2D.new()
	root.add_child(layer)
	for filename: String in DirAccess.get_files_at(asset_root.path_join("assets/units")):
		if not filename.ends_with(".png") or filename.ends_with("_512.png"): continue
		var full := asset_root.path_join("assets/units/"+filename)
		var high := full.get_basename()+"_512.png"
		var image := Image.load_from_file(high if FileAccess.file_exists(high) else full)
		if image == null:
			push_error("Cannot load "+filename)
			quit(1)
			return
		var tok = load("res://scripts/unit_visual.gd").new()
		layer.add_child(tok)
		tok.setup({"name":filename,"hp":30,"max_hp":30,"size_scale":1},count,count%2==0,ImageTexture.create_from_image(image),Vector2(100,100))
		tok.position = Vector2(60+(count%12)*105,135+((count/12)%5)*138)
		count += 1
		if count%60 == 0:
			await process_frame
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png(asset_root.path_join("work/unit-catalog-%d.png" % (count/60)))
			for child in layer.get_children(): child.queue_free()
			await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(asset_root.path_join("work/unit-catalog-last.png"))
	print("UNIT_CATALOG_RENDERED: ",count," real sprite textures")
	layer.queue_free()
	await process_frame
	quit()
