extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var catalog=load("res://scripts/environment_catalog.gd")
	assert(catalog.art_maps().size()==122)
	var count:=0
	for name: String in catalog.art_maps():
		var record: Dictionary=catalog.art_maps()[name]
		assert(record.validation.artistically_complete==false)
		var walls: Array[Dictionary]=catalog.art_walls(name)
		assert(walls.size()==record.props.filter(func(p):return bool(p.enabled)).size(),"unmatched candidates retain original art")
		for wall: Dictionary in walls:
			assert(not wall.has("cells") and not wall.has("blocks_sight"),"visual records cannot become collision/LOS data")
			var entry: Dictionary=catalog.art_annotation(name,wall)
			assert(not entry.is_empty())
			assert(FileAccess.file_exists("res://art/environment/props25/%s-%d.png"%[entry.asset,int(entry.yaw)]))
			assert(wall.outline_uv.size()==4)
		count+=1
	print("ENVIRONMENT_ART25_CHECKS_PASSED ",count)
	quit()
