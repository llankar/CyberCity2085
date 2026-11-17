extends SceneTree
# Rebuild the portable UI PNGs from their versioned vector sources.
func _initialize() -> void:
	var directory := ProjectSettings.globalize_path("res://../../assets/ui/squad_command/icons")
	for file in DirAccess.get_files_at(directory):
		if not file.ends_with(".svg"): continue
		var image := Image.new()
		assert(image.load_svg_from_string(FileAccess.get_file_as_string(directory.path_join(file)),3.0)==OK)
		assert(image.save_png(directory.path_join(file.get_basename()+".png"))==OK)
	quit()
